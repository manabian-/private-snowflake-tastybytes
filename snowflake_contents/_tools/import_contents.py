#!/usr/bin/env python3
"""Import the catalog without executing any downloaded source code.

Requires beautifulsoup4==4.14.3 and markdownify==1.2.2 for HTML conversion.
GitHub archives are pinned to HEAD commits and contain no nested .git directory.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from content_policy import excluded_entry, load_policy, prune_source_tree

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'catalog.json'
MANIFEST = ROOT / 'manifest.json'
HEADINGS = {
    '紹介': 'introduction', 'トレーニング': 'training', 'GitHub': 'github',
    '入門・基本機能': 'fundamentals', 'データエンジニアリング': 'data_engineering',
    'dbt': 'dbt', 'Cortex・生成 AI': 'cortex_generative_ai',
    'データサイエンス・機械学習': 'data_science_machine_learning', 'BI・分析': 'bi_analytics',
    'アプリ開発': 'application_development', 'ガバナンス・データ共有': 'governance_sharing',
    '共通教材・サンプル': 'common_resources',
    'データエンジニアリング・dbt': 'data_engineering_dbt',
    'Cortex・AI・機械学習': 'cortex_ai_machine_learning',
    'BI・アプリ・データ共有': 'bi_applications_sharing',
    '共通リポジトリ内の Tasty Bytes サンプル': 'tasty_bytes_samples',
}


def initialize():
    entries = []
    section = subsection = None
    for line in (ROOT / 'README.md').read_text().splitlines():
        if line.startswith('## '):
            section, subsection = HEADINGS[line[3:]], None
        elif line.startswith('### '):
            subsection = HEADINGS[line[4:]]
        elif line.startswith('- ['):
            for title, url in re.findall(r'\[([^]]+)\]\((https://[^)]+)\)', line):
                parsed = urllib.parse.urlsplit(url)
                segments = urllib.parse.unquote(parsed.path).strip('/').split('/')
                group = '/'.join(x for x in [section, subsection] if x)
                if parsed.hostname == 'github.com':
                    slug = segments[1] if len(segments) == 2 else segments[-1].removesuffix('.md')
                else:
                    slug = segments[-1]
                if title == '日本語':
                    title = entries[-1]['title'] + '（日本語）'
                entries.append({'title': title, 'url': url, 'category': group,
                                'path': f'{group}/{slug}',
                                'kind': 'github' if parsed.hostname == 'github.com' else 'web'})
    entries = [e for e in entries if not excluded_entry(e, load_policy(ROOT))]
    CATALOG.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n')


def fetch(url, destination):
    request = urllib.request.Request(url, headers={'User-Agent': 'SnowflakeContentArchive/1.0'})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open('wb') as out:
        shutil.copyfileobj(response, out, 1024 * 1024)
        return response.geturl()



def apply_repository_policy(record, destination, receipt):
    original_files = record.get('original_files', record.get('files'))
    original_bytes = record.get('original_bytes', record.get('bytes'))
    removed = prune_source_tree(destination, record['repository'], load_policy(ROOT))
    record['excluded_paths'] = sorted(set(record.get('excluded_paths', [])) | set(removed))
    if record['excluded_paths']:
        if original_files is not None:
            record['original_files'] = original_files
            record['original_bytes'] = original_bytes
        record['files'] = sum(p.is_file() for p in destination.rglob('*'))
        record['bytes'] = sum(p.stat().st_size for p in destination.rglob('*') if p.is_file())
    receipt.parent.mkdir(exist_ok=True)
    receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return record


def import_repository(item):
    identity, relative = item
    destination = ROOT / relative
    record = {'repository': identity, 'path': relative, 'url': f'https://github.com/{identity}'}
    receipt = ROOT / '_provenance' / (identity.split('/')[1] + '.json')
    if receipt.exists() and destination.is_dir():
        return apply_repository_policy(json.loads(receipt.read_text()), destination, receipt)
    try:
        command = subprocess.run(['git', 'ls-remote', record['url'] + '.git', 'HEAD'],
                                 text=True, capture_output=True, check=True, timeout=90)
        sha = command.stdout.split()[0]
        if not re.fullmatch('[a-f0-9]{40}', sha):
            raise ValueError('Invalid HEAD commit')
        record['commit'] = sha
        with tempfile.TemporaryDirectory(prefix='snowflake-import-') as temporary:
            temporary = Path(temporary)
            archive = temporary / 'source.tar.gz'
            fetch(f'https://codeload.github.com/{identity}/tar.gz/{sha}', archive)
            record['archive_sha256'] = hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest()
            staging = temporary / 'source'
            staging.mkdir()
            with tarfile.open(archive, 'r:gz') as tar:
                # data filter rejects traversal, escaping links and special files.
                tar.extractall(staging, filter='data')
            roots = list(staging.iterdir())
            if len(roots) != 1 or not roots[0].is_dir():
                raise ValueError('Unexpected archive layout')
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise FileExistsError(destination)
            shutil.move(str(roots[0]), destination)
        record['status'] = 'downloaded'
        record['retrieved_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record['files'] = sum(p.is_file() for p in destination.rglob('*'))
        record['bytes'] = sum(p.stat().st_size for p in destination.rglob('*') if p.is_file())
        record = apply_repository_policy(record, destination, receipt)
        print(f"OK repository {identity}: {record['files']} files, {record['bytes'] // 1048576} MiB", flush=True)
    except Exception as error:
        record.update(status='unavailable', error=str(error))
        print(f'FAILED repository {identity}: {error}', flush=True)
    return record


def render_html(html, base):
    from bs4 import BeautifulSoup
    from markdownify import markdownify
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('article') or soup.find('main') or soup.body
    if main is None:
        raise ValueError('No article/main/body content')
    for tag in main.select('script,style,nav,header,footer,noscript,button'):
        tag.decompose()
    for tag in main.find_all(['a', 'img']):
        attribute = 'href' if tag.name == 'a' else 'src'
        if tag.get(attribute):
            tag[attribute] = urllib.parse.urljoin(base, tag[attribute])
    text = markdownify(str(main), heading_style='ATX', bullets='-')
    if len(text.strip()) < 200:
        raise ValueError('Insufficient article content; page may require JavaScript/login')
    return text.strip() + '\n'


def import_web(entry):
    result = dict(entry)
    destination = ROOT / (entry['path'] + '.md')
    try:
        with tempfile.TemporaryDirectory() as temporary:
            html = Path(temporary) / 'page.html'
            final_url = fetch(entry['url'], html)
            content = render_html(html.read_text(errors='replace'), final_url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        destination.write_text(f"# {entry['title']}\n\n出典: {entry['url']}\n\n取得日時（UTC）: {timestamp}\n\n---\n\n{content}")
        result.update(status='downloaded', local_path=str(destination.relative_to(ROOT)), final_url=final_url,
                      retrieved_at=timestamp, sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    except Exception as error:
        result.update(status='unavailable', error=str(error))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--initialize', action='store_true', help='Parse original README into catalog.json once')
    parser.add_argument('--repositories-only', action='store_true')
    args = parser.parse_args()
    if args.initialize:
        if CATALOG.exists():
            raise FileExistsError(CATALOG)
        initialize()
    entries = [e for e in json.loads(CATALOG.read_text())
               if not excluded_entry(e, load_policy(ROOT))]
    repository_paths = {}
    for entry in entries:
        if entry['kind'] == 'github':
            segments = urllib.parse.urlsplit(entry['url']).path.strip('/').split('/')
            identity = '/'.join(segments[:2])
            if len(segments) == 2 and entry['category'].startswith('github/'):
                repository_paths[identity] = entry['path']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        repositories = list(pool.map(import_repository, repository_paths.items()))
    by_identity = {r['repository']: r for r in repositories}
    results = []
    for entry in entries:
        result = dict(entry)
        if entry['kind'] == 'github':
            segments = urllib.parse.unquote(urllib.parse.urlsplit(entry['url']).path).strip('/').split('/')
            repo = by_identity['/'.join(segments[:2])]
            target = ROOT / repo['path']
            if len(segments) > 2:
                target = target.joinpath(*segments[4:])
            if repo['status'] == 'downloaded' and target.exists():
                link = ROOT / entry['path']
                if link != target:
                    link.parent.mkdir(parents=True, exist_ok=True)
                    if not link.exists() and not link.is_symlink():
                        link.symlink_to(os.path.relpath(target, link.parent), target_is_directory=target.is_dir())
                result.update(status='downloaded', local_path=entry['path'], commit=repo['commit'])
            else:
                result.update(status='unavailable', error=repo.get('error', 'Path absent in repository snapshot'))
        elif args.repositories_only:
            result.update(status='pending', error='Web import not attempted in repositories-only mode')
        else:
            result = import_web(entry)
            print(f"{result['status']} web {entry['url']}", flush=True)
        results.append(result)
    MANIFEST.write_text(json.dumps({'repositories': repositories, 'contents': results}, ensure_ascii=False, indent=2) + '\n')
    print(f"Saved manifest: {len(repositories)} repositories, {len(results)} catalog entries", flush=True)


if __name__ == '__main__':
    main()
