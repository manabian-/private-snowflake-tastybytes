#!/usr/bin/env python3
"""snowflake_contents/ 内のファイルへの出典リンク（ローカル + 取得時コミットに固定した原本 URL）を作る。

使い方:
    python3 tools/source_link.py <snowflake_contents からの相対パス> [--from wiki/data-model] [--label 表示名]

出力例:
    [`setup.sql`](../../snowflake_contents/...)（[原本](https://github.com/.../blob/<commit>/...)）
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.parse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENTS = os.path.join(REPO_ROOT, "snowflake_contents")
ORIGIN_LINE = re.compile(r"取得した原本: \[[^\]]*\]\((https://[^)]+)\)")


def load_repositories():
    """_provenance/*.json の (保存先パス, リポジトリ, コミット) を、長いパス順で返す。"""
    repos = []
    for path in glob.glob(os.path.join(CONTENTS, "_provenance", "*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and data.get("repository") and data.get("path") and data.get("commit"):
            repos.append((data["path"].rstrip("/"), data["repository"], data["commit"]))
    repos.sort(key=lambda r: -len(r[0]))
    return repos


def original_url(rel_path, repos=None):
    """snowflake_contents からの相対パスに対応する原本 URL を返す。分からなければ None。"""
    repos = load_repositories() if repos is None else repos
    full = os.path.join(CONTENTS, rel_path)
    for base, repo, commit in repos:
        if rel_path == base or rel_path.startswith(base + "/"):
            inner = rel_path[len(base):].lstrip("/")
            kind = "tree" if os.path.isdir(full) else "blob"
            return f"https://github.com/{repo}/{kind}/{commit}/" + urllib.parse.quote(inner)
    # training/ や introduction/ の Markdown は、本文冒頭の「取得した原本」行に原本 URL がある
    if os.path.isfile(full) and rel_path.endswith(".md"):
        with open(full, encoding="utf-8") as f:
            m = ORIGIN_LINE.search(f.read(4000))
        if m:
            return m.group(1)
    return None


def source_link(rel_path, from_dir, label=None, repos=None):
    """wiki の from_dir（リポジトリルートからの相対）に置くページ用の出典リンクを返す。"""
    rel_path = rel_path.strip().strip("/")
    full = os.path.join(CONTENTS, rel_path)
    if not os.path.exists(full):
        raise FileNotFoundError(f"snowflake_contents/{rel_path} が見つかりません")
    local = urllib.parse.quote(os.path.relpath(full, os.path.join(REPO_ROOT, from_dir)))
    text = f"[`{label or os.path.basename(rel_path)}`]({local})"
    url = original_url(rel_path, repos)
    return text + (f"（[原本]({url})）" if url else "")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="+", help="snowflake_contents/ からの相対パス")
    parser.add_argument("--from", dest="from_dir", default="wiki/data-model",
                        help="リンクを書くページのディレクトリ（リポジトリルートからの相対。既定: wiki/data-model）")
    parser.add_argument("--label", help="リンクの表示名（既定: ファイル名）")
    args = parser.parse_args()
    repos = load_repositories()
    status = 0
    for p in args.path:
        try:
            print(source_link(p, args.from_dir, args.label, repos))
        except FileNotFoundError as e:
            print(f"error: {e}", file=sys.stderr)
            status = 1
    sys.exit(status)


if __name__ == "__main__":
    main()
