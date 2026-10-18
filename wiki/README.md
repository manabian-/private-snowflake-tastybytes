# Tasty Bytes ナレッジベース

Snowflake の学習用サンプル「Tasty Bytes」について、[`snowflake_contents/`](../snowflake_contents/README.md) に保存した公式ソースから知識を整理したウィキです。

## 書き方のルール

- 事実はすべて、`snowflake_contents/` 内のファイル（ローカルリンク）と、取得時のコミットに固定した原本 URL（「原本」リンク）で確認できるように書いています。
- 原本に書かれていない解釈には **[推測]** と付けています。
- 版によって内容が違う場合は、どちらかに寄せずに両方を残し、[版による差異・矛盾](data-model/version-differences.md) にまとめています。
- ソースは取得時点のスナップショットです。取得日時とコミットは [`snowflake_contents/_provenance/`](../snowflake_contents/_provenance/README.md) と [`snowflake_contents/manifest.json`](../snowflake_contents/manifest.json) に記録されています。

## データモデル

| ページ | 内容 |
| --- | --- |
| [ソースデータの全体像](data-model/source-data-overview.md) | 入手経路（S3・Marketplace・同梱ファイル・内部ステージ）、形による分類、レイヤ構成、データベース名の一覧 |
| [ER 図](data-model/er-diagram.md) | ノートブックで作る 31 テーブルの関係（POS、サプライチェーン、検査・メール・RAG、分析・アプリの 4 図）と、関係ごとの根拠 |
| [中核データモデル（raw_pos / raw_customer）](data-model/core-pos-model.md) | 中核 8 テーブルと `truck_reviews` / `truck_details` の全列・型・説明、エンティティ関係 |
| [整合・分析レイヤのビュー](data-model/harmonized-analytics-views.md) | `orders_v`、`customer_loyalty_metrics_v`、`truck_reviews_v`、`semantic_layer`、派生オブジェクト |
| [半構造化データ](data-model/semi-structured-data.md) | `VARIANT` / `OBJECT` / `ARRAY` / `VECTOR` 列の入れ子構造 |
| [非構造化データ](data-model/unstructured-data.md) | レビュー本文、メール、RAG 用文書、検査レポート画像、画像・音声・動画、音声注文 |
| [教材固有のテーブル](data-model/tutorial-specific-tables.md) | 価格最適化、Snowpark 101、アプリ、ML、データエンジニアリング、SSIS 移行など |
| [Marketplace・第三者データ](data-model/marketplace-third-party-data.md) | Weather Source、SafeGraph、祝日データ |
| [版による差異・矛盾](data-model/version-differences.md) | 型・列順・バケット・データベース名・配布物の違い |

## 教材

| ページ | 内容 |
| --- | --- |
| [教材別データソース対応表](tutorials/data-sources-by-tutorial.md) | 教材ごとのデータベース・ソースデータ・データの形 |

## ノートブック

| ファイル | 内容 |
| --- | --- |
| [`tasty_bytes_load_all_tables.ipynb`](../notebooks/tasty_bytes_load_all_tables.ipynb) | 各教材が S3 から読み込む 31 テーブルを 1 つのデータベース `tasty_bytes_all` に作成・取り込みする Snowflake Notebook。同じテーブルに複数のソースがある場合は 1 つだけを採用 |

## 主な出典リポジトリ

| リポジトリ | 主な内容 |
| --- | --- |
| [Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake](../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake) | Zero to Snowflake v2 のセットアップと vignette |
| [Snowflake-Labs/sf-samples](../snowflake_contents/github/common_resources/sf-samples) | Tasty Bytes 共通 SQL（v1・FY25）、Cortex Analyst、AISQL サンプル |
| [Snowflake-Labs/sfquickstarts](../snowflake_contents/github/common_resources/sfquickstarts) | 教材 Markdown 原本と付属ファイル |
| [Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience](../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience) | 検査レポート・メール・RAG のデータ |
| [Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit](../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit) | 価格最適化のテーブルと同梱 CSV |

すべてのリポジトリとコミットの一覧は [`snowflake_contents/README.md`](../snowflake_contents/README.md) を参照してください。
