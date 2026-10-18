# ソースデータの全体像

Tasty Bytes は Snowflake の frostbyte チームが作った架空のキッチンカー（フードトラック）ブランドで、各教材はこの共通の業務データを Snowflake に読み込んで使います（[`tasty-bytes-introduction-ja.md`](../../snowflake_contents/introduction/tasty-bytes-introduction-ja.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-introduction-ja/tasty-bytes-introduction-ja.md)））。このページでは、教材が使うソースデータを「どこから来るか」と「どんな形か」で整理し、詳細ページへの入口とします。

> **表記ルール**: 本文の事実はリンク先の SQL・Notebook・教材原本に書かれている内容です。原本に書かれていない解釈には **[推測]** と付けています。ソースは取得時点のスナップショット（`snowflake_contents/_provenance/` に記録したコミット）で、公開中の最新版とは異なる場合があります。

## 1. データの入手経路

教材のデータは、大きく次の 5 つの経路で Snowflake に入ります。

| 経路 | 内容 | 主な例 |
| --- | --- | --- |
| 公開 S3 バケット（外部ステージ） | `s3://sfquickstarts/...` を外部ステージとして作り、`COPY INTO` で読み込む | 中核の POS データ、レビュー、メール、検査レポート |
| Snowflake Marketplace（共有データベース） | 第三者のリスティングを「Get」で取得し、共有データベースとして参照する | Weather Source（気象）、SafeGraph（POI）、祝日カレンダー |
| リポジトリ同梱ファイル | GitHub リポジトリに CSV・ZIP・MP3 などが同梱されている | 価格最適化の CSV、レビュー ZIP、画像・音声 |
| 内部ステージへのアップロード・生成 | 利用者がファイルをアップロードするか、Notebook で生成して内部ステージに置く | 画像・音声ステージ、音声注文 MP3、映画レビュー TXT |
| SQL 内の `INSERT` / 生成 | セットアップ SQL が直接値を挿入する | 音声注文の元フレーズ、DCM・SSIS のサンプル |

### 1.1 公開 S3 バケット一覧（Tasty Bytes 関連）

| S3 パス | 主な読み込み先 | 形式 | 主な出典 |
| --- | --- | --- | --- |
| `s3://sfquickstarts/frostbyte_tastybytes/` | 中核 8 テーブル（`raw_pos/*`, `raw_customer/customer_loyalty`） | CSV | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |
| `s3://sfquickstarts/frostbyte_tastybytes/analytics/shift_sales/` | `raw.shift_sales` | CSV | [`tasty-bytes-snowpark-101-for-data-science.md`](../../snowflake_contents/training/data_science_machine_learning/tasty-bytes-snowpark-101-for-data-science.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-snowpark-101-for-data-science/tasty-bytes-snowpark-101-for-data-science.md)） |
| `s3://sfquickstarts/frostbyte_tastybytes/{raw_pos,raw_customer,raw_supply_chain,raw_safegraph,harmonized,analytics,excel}` | 価格最適化用の各テーブル | CSV（ヘッダー付き） | [`tb_po_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/sql/tb_po_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/sql/tb_po_setup.sql)） |
| `s3://sfquickstarts/frostbyte_tastybytes/app/orders/` | `app.orders`（非正規化済み注文） | ファイル形式指定なし | [`zero_to_app_db_setup.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-tasty-bytes-zero-to-app/database/zero_to_app_db_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-zero-to-app/blob/c6fcd92204ad7c924d6a1a0f97d8b775dc0db0b5/database/zero_to_app_db_setup.sql)） |
| `s3://sfquickstarts/frostbyte_tastybytes/app/app_orders/` | `raw.app_order_header` / `raw.app_order_detail` | CSV（`.csv.gz`） | [`developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md`](../../snowflake_contents/training/application_development/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/developing-tasty-bytes-react-native-application-with-snowflake-sql-api/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md)） |
| `s3://sfquickstarts/frostbyte_tastybytes/mlpf_quickstart/` | `tasty_byte_sales`（日別販売数） | CSV | [`ml-forecasting-ad.md`](../../snowflake_contents/training/data_science_machine_learning/ml-forecasting-ad.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/ml-forecasting-ad/ml-forecasting-ad.md)） |
| `s3://sfquickstarts/frostbyte_tastybytes/fine_tuning/` | `SUPPORT_EMAILS`（`CFT_QUICKSTART.csv`） | CSV | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-enhancing-customer-experiences-using-cortex-finetuning/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-enhancing-customer-experiences-using-cortex-finetuning/blob/3b782b2b15883d2581eb554a4d9013e93592ba2d/scripts/setup.sql)） |
| `s3://sfquickstarts/tastybytes-voc/` | `menu`, `truck`, `order_header`, `raw_support.truck_reviews` | CSV | [`tb_voc_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-customer-reviews-analytics-using-snowflake-cortex/setup/tb_voc_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-customer-reviews-analytics-using-snowflake-cortex/blob/661f0f868b8cec0789e6b01579f33fa4b484955e/setup/tb_voc_setup.sql)） |
| `s3://sfquickstarts/tastybytes-ece/` | 検査レポート抽出結果・検査画像・レビュー分析結果・メール・RAG 用文書 | CSV ほか（画像は `COPY FILES`） | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-experience-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-experience-app/setup/setup.sql)） |
| `s3://sfquickstarts/tastybytes-cx/app/` | RAG チャットボット用 `documents` / `vector_store` | CSV | [`tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md`](../../snowflake_contents/training/cortex_generative_ai/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-rag-chatbot-using-cortex-and-streamlit/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md)） |
| `s3://sfquickstarts/tasty-bytes-builder-education/` | 中核 8 テーブル（Northstar では `country` を演習 SQL、残り 7 テーブルを `load_tasty_bytes.sql` で読み込む）。宣言型パイプラインでは `order_header` / `order_detail` / `menu` のみ | CSV | [`load_tasty_bytes.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-snowflake-northstar-data-engineering/00_ingestion/load_tasty_bytes.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-snowflake-northstar-data-engineering/blob/5787837593fbec13a37338981c70648d8b2d50d2/00_ingestion/load_tasty_bytes.sql)）、[`solution_copy_into.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-snowflake-northstar-data-engineering/00_ingestion/solution/solution_copy_into.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-snowflake-northstar-data-engineering/blob/5787837593fbec13a37338981c70648d8b2d50d2/00_ingestion/solution/solution_copy_into.sql)）、[`00_setup_environment.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-declarative-pipelines-dynamic-tables/00_setup_environment.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-declarative-pipelines-dynamic-tables/blob/9937421fb54bae4a3e90ec46850e26fab862f5c0/00_setup_environment.sql)） |
| `s3://sfquickstarts/tastybytes/` | `raw_pos/menu/`（メニューのみ） | CSV | [`comprehensive-guide-to-dynamic-tables.md`](../../snowflake_contents/training/data_engineering/comprehensive-guide-to-dynamic-tables.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/comprehensive-guide-to-dynamic-tables/comprehensive-guide-to-dynamic-tables.md)） |
| `s3://sfquickstarts/data-engineering-with-snowpark-python/` | 中核 8 テーブル（年別パーティション） | Parquet（Snappy） | [`01_setup_snowflake.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-data-engineering-with-snowpark-python/steps/01_setup_snowflake.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python/blob/44c92001766275725eaa8c29d94e81562f00c03e/steps/01_setup_snowflake.sql)） |
| `s3://sfquickstarts/sfguide_getting_started_with_running_distributed_pytorch_models_on_snowflake/` | 中核 8 テーブル（列順・型が一部異なる） | CSV | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake/blob/4f8c4ac06f39fac0b34e918f3ae4c2c6d926fad2/scripts/setup.sql)） |
| `s3://sfquickstarts/misc/aisql/ecommerce_customer_review/` | `customer_data`, `product_catalog`, `product_reviews` | CSV | [`customer_reviews_insight.ipynb`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/customer_reviews_insight.ipynb)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/customer_reviews_insight.ipynb)） |

同じ「中核テーブル」でも、教材によって読み込むバケットが違います。バケットの中身が同じかどうかは、ソースからは確認できません（[版差異のページ](version-differences.md)を参照）。

## 2. データの形による分類

| 分類 | 定義（このウィキでの使い方） | 代表例 | 詳細 |
| --- | --- | --- | --- |
| 構造化 | 列と型が決まったテーブル | `raw_pos.order_header`, `raw_pos.menu`, `raw_supply_chain.*` | [中核データモデル](core-pos-model.md)、[教材固有のテーブル](tutorial-specific-tables.md) |
| 半構造化 | `VARIANT` / `OBJECT` / `ARRAY` / `VECTOR` 列に入った JSON などの入れ子データ | `menu_item_health_metrics_obj`, `truck_build`, `inspection_report_object`, `email_object` | [半構造化データ](semi-structured-data.md) |
| 非構造化 | 自由記述テキスト、画像、音声、文書ファイル | トラックレビュー本文、検査レポート画像、PDF 由来の文書、MP3/WAV | [非構造化データ](unstructured-data.md) |
| 第三者データ | Marketplace の共有データベース | Weather Source、SafeGraph、祝日 | [Marketplace・第三者データ](marketplace-third-party-data.md) |

自由記述テキスト（レビュー本文など）は `VARCHAR` 列に入っているため形式上はテーブルの一部ですが、このウィキでは内容の性質から非構造化データとして扱います。

## 3. レイヤ構成（スキーマの役割）

中核のセットアップでは、次のスキーマを作ります（[`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)））。

| スキーマ | 役割（原本の説明・コメントに基づく） | 主なオブジェクト |
| --- | --- | --- |
| `raw_pos` | POS（販売時点）の生データ | `country`, `franchise`, `location`, `menu`, `truck`, `order_header`, `order_detail`, `truck_details` |
| `raw_customer` | 顧客（ロイヤルティ会員）の生データ | `customer_loyalty` |
| `raw_support` | サポート系の生データ | `truck_reviews` |
| `harmonized` | 生データを結合・整形したビュー | `orders_v`, `customer_loyalty_metrics_v`, `truck_reviews_v` |
| `analytics` | 利用者向けに公開するビュー | `orders_v`, `customer_loyalty_metrics_v`, `truck_reviews_v` |
| `governance` | ガバナンス用オブジェクト | タグ・マスキングポリシー・行アクセスポリシー（vignette-4） |
| `semantic_layer` | 「business-friendly semantic layer」（スキーマのコメント） | `orders_v`, `customer_loyalty_metrics_v`, セマンティックモデル用ステージ |

`raw_*` → `harmonized` → `analytics` という 3 層は、ほとんどの教材で同じ名前のまま使われています。詳細は [整合・分析レイヤのビュー](harmonized-analytics-views.md) を参照してください。

## 4. データベース名の一覧

同じデータモデルが、教材ごとに別のデータベース名で作られます。

| データベース | 作成する教材（例） | 中身 |
| --- | --- | --- |
| `frostbyte_tasty_bytes` | Tasty Bytes 入門 v1、Tableau、Horizon 組織内共有 | 中核 8 テーブル（v1） |
| `tb_101` | Zero to Snowflake（FY25 / v2）、Power BI、VS Code 拡張、Cortex Analyst | 中核 8 テーブル＋`raw_support.truck_reviews` など |
| `tb_voc` | 顧客レビュー分析、非構造化データからの洞察、Hex | `menu`, `truck`, `order_header`, `truck_reviews` と `media` スキーマ |
| `tb_po_prod` | 価格最適化 | 中核＋`raw_supply_chain`, `raw_safegraph` |
| `tasty_bytes` | Northstar、Modern Data Engineering、入門ノートブック | 中核 8 テーブル |
| `tasty_bytes_dbt_db` | dbt Projects on Snowflake | 中核 8 テーブル（`raw` スキーマにまとめる） |
| `tasty_bytes_db` | Iceberg、宣言型パイプライン（Dynamic Tables） | `order_header` ほか一部 |
| `frostbyte_tasty_bytes_dev` | Snowpark 101 | `shift_sales` |
| `frostbyte_tasty_bytes_app` | React Native アプリ | アプリ用注文 |
| `tasty_bytes_enhancing_customer_experience` | カスタマーエクスペリエンスアプリ | 検査レポート・レビュー分析 |
| `tasty_bytes_customer_support_email` | サポートメールアプリ | メール・ベクトルストア |
| `tasty_bytes_chatbot` | RAG チャットボット | 文書・ベクトルストア |
| `TASTYBYTESENDTOENDML_PROD` | 分散 PyTorch | 中核 8 テーブル＋ML 特徴量 |
| `CFT_DB` | Cortex ファインチューニング | サポートメール |
| `quickstart` | ML 予測・異常検知 | 日別販売数 |
| `TASTY_AUDIO_DB` | 音声 AI パイプライン | 音声注文 |
| `TastyBytesDB`（SQL Server） | SSIS 移行 | 移行元の別スキーマ |

教材ごとの詳しい対応は [教材別データソース対応表](../tutorials/data-sources-by-tutorial.md) にまとめています。

## 関連ページ

- [ER 図（全テーブル）](er-diagram.md)
- [中核データモデル（raw_pos / raw_customer）](core-pos-model.md)
- [整合・分析レイヤのビュー](harmonized-analytics-views.md)
- [半構造化データ](semi-structured-data.md)
- [非構造化データ](unstructured-data.md)
- [教材固有のテーブル](tutorial-specific-tables.md)
- [Marketplace・第三者データ](marketplace-third-party-data.md)
- [版による差異・矛盾](version-differences.md)
