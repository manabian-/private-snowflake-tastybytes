# 版による差異・矛盾

教材やリポジトリの版によって、同じはずのデータ定義・名前・配布物が違う箇所をまとめます。どちらが正しいかは決めず、両方を出典付きで残します。

## 1. 中核テーブルの定義

| 項目 | 多数派の定義 | 異なる定義 | 出典 |
| --- | --- | --- | --- |
| `country.city_population` の型 | `VARCHAR(16777216)` | `NUMBER(38,0)`（分散 PyTorch） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） / [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake/blob/4f8c4ac06f39fac0b34e918f3ae4c2c6d926fad2/scripts/setup.sql)） |
| `menu` の列順 | `truck_brand_name` は 4 列目 | `truck_brand_name` が最後（分散 PyTorch） | 同上 |
| `order_header` の列順 | `order_ts` は 10 列目 | `order_ts` が最後（分散 PyTorch） | 同上 |
| `truck_reviews.review_id` の型 | `NUMBER(18,0)`（`tb_voc` 系、翻訳テンプレート） | `NUMBER(38,0)`（`tb_101` v2） | [`tb_voc_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-customer-reviews-analytics-using-snowflake-cortex/setup/tb_voc_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-customer-reviews-analytics-using-snowflake-cortex/blob/661f0f868b8cec0789e6b01579f33fa4b484955e/setup/tb_voc_setup.sql)） / [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |
| `order_header.location_id` と `location.location_id` | `FLOAT` と `NUMBER(19,0)`（同じ SQL の中で型が違う） | `sample_orders_cli.LOCATION_ID` は `NUMBER(38,0)` | [`load_from_cli_stage.sql`](../../snowflake_contents/github/data_engineering_dbt/modern-data-engineering-snowflake/module-2/load_from_cli_stage.sql)（[原本](https://github.com/Snowflake-Labs/modern-data-engineering-snowflake/blob/824bc65c1599508a19278ff618abac39e8faa464/module-2/load_from_cli_stage.sql)） |
| `truck_build` の型 | Setup の DDL は `OBJECT` | vignette-1 の説明文は「VARIANT data type」 | [`vignette-1.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-1.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-1.sql)） |

分散 PyTorch 教材は列名を指定しない `COPY INTO` で CSV を読み込みます（CSV の列はテーブルの列順に対応付けられます）。**[推測]** 列順が違うのは、この教材の S3 バケット（`sfguide_getting_started_with_running_distributed_pytorch_models_on_snowflake/`）のファイルの列順に合わせたためと考えられます。

## 2. 同じテーブルを読み込む S3 バケット

中核 8 テーブルを読み込む S3 の場所が教材によって違います。中身が同じかどうかは、このリポジトリからは確認できません。

| バケット | 形式 | 使う教材 |
| --- | --- | --- |
| `s3://sfquickstarts/frostbyte_tastybytes/` | CSV | Zero to Snowflake（v1・FY25・v2）、Power BI、Tableau、Horizon、dbt、VS Code 拡張、価格最適化、入門ノートブック |
| `s3://sfquickstarts/tasty-bytes-builder-education/` | CSV | Northstar、Modern Data Engineering、宣言型パイプライン |
| `s3://sfquickstarts/tastybytes-voc/` | CSV | `tb_voc` 系（`menu`, `truck`, `order_header` のみ） |
| `s3://sfquickstarts/tastybytes-ece/` | CSV | カスタマーエクスペリエンスアプリ（`menu`, `truck` のみ） |
| `s3://sfquickstarts/data-engineering-with-snowpark-python/` | Parquet | Snowpark Python データエンジニアリング（最初に 2019〜2021 年の注文を読み込み、2022 年分は後の手順で読み込む） |
| `s3://sfquickstarts/sfguide_getting_started_with_running_distributed_pytorch_models_on_snowflake/` | CSV | 分散 PyTorch |
| `s3://sfquickstarts/tastybytes/` | CSV | `raw_pos/menu/` のみ（Dynamic Tables 総合ガイド、Modern DE、Snowpark Connect、入門ノートブック） |

ファイル形式の指定も違います。中核の Setup は `type = 'csv'` だけですが、価格最適化は `skip_header = 1` などを指定し、`menu/menu.csv` のようにファイル名を明示します（[`tb_po_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/sql/tb_po_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/sql/tb_po_setup.sql)））。

## 3. 中核のセットアップ SQL の版

| 版 | データベース | 追加要素 | 出典 |
| --- | --- | --- | --- |
| v1（2023-03-17） | `frostbyte_tasty_bytes` | 中核 8 テーブル＋ `orders_v` / `customer_loyalty_metrics_v` | [`tb_introduction.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/tb_introduction.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/tb_introduction.sql)） |
| FY25（v2） | `tb_101` | v1 と同じ構成（データベース名のみ変更） | [`tb_introduction.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_introduction.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_introduction.sql)） |
| Zero to Snowflake Setup（v2、2025） | `tb_101` | `raw_support.truck_reviews`、`truck_details`（`truck_build`）、`governance` / `semantic_layer` スキーマ、Cortex Search、`japan_menu_item_sales_feb_2022` | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |
| 日本語ハンズオン | `tb_101` | 中核 8 テーブル（`truck_reviews` と `truck_details` はない） | [`01_tb_introduction.sql`](../../snowflake_contents/github/common_resources/zero-to-snowflake-ja/sql/01_tb_introduction.sql)（[原本](https://github.com/Snowflake-Labs/zero-to-snowflake-ja/blob/47239042d9d7bfb882f5aaab503fe98e2ac42657/sql/01_tb_introduction.sql)） |

`raw_pos.truck_dev` は、v1 の変換教材と日本語ハンズオンでは `raw_pos.truck` から作りますが、v2 の vignette-1 では `CREATE OR REPLACE TABLE raw_pos.truck_dev CLONE raw_pos.truck_details` で作り、`truck_build` から `year`・`make`・`model` を取り出します（[`tb_zts_transformation.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/tb_zts_transformation.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/tb_zts_transformation.sql)）、[`04_tb_transformation.sql`](../../snowflake_contents/github/common_resources/zero-to-snowflake-ja/sql/04_tb_transformation.sql)（[原本](https://github.com/Snowflake-Labs/zero-to-snowflake-ja/blob/47239042d9d7bfb882f5aaab503fe98e2ac42657/sql/04_tb_transformation.sql)）、[`vignette-1.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-1.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-1.sql)））。vignette-1 の末尾にも、`raw_pos.truck` から `truck_details` を作り直す SQL があります。

## 4. Marketplace のデータベース名・リスティング名

| データ | データベース名の違い |
| --- | --- |
| Weather Source | `FROSTBYTE_WEATHERSOURCE` / `TB_WEATHERSOURCE` / `ZTS_WEATHERSOURCE` / `Pelmorex_Weather_Source_frostbyte` |
| SafeGraph | `FROSTBYTE_SAFEGRAPH` / `TB_SAFEGRAPH` / `ZTS_SAFEGRAPH` / `SAFEGRAPH_FROSTBYTE` |

気象のリスティング名は、多くの教材で「Weather Source LLC: frostbyte」、Northstar 教材では「Pelmorex Weather Source: Frostbyte」です。詳細は [Marketplace・第三者データ](marketplace-third-party-data.md) を参照してください。

SafeGraph との結合キーも、`location_id`（FY25・Snowpark 101）、`location_id` と `iso_country_code`（v2）、`placekey`（Power BI）と教材によって違います。

## 5. 「非構造化データからの洞察」教材の 2 つの版

| 項目 | GitHub リポジトリ版 | sfquickstarts 版 |
| --- | --- | --- |
| 出典 | [`sfguide-gaining-insights-from-unstructured-data-with-cortex-ai`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/tree/f5ce635e7638198d72a3211518d8c03406bba670/)） | [`gain-insights-from-unstructured-data`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/tree/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data)） |
| メディアステージ | `images`, `audio` | `images`, `audio`, `video` |
| 画像 | 車の広告・顔・事務用品などのファイル名 | `ft_01.jpeg` ～ `ft_06.jpeg` |
| 動画 | なし | `food_truck_clip_1.mp4` ～ `_4.mp4` |
| 参照テーブル | Notebook が `TO_FILE` を含む CTAS で作る | setup.sql が `*_PATH`, `UPLOAD_DATE` の空テーブルを作り、アップロード後に挿入 |
| 追加オブジェクト | — | `TRUCK_REVIEWS_V_SAMPLE`、`EXTRACTION_EVAL_DATA` |

教材 Markdown 原本（[`gain-insights-from-unstructured-data.md`](../../snowflake_contents/training/cortex_generative_ai/gain-insights-from-unstructured-data.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/gain-insights-from-unstructured-data.md)））は sfquickstarts 版の `data.zip` と `setup-post-upload.sql` を指しています。詳細は [非構造化データ](unstructured-data.md#images-audio) を参照してください。

## 6. 説明と中身が合わない箇所

| 箇所 | 説明 | 実際の定義 | 出典 |
| --- | --- | --- | --- |
| `customer_loyalty_metrics_v.visited_location_ids_array` のコメント | 「List of franchises this customer has visited」 | `ARRAY_AGG(DISTINCT oh.location_id)`（場所 ID の配列） | [`100_setup_data_model.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/100_setup_data_model.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/100_setup_data_model.sql)） |
| `harmonized.menu_item_aggregate_dt` | 名前の `_dt` | 通常のテーブル（S3 から `COPY INTO`） | [`tb_po_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/sql/tb_po_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/sql/tb_po_setup.sql)） |
| EC 商品レビューの README | 「e-commerce company (Tasty Bytes)」 | データは EC の商品（玩具・電子機器など）で、フードトラックではない | [`README.md`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/README.md)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/README.md)） |
| SSIS 移行の README | `etl/` に `update_truck_inventories.dtsx` がある | 取得したリポジトリには `daily_sales_agg.dtsx` のみ | [`README.md`](../../snowflake_contents/github/data_engineering_dbt/sfguide-scai-e2e-ssis-migration/README.md)（[原本](https://github.com/Snowflake-Labs/sfguide-scai-e2e-ssis-migration/blob/0016b567bf446369cb18ea45f4c8126e23810674/README.md)） |
| React Native の `data_app_orders_v` | — | `TIMESTAMP_NTZ_FROM_PARTS` の分の位置に `oh.second` を渡している | [`developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md`](../../snowflake_contents/training/application_development/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/developing-tasty-bytes-react-native-application-with-snowflake-sql-api/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md)） |
| `truck_build.make` | — | v2 Setup が `truck_id` が偶数の `'Ford_'` だけを `'Ford'` に置き換えるため、`'Ford'` と `'Ford_'` が混在する（vignette-1 の演習の前提） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |

## 関連ページ

- [ソースデータの全体像](source-data-overview.md)
- [中核データモデル](core-pos-model.md)
- [非構造化データ](unstructured-data.md)
- [Marketplace・第三者データ](marketplace-third-party-data.md)
