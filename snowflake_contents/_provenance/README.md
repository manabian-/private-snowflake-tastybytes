# Source snapshots

リポジトリ名の JSON ファイルは、同名の GitHub リポジトリを取得した際の記録です。

- `url` / `repository`: 元のリポジトリ
- `commit`: 取得時に解決した HEAD のコミット SHA
- `path`: `snowflake_contents/` を基準としたソース保存先
- `archive_sha256`: HTTPS で取得した、そのコミットの tar.gz アーカイブの SHA-256
- `retrieved_at`: 取得日時（UTC）
- `files` / `bytes`: 除外ルールを適用した後に保存しているソースのファイル数と合計サイズ
- `original_files` / `original_bytes`: 除外前のファイル数とサイズ（除外がある場合）
- `excluded_paths`: アーカイブ済み・旧教材として除外した、リポジトリ内の相対パス

チェックサムは取得したアーカイブの識別用です。上流が公開した署名・チェックサムを表すものではありません。各ソースのライセンスと著作権表示は、展開先にある原本を参照してください。

Web ページ・個別サンプルの取得結果、代替 Markdown の出典とチェックサムは、上位ディレクトリの `manifest.json` に記録しています。

`source_link_issues.json` は保存済みソースの参照切れシンボリックリンクの記録です。旧教材の除外後は0件です。`validation.json` は保存しているソースの件数・サイズと検証結果、`repository_archive_status.json` は GitHub のアーカイブ表示を確認した結果です。
