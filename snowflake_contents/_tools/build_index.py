#!/usr/bin/env python3
"""Link downloaded sources, optionally use official guide Markdown, and build indexes."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.parse

from content_policy import excluded_entry, excluded_source, load_policy

ROOT = Path(__file__).resolve().parents[1]


def normalize(name):
    return name.lower().replace('-', '_')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-fallback', action='store_true', help='Use exact matching guide source when web is inaccessible')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    policy = load_policy(ROOT)
    manifest['contents'] = [e for e in manifest['contents'] if not excluded_entry(e, policy)]
    repositories = {r['repository']: r for r in manifest['repositories']}
    quickstarts = repositories.get('Snowflake-Labs/sfquickstarts', {})
    guide_root = ROOT / quickstarts.get('path', '_not_downloaded')
    markdowns = collections.defaultdict(list)
    if guide_root.exists():
        for file in guide_root.rglob('*.md'):
            if not excluded_source(file.relative_to(guide_root), 'Snowflake-Labs/sfquickstarts', policy):
                markdowns[normalize(file.stem)].append(file)
    for item in manifest['contents']:
        if item['kind'] != 'web' or item['status'] == 'downloaded':
            continue
        item['status'] = 'unavailable'
        item['error'] = 'HTTPS proxy denied destination (403 CONNECT); web page not downloaded'
        if not args.source_fallback or 'www.snowflake.com/' not in item['url']:
            continue
        slug = urllib.parse.urlsplit(item['url']).path.rstrip('/').split('/')[-1]
        candidates = markdowns.get(normalize(slug), [])
        if len(candidates) != 1:
            item['source_candidates'] = [str(p.relative_to(ROOT)) for p in candidates]
            continue
        source = candidates[0]
        relative = source.relative_to(guide_root).as_posix()
        source_url = f"https://github.com/Snowflake-Labs/sfquickstarts/blob/{quickstarts['commit']}/{urllib.parse.quote(relative)}"
        raw_base = f"https://raw.githubusercontent.com/Snowflake-Labs/sfquickstarts/{quickstarts['commit']}/{urllib.parse.quote(str(Path(relative).parent))}/"
        content = source.read_text()
        destination = ROOT / (item['path'] + '.md')
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Preserve code samples; resolve article links outside fenced code.
        def resolve(target):
            if re.match(r'^[a-z]+:|^#|^//', target, re.I):
                return target
            parsed = urllib.parse.urlsplit(target)
            candidate = source.parent / urllib.parse.unquote(parsed.path)
            if candidate.exists() and candidate.resolve().is_relative_to(ROOT):
                local = urllib.parse.quote(os.path.relpath(candidate, destination.parent))
                return urllib.parse.urlunsplit(('', '', local, parsed.query, parsed.fragment))
            return urllib.parse.urljoin(raw_base, target)
        def links(text):
            text = re.sub(r'(!?\[[^\]]*\]\()([^\s)]+)(\))',
                          lambda m: m[1] + resolve(m[2]) + m[3], text)
            text = re.sub(r"((?:src|href)=[\"'])([^\"']+)([\"'])",
                          lambda m: m[1] + resolve(m[2]) + m[3], text)
            return text
        chunks = re.split(r'(^[ \t]*`{3,}[^\n]*\n.*?^[ \t]*`{3,}[ \t]*$)', content,
                          flags=re.M | re.S)
        content = ''.join(chunk if i % 2 else links(chunk) for i, chunk in enumerate(chunks))
        destination.write_text(
            f"# {item['title']}\n\n対象ページ: {item['url']}\n\n"
            f"取得した原本: [{relative}]({source_url})\n\n"
            f"原本コミット: `{quickstarts['commit']}`\n\n"
            "> Web ページはネットワーク制限により取得できていません。以下は公式 GitHub の教材 Markdown 原本です。公開ページの現在の内容と一致するとは限りません。\n\n---\n\n" + content
        )
        item.update(status='source_markdown', local_path=str(destination.relative_to(ROOT)),
                    source_path=str(source.relative_to(ROOT)), source_url=source_url,
                    commit=quickstarts['commit'], retrieved_at=quickstarts['retrieved_at'],
                    sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    categories = collections.defaultdict(list)
    for item in manifest['contents']:
        categories[item['category']].append(item)
    counts = collections.Counter(e['status'] for e in manifest['contents'])
    lines = ['# Snowflake コンテンツ', '',
             'このディレクトリでは、Snowflake 社が提供している Tasty Bytes 関連コンテンツを整理します。', '',
             '## 保存形式', '',
             '- `introduction/`: 紹介・教材目次',
             '- `training/`: トレーニング教材（分野ごとの英語フォルダ）',
             '- `github/`: アーカイブ済み・旧教材を除いた GitHub ソース（分類ごとの英語フォルダ）',
             '- `import_policy.json`: Coursera・アーカイブ済み・廃止教材の除外ルール',
             f"- `catalog.json`: 対象リンク{len(manifest['contents'])}件の元データ",
             '- `manifest.json`・`_provenance/`: 出典・取得結果・コミット・チェックサム',
             '- [`_tools/`](_tools/README.md): 取得・目次生成の手順', '',
             'GitHub ソースはアーカイブ済み・旧教材を除き、`.git` や履歴を含まない通常ファイルとして保存しています。除外したソースのパスは `_provenance/` の各リポジトリの記録に残しています。重複する参照はこのディレクトリ内の相対シンボリックリンクです。原本のライセンス等は各ソース内に保持しています。', '',
             '画像・添付ファイルは取得済み原本へのローカル参照を優先し、それ以外は元の Web URL を保持します。動画・ログイン後の講座・外部データセット・Git LFS/サブモジュールの実体は含みません。教材の実行環境や Snowflake リソースは作成していません。', '',
             '## 取得状況', '',
             f"- GitHub リポジトリ: {sum(r['status'] == 'downloaded' for r in manifest['repositories'])}/{len(manifest['repositories'])} 件取得",
             f"- 対象リンク: 取得済み {counts['downloaded']} 件、公式 Markdown 原本による代替 {counts['source_markdown']} 件、未取得 {counts['unavailable']} 件", '',
             '**公式 Markdown 原本による代替**は、公開ページそのものを取得・変換したものではありません。Web ページの直接取得はネットワーク制限により未完了です。未取得項目はリンクだけを記載し、本文を取得済みとは扱いません。', '',
             '## ローカル目次', '']
    labels = {'downloaded': '取得済み', 'source_markdown': '公式 Markdown 原本（代替）', 'unavailable': '未取得'}
    for category, items in categories.items():
        folder = ROOT / category
        folder.mkdir(parents=True, exist_ok=True)
        table = ['| コンテンツ | ローカル | 出典 | 状態 |', '| --- | --- | --- | --- |']
        for item in items:
            local = '—'
            if item.get('local_path'):
                path = ROOT / item['local_path']
                target = os.path.relpath(path, folder)
                local = f"[開く]({urllib.parse.quote(target)})"
            table.append(f"| {item['title']} | {local} | [元ページ]({item['url']}) | {labels[item['status']]} |")
        (folder / 'README.md').write_text('# ' + category + '\n\n' + '\n'.join(table) + '\n')
        lines += [f'### [{category}]({category}/README.md)', '']
        for item in items:
            if item.get('local_path'):
                lines.append(f"- [{item['title']}]({urllib.parse.quote(item['local_path'])}) — {labels[item['status']]} / [出典]({item['url']})")
            else:
                lines.append(f"- {item['title']} — 未取得 / [出典]({item['url']})")
        lines.append('')
    issues = ROOT / '_provenance/source_link_issues.json'
    if issues.exists():
        count = len(json.loads(issues.read_text()))
        if count:
            lines += ['## 原本に含まれる参照切れ', '',
                      f'共通リポジトリ内の旧教材に、元のソース構成で参照先が存在しないシンボリックリンクが {count} 件あります。原本は変更せず、[_provenance/source_link_issues.json](_provenance/source_link_issues.json) に記録しています。今回作成した目次・参照リンクとは区別しています。', '']
    (ROOT / 'README.md').write_text('\n'.join(lines))
    print(json.dumps(dict(counts), ensure_ascii=False))
    for item in manifest['contents']:
        if item['status'] == 'unavailable':
            print('UNAVAILABLE', item['url'])


if __name__ == '__main__':
    main()
