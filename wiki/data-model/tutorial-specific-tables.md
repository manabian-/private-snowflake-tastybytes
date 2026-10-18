# 教材固有のテーブル（構造化データ）

[中核データモデル](core-pos-model.md)以外で、特定の教材だけが読み込む・作る構造化データをまとめます。非構造化データ（レビュー・メール・文書・画像・音声）は [非構造化データ](unstructured-data.md) に、JSON などの入れ子構造は [半構造化データ](semi-structured-data.md) にあります。

> 「同梱 CSV の行数」は、リポジトリに入っている CSV を Python の `csv` モジュールで数え、ヘッダー 1 行を引いた値です。教材のセットアップは S3 から読み込むため、S3 上のファイルが同梱 CSV と同じとは限りません。

<a id="price-optimization"></a>

## 1. 価格最適化（`tb_po_prod`）

出典: [`tb_po_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/sql/tb_po_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/sql/tb_po_setup.sql)）、同梱 CSV: [`csv`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/csv)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/tree/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/csv)）

中核 8 テーブル（`raw_pos.*`, `raw_customer.customer_loyalty`、列は中核と同じ）に加え、サプライチェーン・POI・事前集計のテーブルを読み込みます。ファイル形式は `skip_header = 1`、`field_optionally_enclosed_by = '"'` です。

### `raw_supply_chain`（`s3://sfquickstarts/frostbyte_tastybytes/raw_supply_chain`）

| テーブル | 列（型） | 同梱 CSV の行数 |
| --- | --- | --- |
| `item` | `ITEM_ID NUMBER(38,0)`, `NAME`, `CATEGORY`, `UNIT`, `UNIT_PRICE NUMBER(38,9)`, `UNIT_CURRENCY`, `SHELF_LIFE_DAYS NUMBER(38,0)`, `VENDOR_ID NUMBER(38,0)`, `IMAGE_URL` | 89 |
| `recipe` | `RECIPE_ID`, `MENU_ITEM_ID`, `MENU_ITEM_LINE_ITEM`, `ITEM_ID`（いずれも `NUMBER(38,0)`）, `UNIT_QUANTITY NUMBER(38,9)` | 274 |
| `item_prices` | `ITEM_ID NUMBER(38,0)`, `UNIT_PRICE NUMBER(38,2)`, `START_DATE DATE`, `END_DATE DATE` | 801 |
| `price_elasticity` | `PE_ID NUMBER(11,0)`, `MENU_ITEM_ID NUMBER(38,0)`, `PRICE NUMBER(38,2)`, `CURRENCY VARCHAR(3)`, `FROM_DATE DATE`, `THROUGH_DATE DATE`, `DAY_OF_WEEK NUMBER(2,0)` | 113,667 |
| `menu_prices` | `MENU_ITEM_ID NUMBER(38,0)`, `SALES_PRICE_USD NUMBER(38,2)`, `START_DATE DATE`, `END_DATE DATE` | 900 |

同梱 CSV の先頭データ行の例: `item` は `1,Bottled Water,Beverage,36 Count Pack,4.280000000,USD,365,1,`、`recipe` は `1,14,1,1,0.031250000`。**[推測]** `recipe` はメニュー品目（`MENU_ITEM_ID`）と食材（`ITEM_ID`）の対応と使用量で、`item_prices` / `menu_prices` は期間ごとの食材単価・販売価格です。

### `raw_safegraph.core_poi_geometry`（`s3://sfquickstarts/frostbyte_tastybytes/raw_safegraph`）

SafeGraph 形式の POI（地点）データで、30 列あります。主な列は `PLACEKEY`, `LOCATION_NAME`, `TOP_CATEGORY`, `SUB_CATEGORY`, `NAICS_CODE`, `LATITUDE`, `LONGITUDE`, `CITY`, `REGION`, `POSTAL_CODE`, `OPEN_HOURS VARIANT`, `POLYGON_WKT`, `ISO_COUNTRY_CODE`, `WKT_AREA_SQ_METERS`, `COUNTRY` です。同梱 CSV は 15,000 行で、先頭データ行は Munich の `Ostpark Munchen` です。Marketplace の SafeGraph とは別に、教材が S3 から読み込むコピーです（[Marketplace・第三者データ](marketplace-third-party-data.md)）。

### 事前集計テーブルと分析ビュー

| オブジェクト | 種類 | 内容 | 同梱 CSV の行数 |
| --- | --- | --- | --- |
| `harmonized.menu_item_aggregate_dt` | **テーブル**（S3 から `COPY INTO`） | 日付・曜日・ブランド・品目ごとの `SALE_PRICE`, `BASE_PRICE`, `COST_OF_GOODS_USD`, `COUNT_ORDERS`, `TOTAL_QUANTITY_SOLD`, `COMPETITOR_PRICE` | 303,782 |
| `harmonized.menu_item_cogs_and_price_v` | ビュー | 品目ごとの期間別原価・販売価格 | 800（同名 CSV） |
| `harmonized.order_item_cost_v` | ビュー | 注文明細の原価 | — |
| `analytics.menu_item_aggregate_v` | ビュー | `menu_item_aggregate_dt` を公開 | 303,782（同名 CSV） |
| `analytics.order_item_cost_agg_v` | ビュー | 年月・品目ごとの平均売上・原価・利益と前期の値（列名は `AVG_REVENUE_WO_ITEM`, `PREV_AVG_PROFIT_WO_ITEM` など） | 9,036（同名 CSV） |

名前の末尾は `_dt` ですが、`menu_item_aggregate_dt` は Dynamic Table ではなく通常のテーブルとして作られます。同梱の `csv/analytics/` と `csv/harmonized/` にはビューと同名の CSV があります。**[推測]** これらはビューの結果を書き出したもので、ビューの定義を理解する参考になります。

Notebook（[`0_start_here.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/notebooks/0_start_here.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/notebooks/0_start_here.ipynb)））は、さらに `demand_est_input_train` / `_test` / `_full`（`save_as_table`）、`analytics.pricing`、`pricing_detail`、`pricing_final`（`CREATE OR REPLACE TABLE`）などを作ります。

## 2. Snowpark 101 for Data Science（`frostbyte_tasty_bytes_dev`）

出典: [`tasty-bytes-snowpark-101-for-data-science.md`](../../snowflake_contents/training/data_science_machine_learning/tasty-bytes-snowpark-101-for-data-science.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-snowpark-101-for-data-science/tasty-bytes-snowpark-101-for-data-science.md)）

| オブジェクト | 内容 |
| --- | --- |
| `raw.shift_sales` | `location_id NUMBER(19,0)`, `city`, `date DATE`, `shift_sales FLOAT`, `shift VARCHAR(2)`, `month NUMBER(2,0)`, `day_of_week NUMBER(2,0)`, `city_population NUMBER(38,0)`。`@s3load/analytics/shift_sales/` から読み込む |
| `harmonized.shift_sales` | `raw.shift_sales` に SafeGraph の `latitude`, `longitude`, `location_name` を `location_id` で結合した CTAS |
| `analytics.shift_sales_v` | `harmonized.shift_sales` を公開するビュー。Notebook の入力 |

教材原本は「each truck having the ability to choose two different selling locations per day」と説明しています。シフト単位の売上から、最も売上が見込める場所を予測するモデルを作ります。

Sigma のパートナー教材も、Seattle のシフト売上 CSV（`SHIFT_SALES.csv`、Sigma が配布）をアップロードして使います（[`partner-snowflake-predictive-model-using-sigma.md`](../../snowflake_contents/training/bi_analytics/partner-snowflake-predictive-model-using-sigma.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/partner-snowflake-predictive-model-using-sigma/partner-snowflake-predictive-model-using-sigma.md)））。

## 3. アプリ用の注文データ

| 教材 | オブジェクト | 内容 | 出典 |
| --- | --- | --- | --- |
| Build a Data App（Zero to App）、SPCS 版 | `frostbyte_tasty_bytes.app.orders` | `harmonized.orders_v` と同じ 32 列の非正規化テーブル。`s3://sfquickstarts/frostbyte_tastybytes/app/orders/` から読み込む | [`zero_to_app_db_setup.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-tasty-bytes-zero-to-app/database/zero_to_app_db_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-zero-to-app/blob/c6fcd92204ad7c924d6a1a0f97d8b775dc0db0b5/database/zero_to_app_db_setup.sql)） |
| 同上 | `app.users` | `user_id`, `user_name`, `hashed_password`, `franchise_id`, `password_date`, `status`（フランチャイズのログイン用） | [`build-a-data-app-with-snowflake.md`](../../snowflake_contents/training/application_development/build-a-data-app-with-snowflake.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/build-a-data-app-with-snowflake/build-a-data-app-with-snowflake.md)） |
| React Native アプリ | `raw.app_order_header` | `order_id`, `month`, `day`, `hour`, `minute`, `second`, `order_total NUMBER(19,3)`, `order_tax_amount NUMBER(2,0)`, `first_name`, `last_name`, `gender`, `order_status` | [`developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md`](../../snowflake_contents/training/application_development/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/developing-tasty-bytes-react-native-application-with-snowflake-sql-api/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md)） |
| 同上 | `raw.app_order_detail` | `order_id`, `order_detail_id`, `menu_item_name`, `quantity NUMBER(2,0)`, `unit_price NUMBER(19,3)` | 同上 |
| 同上 | `harmonized.data_app_orders_v` | 年を `YEAR(CURRENT_DATE())` とし、`TIMESTAMP_NTZ_FROM_PARTS(..., oh.month, oh.day, oh.hour, oh.second, 0)` で `order_ts` を組み立てる | 同上 |

`data_app_orders_v` の `TIMESTAMP_NTZ_FROM_PARTS` は、分の位置に `oh.second`、秒の位置に `0` を渡しています（原本どおり）。

## 4. 機械学習教材

| 教材 | オブジェクト | 内容 | 出典 |
| --- | --- | --- | --- |
| ML 予測・異常検知 | `quickstart.ml_functions.tasty_byte_sales` | `DATE`, `PRIMARY_CITY`, `MENU_ITEM_NAME`, `TOTAL_SOLD NUMBER(17,0)`。`s3://sfquickstarts/frostbyte_tastybytes/mlpf_quickstart/ml_functions_quickstart.csv` から読み込む | [`ml-forecasting-ad.md`](../../snowflake_contents/training/data_science_machine_learning/ml-forecasting-ad.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/ml-forecasting-ad/ml-forecasting-ad.md)） |
| 同上 | `vancouver_sales`, `lobster_sales`, `canadian_holidays` ほか | 上のテーブルと祝日データから作る学習用テーブル・ビュー | 同上 |
| 分散 PyTorch | `ML.CUSTOMER_FEATURES` | `customer_loyalty` から `CUSTOMER_ID`, `CITY`, `COUNTRY`, `GENDER`, `MARITAL_STATUS`, `BIRTHDAY_DATE`, `AGE` | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake/blob/4f8c4ac06f39fac0b34e918f3ae4c2c6d926fad2/scripts/setup.sql)） |
| 同上 | `ML.MENU_ITEM_FEATURES` | `menu` から `MENU_TYPE`, `TRUCK_BRAND_NAME`, `MENU_ITEM_NAME`, `ITEM_CATEGORY`, `ITEM_SUBCATEGORY`, `SALE_PRICE_USD` | 同上 |
| VS Code 拡張（リモート開発） | `tb_101.ml.daily_sales`, `daily_sales_weather` | Notebook が中核テーブルと Weather Source（`frostbyte_weathersource`）から `CREATE OR REPLACE TABLE` で作る学習データ | [`forecast.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-getting-started-with-remote-development-vscode-extension/forecast.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-with-remote-development-vscode-extension/blob/1f509be4b9387757776a629da32c2fd3bb49ed9e/forecast.ipynb)） |

## 5. データエンジニアリング教材

| 教材 | オブジェクト | 内容 | 出典 |
| --- | --- | --- | --- |
| Modern Data Engineering | `load_data.public.sample_menu_copy_into` | `menu` と同じ 11 列。`s3://sfquickstarts/tastybytes/raw_pos/menu/` から読み込む | [`module_2_batch_data_ingestion.ipynb`](../../snowflake_contents/github/data_engineering_dbt/modern-data-engineering-snowflake/module-2/module_2_batch_data_ingestion.ipynb)（[原本](https://github.com/Snowflake-Labs/modern-data-engineering-snowflake/blob/824bc65c1599508a19278ff618abac39e8faa464/module-2/module_2_batch_data_ingestion.ipynb)） |
| 同上 | `load_data.public.sample_orders_cli` | `order_header` と同じ 16 列（`LOCATION_ID` は `NUMBER(38,0)`）。同梱の `sample_orders.csv` を Snowflake CLI のステージから読み込む | [`load_from_cli_stage.sql`](../../snowflake_contents/github/data_engineering_dbt/modern-data-engineering-snowflake/module-2/load_from_cli_stage.sql)（[原本](https://github.com/Snowflake-Labs/modern-data-engineering-snowflake/blob/824bc65c1599508a19278ff618abac39e8faa464/module-2/load_from_cli_stage.sql)） |
| 同上 | `tasty_bytes.raw_pos.daily_sales_hamburg`（Dynamic Table）、`harmonized.weather_hamburg_t` など | Hamburg の売上と気象 | [`module_3_data_transformations.ipynb`](../../snowflake_contents/github/data_engineering_dbt/modern-data-engineering-snowflake/module-3/module_3_data_transformations.ipynb)（[原本](https://github.com/Snowflake-Labs/modern-data-engineering-snowflake/blob/824bc65c1599508a19278ff618abac39e8faa464/module-3/module_3_data_transformations.ipynb)）、[`module_5_orchestrating_pipelines.ipynb`](../../snowflake_contents/github/data_engineering_dbt/modern-data-engineering-snowflake/module-5/module_5_orchestrating_pipelines.ipynb)（[原本](https://github.com/Snowflake-Labs/modern-data-engineering-snowflake/blob/824bc65c1599508a19278ff618abac39e8faa464/module-5/module_5_orchestrating_pipelines.ipynb)） |
| Dynamic Tables 総合ガイド | `menu_raw` | `menu` と同じ 11 列。`s3://sfquickstarts/tastybytes/raw_pos/menu/` から読み込む。原本は「100 menu items across 4 item categories」が読み込まれると説明 | [`comprehensive-guide-to-dynamic-tables.md`](../../snowflake_contents/training/data_engineering/comprehensive-guide-to-dynamic-tables.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/comprehensive-guide-to-dynamic-tables/comprehensive-guide-to-dynamic-tables.md)） |
| 同上 | `order_events` | `order_id`, `menu_item_id`, `quantity`, `event_ts`。`INSERT` で 2 件のイベントを作る | 同上 |
| DCM Projects（フルデモ） | `RAW.MENU`, `RAW.TRUCK`, `RAW.CUSTOMER`, `RAW.ORDER_HEADER`, `RAW.ORDER_DETAIL`, `RAW.DAILY_ORDERS_INCOMING`, `RAW.INVENTORY`, `RAW.ALL_ITEMS`, `RAW.ALL_REGIONS` | 中核より列を絞った独自定義（例: `MENU` は 5 列、`TRUCK` は `TRUCK_ID`, `TRUCK_BRAND_NAME`, `MENU_TYPE`）。内部ステージ `TASTY_BYTES_ORDERS_STAGE` の CSV を取り込むタスクがある | [`raw.sql`](../../snowflake_contents/github/data_engineering_dbt/snowflake-dcm-projects/sample-projects/dcm-full-demo-project/sources/definitions/raw.sql)（[原本](https://github.com/Snowflake-Labs/snowflake-dcm-projects/blob/92ca6a42b2aec4c7bc7405664b7a16ec349baab4/sample-projects/dcm-full-demo-project/sources/definitions/raw.sql)）、[`ingest.sql`](../../snowflake_contents/github/data_engineering_dbt/snowflake-dcm-projects/sample-projects/dcm-full-demo-project/sources/definitions/ingest.sql)（[原本](https://github.com/Snowflake-Labs/snowflake-dcm-projects/blob/92ca6a42b2aec4c7bc7405664b7a16ec349baab4/sample-projects/dcm-full-demo-project/sources/definitions/ingest.sql)） |

## 6. SSIS 移行（SQL Server の `TastyBytesDB`）

出典: [`00_ddl.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-scai-e2e-ssis-migration/source_db/00_ddl.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-scai-e2e-ssis-migration/blob/0016b567bf446369cb18ea45f4c8126e23810674/source_db/00_ddl.sql)）、[`README.md`](../../snowflake_contents/github/data_engineering_dbt/sfguide-scai-e2e-ssis-migration/README.md)（[原本](https://github.com/Snowflake-Labs/sfguide-scai-e2e-ssis-migration/blob/0016b567bf446369cb18ea45f4c8126e23810674/README.md)）

SnowConvert AI による移行の題材として作られた、**Snowflake の中核モデルとは別設計**の SQL Server データベースです。README は「localized menus, customer loyalty, order management, inventory tracking, and employee scheduling」を扱い、移行時の警告（EWI）が出るように T-SQL 固有の構文（計算列、`ROWVERSION`、`MONEY`、`NTEXT`、`UNIQUEIDENTIFIER` など）を意図的に使っていると説明しています。

| テーブル（`TastyBytes` スキーマ） | 主な列 |
| --- | --- |
| `Country` | `CountryID`, `CountryName`, `CountryCode CHAR(3)`, `CurrencyCode CHAR(3)`, `TaxRate`, `DisplayName`（計算列）, `IsActive` |
| `City` | `CityID`, `CityName`, `CountryID`, `StateProvince`, `Latitude`, `Longitude`, `PopulationSize` |
| `FoodTruck` | `TruckID`, `TruckGUID`（`ROWGUIDCOL`）, `TruckName`, `LicensePlate`, `CityID`, `TruckConfig NVARCHAR(MAX)`, `YearPurchased`, `MaxCapacity`, `IsOperational` |
| `Menu` | `MenuID`, `MenuName`, `TruckID`, `CuisineType`, `MenuDescription NTEXT`, `BasePriceTier MONEY`, `IsSeasonalMenu`, `EffectiveFrom`, `EffectiveTo` |
| `MenuItem` | `MenuItemID`, `MenuID`, `ItemName`, `ItemDescription`, `BasePrice MONEY`, `CalorieCount`, `IsVegetarian`, `IsGlutenFree`, `IsSpicy`, `PriceWithTax`（計算列）, `RowVer ROWVERSION` |
| `Customer` | `CustomerID`, `CustomerGUID`, `FirstName`, `LastName`, `Email`, `PhoneNumber`, `PreferredCityID`, `LoyaltyPoints`, `MemberSince`, `IsActive` |
| `OrderHeader` | `OrderID`, `CustomerID`, `TruckID`, `OrderDate`, `CompletedAt`, `OrderStatus`, `TotalAmount MONEY`, `TipAmount`, `PaymentMethod`, `OrderNotes` |
| `OrderDetail` | `OrderID`, `LineNumber`, `MenuItemID`, `Quantity`, `UnitPrice SMALLMONEY`, `Discount`, `LineTotal`（計算列）, `SpecialRequests` |
| `Inventory` | `InventoryID`, `TruckID`, `IngredientName`, `QuantityOnHand`, `UnitOfMeasure`, `ReorderLevel`, `SupplierNotes`（`SPARSE`） |
| `EmployeeShift` | `ShiftID`, `EmployeeName`, `TruckID`, `ShiftDate`, `StartTime`, `EndTime`, `HoursWorked`（計算列）, `Role`, `HourlyRate` |

このほかに `etl_results.etl_logs`、ビュー `vw_TopSellingItems`、関数 `fn_FormatCustomerName`、プロシージャ `sp_UpdateInventory` があります。サンプルデータは [`01_data.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-scai-e2e-ssis-migration/source_db/01_data.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-scai-e2e-ssis-migration/blob/0016b567bf446369cb18ea45f4c8126e23810674/source_db/01_data.sql)） の `INSERT` 文です。

README は SSIS パッケージとして `daily_sales_agg.dtsx` と `update_truck_inventories.dtsx` を挙げていますが、取得したリポジトリの `etl/` には `daily_sales_agg.dtsx` だけがあります。

## 7. その他の小さなテーブル

| 教材 | オブジェクト | 内容 | 出典 |
| --- | --- | --- | --- |
| Zero to Snowflake v2（ガバナンス） | `governance.row_policy_map` | 行アクセスポリシー用の対応表 | [`vignette-4.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-4.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-4.sql)） |
| Power BI | `tb_101.powerbi.dim_date`, `dim_time`, `row_policy_map` | 日付・時刻ディメンションと行アクセス用の表 | [`end-to-end-analytics-with-snowflake-and-power-bi.md`](../../snowflake_contents/training/bi_analytics/end-to-end-analytics-with-snowflake-and-power-bi.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/end-to-end-analytics-with-snowflake-and-power-bi/end-to-end-analytics-with-snowflake-and-power-bi.md)） |
| Microsoft Purview | `PurviewLab.RAW.CUSTOMER`（10 行）, `PurviewLab.RAW.ORDERS`（21 行） | `INSERT` で作る小さなサンプル。都市名（Hamburg、Paris など）は Tasty Bytes と共通だが、中核テーブルとは別のデータ | [`getting-started-with-microsoft-purview-and-snowflake.md`](../../snowflake_contents/training/governance_sharing/getting-started-with-microsoft-purview-and-snowflake.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/getting-started-with-microsoft-purview-and-snowflake/getting-started-with-microsoft-purview-and-snowflake.md)） |
| Horizon 組織内共有 | `weather.history_day`, `weather.postal_codes` | Marketplace の Weather Source から作るローカルコピー（[Marketplace・第三者データ](marketplace-third-party-data.md)） | [`200_setup_data_products.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/200_setup_data_products.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/200_setup_data_products.sql)） |

Internal Marketplace による社内共有の教材は、データベース名に `tasty_bytes_local` などを使いますが、リポジトリの SQL が作るテーブルは TPC-H 系（`CUSTOMER`, `LINEITEM`, `ORDERS` など）とサプライチェーン用で、Tasty Bytes の中核データは読み込みません（[`sfguide-intra-company-data-sharing-with-the-snowflake-internal-marketplace`](../../snowflake_contents/github/bi_applications_sharing/sfguide-intra-company-data-sharing-with-the-snowflake-internal-marketplace)（[原本](https://github.com/Snowflake-Labs/sfguide-intra-company-data-sharing-with-the-snowflake-internal-marketplace/tree/668d3ef8eeb066ecae9251987200139f380203a0/)））。

## 8. 参考: 目次（catalog）の対象外で Tasty Bytes データを使うガイド

`snowflake_contents/catalog.json` の対象リンクには含まれていませんが、取得した sfquickstarts リポジトリの中で Tasty Bytes のデータを使っているガイドです。本文の詳細はこのウィキでは扱っていません。

| ガイド | 使うデータ | 出典 |
| --- | --- | --- |
| Getting Started with Hybrid Tables | `s3://sfquickstarts/hybrid_table_guide` の CSV から Hybrid Table `TRUCK`, `ORDER_HEADER_*` など | [`getting-started-with-hybrid-tables`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/getting-started-with-hybrid-tables)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/tree/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/getting-started-with-hybrid-tables)） |
| Intro to Iceberg | `s3://sfquickstarts/tastybytes/raw_pos/menu/` を Iceberg テーブル `menu_raw` へ | [`intro-to-iceberg`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/intro-to-iceberg)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/tree/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/intro-to-iceberg)） |
| Snowflake Postgres: Getting Started with Tables | `quickstart.truck`, `truck_history`, `order_header`（`INSERT` で作成） | [`snowflake-postgres-getting-started-with-tables`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/snowflake-postgres-getting-started-with-tables)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/tree/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/snowflake-postgres-getting-started-with-tables)） |
| Secure Multi-tenant Data Applications（Sigma） | `FROSTBYTE_TASTY_BYTES.HARMONIZED.ORDERS` に行アクセスポリシー | [`snowflake-build-secure-multitenant-data-applications-snowflake-sigma`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/snowflake-build-secure-multitenant-data-applications-snowflake-sigma)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/tree/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/snowflake-build-secure-multitenant-data-applications-snowflake-sigma)） |
| Data Engineering with Snowpark Python（Intro）・with Notebooks | `FROSTBYTE_RAW_STAGE`（Parquet）と `FROSTBYTE_WEATHERSOURCE` | [`data-engineering-with-snowpark-python-intro`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/data-engineering-with-snowpark-python-intro)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/tree/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/data-engineering-with-snowpark-python-intro)） |

## 関連ページ

- [ER 図（全テーブル）](er-diagram.md)
- [ソースデータの全体像](source-data-overview.md)
- [非構造化データ](unstructured-data.md)
- [Marketplace・第三者データ](marketplace-third-party-data.md)
- [教材別データソース対応表](../tutorials/data-sources-by-tutorial.md)
