# Content import tools

README に列挙されたリンクを `../catalog.json` に固定し、分類別に取得します。教材のコードは実行しません。

```bash
# リポジトリのルートで実行
python -m venv /tmp/snowflake-import-venv
/tmp/snowflake-import-venv/bin/pip install -r snowflake_contents/_tools/requirements.txt
/tmp/snowflake-import-venv/bin/python snowflake_contents/_tools/import_contents.py
/tmp/snowflake-import-venv/bin/python snowflake_contents/_tools/build_index.py --source-fallback
```

- GitHub は取得時の HEAD コミットを解決し、そのコミットのアーカイブを展開します。既存の取得済みスナップショットは再利用します。
- Git の履歴・`.git` ディレクトリは取り込みません。ライセンスなどの原本は保持します。
- `../import_policy.json` に従い、Coursera、`_archived` ディレクトリ、旧教材・廃止を明記した Document AI 教材、旧 Native App 教材に対応するサンプルを除外します。取得済みソースの再利用時も除外ルールを適用します。
- 除外したパスは各リポジトリの取得記録の `excluded_paths` に記録します。`files` / `bytes` は保存しているソースの件数・サイズで、除外前の件数・サイズは `original_files` / `original_bytes` に保持します。
- Web ページは本文を Markdown 化し、相対リンク・画像 URL を元の Web サイトの絶対 URL に変換します。
- 出典、コミット、アーカイブ SHA-256、取得時刻は `../_provenance/` と `../manifest.json` に記録します。
- リポジトリのコードに依存する外部サービス、データセット、Git LFS・サブモジュールの実体、動画やログイン後の講座内容は、この取得処理の対象外です。
- 必要な接続先は `github.com`、`codeload.github.com`、`www.snowflake.com`、`docs.snowflake.com` です。TLS 検証と環境のプロキシを使用します。
- 取得できなかった項目は `manifest.json` に理由を残します。リンク一覧やエラーページを教材の本文として扱いません。

`--initialize` は初回の元 README 解析専用です。`catalog.json` が存在する場合は上書きしません。`--repositories-only` は GitHub ソースだけを取得します。

`build_index.py --source-fallback` は未取得の Snowflake ガイドについて、`sfquickstarts` 内で除外ルールに該当せずファイル名が一致する公式 Markdown を探し、代替原本であることを明示して配置します。公開ページの現状と一致するとは保証しません。目次と取得状況も再生成します。Web 取得が許可されていない環境では `import_contents.py --repositories-only` の後に実行できます。
