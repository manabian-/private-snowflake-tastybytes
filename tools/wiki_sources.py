#!/usr/bin/env python3
"""wiki が引用しているソースを記録し、ソースの変更が影響するページを見つける（AGENTS.md の Incremental Updates）。

使い方:
    python3 tools/wiki_sources.py snapshot   # wiki/_meta/sources.json を更新する
    python3 tools/wiki_sources.py diff       # 前回の snapshot からの変更と、影響するページを表示する

diff は、変更・削除されたソースとそれを引用しているページ、
catalog.json に追加・削除されたリンクを表示します。変更があれば終了コード 1 を返します。
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_link import CONTENTS, REPO_ROOT  # noqa: E402

WIKI = os.path.join(REPO_ROOT, "wiki")
SNAPSHOT = os.path.join(WIKI, "_meta", "sources.json")
CATALOG = os.path.join(CONTENTS, "catalog.json")
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)\s]*)?\)")


def files_under(directory):
    """ディレクトリ配下のファイルを並べて返す。

    git 管理下なら追跡中のファイルだけを使う（PUSH_EXCLUSIONS.md などで除外したファイルの有無で
    ローカルと CI のチェックアウトの結果が変わらないようにするため）。
    """
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--", directory], cwd=REPO_ROOT,
                             capture_output=True, check=True).stdout
        paths = [os.path.join(REPO_ROOT, p) for p in out.decode().split("\0") if p]
        paths = [p for p in paths if os.path.lexists(p)]
        if paths:
            return sorted(paths)
    except (OSError, subprocess.CalledProcessError):
        pass
    found = []
    for root, dirs, files in os.walk(directory):
        found += [os.path.join(root, name) for name in files]
    return sorted(found)


def sha256_of(path):
    """ファイルなら内容から、ディレクトリなら配下の全ファイルの相対パスとサイズからハッシュを作る。

    ディレクトリ（リポジトリ全体へのリンクなど）は数百 MB になることがあるため内容は読まない。
    そのため、サイズが変わらない内容変更はディレクトリ単位では検出できない。
    """
    h = hashlib.sha256()
    if os.path.isdir(path):
        for p in files_under(path):
            # シンボリックリンクはリンク先ではなくリンク自体の大きさを使う
            h.update(f"{os.path.relpath(p, path)}\0{os.lstat(p).st_size}\n".encode())
    else:
        with open(path, "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def cited_sources():
    """{snowflake_contents からの相対パス: [引用しているページ]} を返す。"""
    cited = {}
    for page in sorted(glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True)):
        with open(page, encoding="utf-8") as f:
            body = re.sub(r"```.*?```", "", f.read(), flags=re.S)
        for m in LINK.finditer(body):
            url = m.group(1)
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(page), urllib.parse.unquote(url)))
            if not target.startswith(CONTENTS + os.sep):
                continue
            rel = os.path.relpath(target, CONTENTS)
            pages = cited.setdefault(rel, [])
            page_rel = os.path.relpath(page, REPO_ROOT)
            if page_rel not in pages:
                pages.append(page_rel)
    return cited


def catalog_urls():
    with open(CATALOG, encoding="utf-8") as f:
        return sorted({item["url"] for item in json.load(f) if item.get("url")})


def snapshot():
    sources = {}
    for rel, pages in sorted(cited_sources().items()):
        full = os.path.join(CONTENTS, rel)
        sources[rel] = {"sha256": sha256_of(full) if os.path.exists(full) else None, "pages": pages}
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        json.dump({"sources": sources, "catalog_urls": catalog_urls()}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(sources)} sources recorded in {os.path.relpath(SNAPSHOT, REPO_ROOT)}")
    return 0


def diff():
    if not os.path.exists(SNAPSHOT):
        print("snapshot がありません。先に `python3 tools/wiki_sources.py snapshot` を実行してください。")
        return 2
    with open(SNAPSHOT, encoding="utf-8") as f:
        old = json.load(f)
    changed, deleted = [], []
    for rel, info in old["sources"].items():
        full = os.path.join(CONTENTS, rel)
        if not os.path.exists(full):
            deleted.append((rel, info["pages"]))
        elif sha256_of(full) != info["sha256"]:
            changed.append((rel, info["pages"]))
    current = cited_sources()
    uncited_new = sorted(set(current) - set(old["sources"]))
    old_urls, new_urls = set(old.get("catalog_urls", [])), set(catalog_urls())

    affected = sorted({p for _, pages in changed + deleted for p in pages})
    for title, items in (("変更されたソース", changed), ("削除されたソース", deleted)):
        if items:
            print(f"## {title}")
            for rel, pages in items:
                print(f"- snowflake_contents/{rel} → {', '.join(pages)}")
    if uncited_new:
        print("## snapshot 後に wiki から引用され始めたソース（snapshot の更新が必要）")
        for rel in uncited_new:
            print(f"- snowflake_contents/{rel}")
    for title, urls in (("catalog.json に追加されたリンク", new_urls - old_urls),
                        ("catalog.json から削除されたリンク", old_urls - new_urls)):
        if urls:
            print(f"## {title}")
            for u in sorted(urls):
                print(f"- {u}")
    if affected:
        print("## 更新が必要なページ")
        for p in affected:
            print(f"- {p}")
    if not (changed or deleted or uncited_new or new_urls != old_urls):
        print("変更はありません。")
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["snapshot", "diff"])
    args = parser.parse_args()
    sys.exit(snapshot() if args.command == "snapshot" else diff())


if __name__ == "__main__":
    main()
