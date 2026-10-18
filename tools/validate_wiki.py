#!/usr/bin/env python3
"""wiki/ を検査する（AGENTS.md の Validation）。

検査内容:
  - error: ローカルリンクのリンク切れ、ページ内アンカー（#...）の不在
  - error: 原本リンク（github.com/Snowflake-Labs/...）のコミットが _provenance と一致しない
  - warning: snowflake_contents/ への出典リンクが 1 つもないページ（目次ページを除く）
  - warning: 同じ見出し（H1）を持つページの重複

使い方:
    python3 tools/validate_wiki.py [--strict]   # --strict は warning も失敗扱いにする
"""
import argparse
import glob
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_link import REPO_ROOT, load_repositories  # noqa: E402

WIKI = os.path.join(REPO_ROOT, "wiki")
LINK = re.compile(r"\]\(([^)\s]+)\)")
GITHUB = re.compile(r"https://github\.com/([^/]+/[^/]+)/(?:blob|tree)/([0-9a-f]{40})/")
# 出典を必須としないページ（目次・索引）
INDEX_PAGES = {"README.md"}


def slugify(heading):
    """GitHub の見出しアンカーに近い規則でスラッグを作る。"""
    h = re.sub(r"<[^>]+>", "", heading).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors_of(path, cache={}):
    if path not in cache:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        ids = set(re.findall(r'<a id="([^"]+)"', text))
        ids |= {slugify(h) for h in re.findall(r"^#+ (.*)$", text, flags=re.M)}
        cache[path] = ids
    return cache[path]


def check(strict):
    errors, warnings = [], []
    commits = {repo: commit for _, repo, commit in load_repositories()}
    titles = {}
    pages = sorted(glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True))
    for page in pages:
        rel = os.path.relpath(page, REPO_ROOT)
        with open(page, encoding="utf-8") as f:
            text = f.read()
        body = re.sub(r"```.*?```", "", text, flags=re.S)  # コードブロック内は対象外

        h1 = re.search(r"^# (.+)$", text, flags=re.M)
        if h1:
            titles.setdefault(h1.group(1).strip(), []).append(rel)

        has_source = False
        for m in LINK.finditer(body):
            url = m.group(1)
            if url.startswith(("http://", "https://")):
                g = GITHUB.match(url)
                if g and g.group(1) in commits and g.group(2) != commits[g.group(1)]:
                    errors.append(f"{rel}: 原本リンクのコミットが _provenance と異なります: {url}")
                continue
            if url.startswith("mailto:"):
                continue
            path, _, anchor = url.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(page), urllib.parse.unquote(path))) if path else page
            if not os.path.exists(target):
                errors.append(f"{rel}: リンク切れ: {url}")
                continue
            if "snowflake_contents" + os.sep in target + os.sep:
                has_source = True
            if anchor and target.endswith(".md") and anchor not in anchors_of(target):
                errors.append(f"{rel}: アンカーが見つかりません: {url}")

        if not has_source and os.path.basename(page) not in INDEX_PAGES:
            warnings.append(f"{rel}: snowflake_contents/ への出典リンクがありません")

    for title, files in titles.items():
        if len(files) > 1:
            warnings.append(f"同じ見出しのページが複数あります（{title}）: {', '.join(files)}")

    for e in errors:
        print(f"error: {e}")
    for w in warnings:
        print(f"warning: {w}")
    print(f"{len(pages)} pages, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (strict and warnings) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="warning も失敗扱いにする")
    sys.exit(check(parser.parse_args().strict))


if __name__ == "__main__":
    main()
