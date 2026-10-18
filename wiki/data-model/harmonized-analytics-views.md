# 整合・分析レイヤのビュー

[中核データモデル](core-pos-model.md)の生テーブルから作られる `harmonized`（整合）・`analytics`（分析）・`semantic_layer` のビューと、教材の中で追加される派生オブジェクトをまとめます。ソースデータそのものではありませんが、多くの教材はこれらのビューを入口にデータを読むため、ソーステーブルとの対応をここで整理します。

主な出典: [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)）（v2）、[`tb_introduction.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/tb_introduction.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/tb_introduction.sql)）（v1）

## 1. `harmonized.orders_v` / `analytics.orders_v`

注文明細 1 行を 1 行とし、注文・トラック・メニュー・フランチャイズ・場所・顧客の属性を横に並べたビューです。

| 列 | 元の列 |
| --- | --- |
| `order_id`, `truck_id`, `order_ts` | `order_header` |
| `order_detail_id`, `line_number` | `order_detail` |
| `truck_brand_name`, `menu_type` | `menu` |
| `primary_city`, `region`, `country`, `franchise_flag`, `franchise_id` | `truck` |
| `franchisee_first_name`, `franchisee_last_name` | `franchise.first_name`, `franchise.last_name` |
| `location_id` | `location` |
| `customer_id`, `first_name`, `last_name`, `e_mail`, `phone_number`, `children_count`, `gender`, `marital_status` | `customer_loyalty`（左外部結合） |
| `menu_item_id`, `quantity`, `unit_price`, `price` | `order_detail` |
| `menu_item_name` | `menu` |
| `order_amount`, `order_tax_amount`, `order_discount_amount`, `order_total` | `order_header` |

結合条件:

```sql
FROM raw_pos.order_detail od
JOIN raw_pos.order_header oh ON od.order_id = oh.order_id
JOIN raw_pos.truck t         ON oh.truck_id = t.truck_id
JOIN raw_pos.menu m          ON od.menu_item_id = m.menu_item_id
JOIN raw_pos.franchise f     ON t.franchise_id = f.franchise_id
JOIN raw_pos.location l      ON oh.location_id = l.location_id
LEFT JOIN raw_customer.customer_loyalty cl ON oh.customer_id = cl.customer_id
```

`analytics.orders_v` は `SELECT DATE(o.order_ts) AS date, * FROM harmonized.orders_v o` で、先頭に `date` 列を加えただけのビューです（コメント: 「Tasty Bytes Order Detail View」）。

`order_total` などヘッダーの金額は明細の行数だけ繰り返されます。**[推測]** 明細単位の売上を集計するときは `price` を使う設計で、気象との結合ビュー（`daily_city_metrics_v`、`daily_sales_by_weather_v`）も `SUM(price)` を使っています。

### バリエーション

| 教材 | 違い | 出典 |
| --- | --- | --- |
| Horizon 組織内共有 | `analytics.orders_v` を `SECURE VIEW` で作る。アプリ共有用に `frostbyte_tasty_bytes_app.harmonized.orders_v` を CTAS の**テーブル**として複製（SQL コメントに件数「693M」） | [`100_setup_data_model.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/100_setup_data_model.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/100_setup_data_model.sql)） |
| Data App（Zero to App）・SPCS | 同じ 32 列を持つ非正規化テーブル `app.orders` を S3 から直接読み込む（ビューではない） | [`zero_to_app_db_setup.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-tasty-bytes-zero-to-app/database/zero_to_app_db_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-zero-to-app/blob/c6fcd92204ad7c924d6a1a0f97d8b775dc0db0b5/database/zero_to_app_db_setup.sql)） |
| Snowpark Python データエンジニアリング | Snowpark で結合した `POS_FLATTENED_V` を作り、ストリームを張る | [`04_create_pos_view.py`](../../snowflake_contents/github/data_engineering_dbt/sfguide-data-engineering-with-snowpark-python/steps/04_create_pos_view.py)（[原本](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python/blob/44c92001766275725eaa8c29d94e81562f00c03e/steps/04_create_pos_view.py)） |
| dbt Projects on Snowflake | staging モデル（`raw_pos_*.sql`）と marts モデル `orders.sql` で同等の結合を表現 | [`orders.sql`](../../snowflake_contents/github/data_engineering_dbt/getting-started-with-dbt-on-snowflake/tasty_bytes_dbt_demo/models/marts/orders.sql)（[原本](https://github.com/Snowflake-Labs/getting-started-with-dbt-on-snowflake/blob/ce9dfd8fc6c9d0fb4c46d3df16503efe210ae249/tasty_bytes_dbt_demo/models/marts/orders.sql)） |

<a id="customer-loyalty-metrics"></a>

## 2. `harmonized.customer_loyalty_metrics_v` / `analytics.customer_loyalty_metrics_v`

ロイヤルティ会員ごとの売上合計と訪問場所の配列です。

```sql
SELECT cl.customer_id, cl.city, cl.country, cl.first_name, cl.last_name,
       cl.phone_number, cl.e_mail,
       SUM(oh.order_total) AS total_sales,
       ARRAY_AGG(DISTINCT oh.location_id) AS visited_location_ids_array
FROM raw_customer.customer_loyalty cl
JOIN raw_pos.order_header oh ON cl.customer_id = oh.customer_id
GROUP BY ...
```

`visited_location_ids_array` は `ARRAY` 型の半構造化列です。Horizon 組織内共有版はこのビューの各列に説明コメントを付けており、`VISITED_LOCATION_IDS_ARRAY` を「List of franchises this customer has visited」と説明しています（[`100_setup_data_model.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/100_setup_data_model.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/100_setup_data_model.sql)））。ただし中身は `order_header.location_id` の配列です。

<a id="truck-reviews-v"></a>

## 3. `harmonized.truck_reviews_v` / `analytics.truck_reviews_v`

レビュー（非構造化テキスト）に注文・トラック・ブランドの属性を付けたビューで、v2 Setup と `tb_voc` 系の教材で同じ定義です。

| 列 | 元 |
| --- | --- |
| `review_id`, `order_id`, `language`, `source`, `review` | `raw_support.truck_reviews` |
| `truck_id`, `customer_id` | `order_header` |
| `date` | `TO_DATE(order_header.order_ts)` |
| `primary_city` | `truck` |
| `truck_brand_name` | `menu`（`menu_type_id` で結合） |

v2 Setup は、このビューを元に Cortex Search サービス `harmonized.tasty_bytes_review_search` を作ります（`ON REVIEW`、属性は `LANGUAGE, ORDER_ID, REVIEW_ID, TRUCK_BRAND_NAME, PRIMARY_CITY, DATE, SOURCE`、`TARGET_LAG = '1 hour'`）。レビュー本文の詳細は [非構造化データ](unstructured-data.md#truck-reviews) を参照してください。

## 4. `semantic_layer` のビュー（v2）

Cortex Analyst 用に、ID を `VARCHAR` に変換したビューを作ります。

| ビュー | 内容 |
| --- | --- |
| `semantic_layer.orders_v` | `harmonized.orders_v` から主要列を選び、`*_id` を `VARCHAR` に変換し、`DATE(order_ts) AS order_date` を追加。`customer_id IS NOT NULL AND primary_city IS NOT NULL` で絞り込む |
| `semantic_layer.customer_loyalty_metrics_v` | `customer_id`, `city`, `country`, `total_sales`, `visited_location_ids_array`（`location_id` を `VARCHAR` にした配列） |

これに対応するセマンティックモデルは [`TASTY_BYTES_BUSINESS_ANALYTICS.yaml`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/semantic_models/TASTY_BYTES_BUSINESS_ANALYTICS.yaml)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/semantic_models/TASTY_BYTES_BUSINESS_ANALYTICS.yaml)） で、`ORDERS_V` と `CUSTOMER_LOYALTY_METRICS_V` を `CUSTOMER_ID` で関連付けています。

別の Cortex Analyst サンプル（[`sales_detail_semantic_model.yaml`](../../snowflake_contents/github/common_resources/sf-samples/samples/cortex-analyst/Cortex%20Analyst%20Tasty%20Bytes/sales_detail_semantic_model.yaml)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/cortex-analyst/Cortex%20Analyst%20Tasty%20Bytes/sales_detail_semantic_model.yaml)））は `TB_101.ANALYTICS.ORDERS_V` を直接参照し、次元 24 個・時間次元 2 個（`DATE`, `ORDER_TS`）・メジャー 3 個（`QUANTITY`, `UNIT_PRICE`, `PRICE`）を定義しています。

## 5. その他の派生オブジェクト

| オブジェクト | 種類 | 元データ | 出典 |
| --- | --- | --- | --- |
| `analytics.japan_menu_item_sales_feb_2022` | ビュー | `analytics.orders_v`（`country = 'Japan'`、2022 年 2 月） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |
| `harmonized.menu_v` / `analytics.menu_v` | ビュー | `raw_pos.menu` の `menu_item_health_metrics_obj` を `FLATTEN` | [`tb_semi_structured_data.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_semi_structured_data.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_semi_structured_data.sql)） |
| `raw_pos.menu_staging` | テーブル | `s3://sfquickstarts/frostbyte_tastybytes/raw_pos/menu/` を再読み込み | [`vignette-2.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-2.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-2.sql)） |
| `harmonized.ingredient`, `ingredient_to_menu_lookup`, `ingredient_usage_by_truck` | Dynamic Table | `menu_staging` の材料配列を展開 | [`vignette-2.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-2.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-2.sql)） |
| `raw_pos.truck_dev` | テーブル（クローン） | `raw_pos.truck` / `truck_details` | [`vignette-1.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-1.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-1.sql)） |
| `harmonized.daily_weather_v` | ビュー | Weather Source `history_day` × `postal_codes` × `raw_pos.country` | [`tb_collaboration.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_collaboration.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_collaboration.sql)） |
| `analytics.daily_city_metrics_v` | ビュー | `daily_weather_v` を `orders_v` と日付・都市・国で左外部結合 | [`tb_collaboration.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_collaboration.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_collaboration.sql)） |
| `analytics.daily_sales_by_weather_v` | ビュー | `daily_weather_v` と `orders_v` の日別集計 | [`vignette-5.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-5.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-5.sql)） |
| `harmonized.tastybytes_poi_v` | ビュー | `raw_pos.location` × SafeGraph（`location_id` と `iso_country_code`） | [`vignette-5.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-5.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-5.sql)） |
| `analytics.daily_city_metrics`（Dynamic Table） | Dynamic Table | 気象と注文 | [`200_setup_data_products.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/200_setup_data_products.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/200_setup_data_products.sql)） |
| `dt_dim_*`, `dt_fact_*` | Dynamic Table（スタースキーマ） | `tb_101` の生テーブル（SafeGraph のコピー `raw_pos.safegraph_frostbyte_location` も作るが、`dim_location` での結合はコメントアウトされている） | [`end-to-end-analytics-with-snowflake-and-power-bi.md`](../../snowflake_contents/training/bi_analytics/end-to-end-analytics-with-snowflake-and-power-bi.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/end-to-end-analytics-with-snowflake-and-power-bi/end-to-end-analytics-with-snowflake-and-power-bi.md)） |
| `orders_enriched` → `order_fact` → `daily_business_metrics` ほか | Dynamic Table（3 層） | `tasty_bytes_db.raw` の `order_header` / `order_detail` / `menu` | [`01_dynamic_tables.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-declarative-pipelines-dynamic-tables/01_dynamic_tables.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-declarative-pipelines-dynamic-tables/blob/9937421fb54bae4a3e90ec46850e26fab862f5c0/01_dynamic_tables.sql)） |

気象・POI のビューが参照する共有データベースの名前は教材ごとに違います（[Marketplace・第三者データ](marketplace-third-party-data.md)）。

## 関連ページ

- [中核データモデル](core-pos-model.md)
- [半構造化データ](semi-structured-data.md)
- [Marketplace・第三者データ](marketplace-third-party-data.md)
- [教材別データソース対応表](../tutorials/data-sources-by-tutorial.md)
