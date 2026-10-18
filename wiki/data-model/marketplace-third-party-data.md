# Marketplace・第三者データ

Tasty Bytes の教材は、自社データ（POS・顧客）に Snowflake Marketplace の第三者データを結合して分析します。Marketplace のデータは S3 から読み込むのではなく、リスティングを「Get」して**共有データベース**として参照します。共有データベースの名前は取得時に利用者が付けるため、教材ごとに違います。

> 共有データベースの列定義は、このリポジトリのソースには含まれていません。下の表の列は、教材の SQL が実際に参照している列だけです。

## 1. Weather Source（気象データ）

### リスティングとデータベース名

| 教材 | リスティング名（原本の表記） | データベース名 | 出典 |
| --- | --- | --- | --- |
| Zero to Snowflake v2（vignette-5） | Weather Source LLC: frostbyte | `ZTS_WEATHERSOURCE` | [`vignette-5.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-5.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-5.sql)） |
| Zero to Snowflake FY25（コラボレーション） | Weather Source LLC: frostbyte | `TB_WEATHERSOURCE` | [`tb_collaboration.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_collaboration.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_collaboration.sql)） |
| Zero to Snowflake v1（コラボレーション） | — | `FROSTBYTE_WEATHERSOURCE` | [`tb_zts_collaboration.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/tb_zts_collaboration.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/tb_zts_collaboration.sql)） |
| Snowpark Python データエンジニアリング | Weather Source LLC: frostbyte | `FROSTBYTE_WEATHERSOURCE` | [`03_load_weather.sql`](../../snowflake_contents/github/data_engineering_dbt/sfguide-data-engineering-with-snowpark-python/steps/03_load_weather.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python/blob/44c92001766275725eaa8c29d94e81562f00c03e/steps/03_load_weather.sql)） |
| Horizon 組織内共有 | Weather Source LLC: frostbyte | `FROSTBYTE_WEATHERSOURCE` | [`200_setup_data_products.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/200_setup_data_products.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/200_setup_data_products.sql)） |
| VS Code 拡張（リモート開発） | リスティング `GZSOZ1LLEL` を SQL で取得 | `frostbyte_weathersource` | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-getting-started-with-remote-development-vscode-extension/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-with-remote-development-vscode-extension/blob/1f509be4b9387757776a629da32c2fd3bb49ed9e/setup.sql)） |
| Northstar データエンジニアリング | Pelmorex Weather Source: Frostbyte | `Pelmorex_Weather_Source_frostbyte` | [`snowflake-northstar-data-engineering.md`](../../snowflake_contents/training/data_engineering/snowflake-northstar-data-engineering.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/snowflake-northstar-data-engineering/snowflake-northstar-data-engineering.md)） |

VS Code 拡張の setup.sql は、`SYSTEM$REQUEST_LISTING_AND_WAIT('GZSOZ1LLEL')`、`SYSTEM$ACCEPT_LEGAL_TERMS(...)`、`CREATE DATABASE IF NOT EXISTS frostbyte_weathersource FROM LISTING 'GZSOZ1LLEL'` で、リスティングの取得をコードで行います。

**[推測]** Northstar 教材のリスティング名「Pelmorex Weather Source: Frostbyte」は、ほかの教材の「Weather Source LLC: frostbyte」と同じ系統のデータの新しい表記と考えられます。どちらも `onpoint_id.history_day` / `onpoint_id.postal_codes` を参照しますが、同じリスティングかどうかはソースからは確認できません。

### 参照されるテーブルと列

| テーブル | 教材が参照する列 |
| --- | --- |
| `onpoint_id.history_day` | `date_valid_std`, `postal_code`, `country`, `city_name`, `avg_temperature_air_2m_f`, `tot_precipitation_in`, `tot_snowdepth_in`, `max_wind_speed_100m_mph` |
| `onpoint_id.postal_codes` | `postal_code`, `country`, `city_name` |

### Tasty Bytes との結合

`harmonized.daily_weather_v` は次のように結合します（FY25・v2・Horizon で同じ形）。

```sql
FROM <weather_db>.onpoint_id.history_day hd
JOIN <weather_db>.onpoint_id.postal_codes pc
    ON pc.postal_code = hd.postal_code
    AND pc.country = hd.country
JOIN tb_101.raw_pos.country c
    ON c.iso_country = hd.country
    AND c.city = hd.city_name
```

つまり、気象データの国コード・都市名と、`raw_pos.country` の `iso_country`・`city` が一致する都市だけが残ります。この結果を `orders_v` と日付・都市・国で結合し、日別の売上と気象を並べたビュー（`daily_city_metrics_v`、`daily_sales_by_weather_v`）を作ります（[整合・分析レイヤのビュー](harmonized-analytics-views.md)）。

Horizon 組織内共有教材は、共有データをそのまま使わず、`frostbyte_tasty_bytes.weather.history_day`（`country in ('US','DE','ZA') AND year(date_valid_std) = 2022`）と `weather.postal_codes`（`country in ('US','DE','ZA')`）に CTAS でコピーしてから、データ製品として共有します。

## 2. SafeGraph（POI・地点データ）

### リスティングとデータベース名

| 教材 | リスティング名 | データベース名 | 出典 |
| --- | --- | --- | --- |
| Zero to Snowflake v2（vignette-5） | Safegraph: frostbyte | `ZTS_SAFEGRAPH` | [`vignette-5.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-5.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-5.sql)） |
| Zero to Snowflake FY25（地理空間） | SafeGraph: frostbyte | `TB_SAFEGRAPH` | [`tb_geospatial.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_geospatial.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_geospatial.sql)） |
| Zero to Snowflake v1（地理空間） | — | `FROSTBYTE_SAFEGRAPH` | [`tb_zts_geospatial.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/tb_zts_geospatial.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/tb_zts_geospatial.sql)） |
| Snowpark 101 for Data Science | SafeGraph: frostbyte | `FROSTBYTE_SAFEGRAPH` | [`tasty-bytes-snowpark-101-for-data-science.md`](../../snowflake_contents/training/data_science_machine_learning/tasty-bytes-snowpark-101-for-data-science.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-snowpark-101-for-data-science/tasty-bytes-snowpark-101-for-data-science.md)） |
| Power BI | — | `SAFEGRAPH_FROSTBYTE` | [`end-to-end-analytics-with-snowflake-and-power-bi.md`](../../snowflake_contents/training/bi_analytics/end-to-end-analytics-with-snowflake-and-power-bi.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/end-to-end-analytics-with-snowflake-and-power-bi/end-to-end-analytics-with-snowflake-and-power-bi.md)） |

どの教材もテーブル `public.frostbyte_tb_safegraph_s` を参照します。

### 参照される列と結合キー

教材が参照する列: `location_id`, `placekey`, `location_name`, `latitude`, `longitude`, `top_category`, `sub_category`, `category_tags`, `city`, `country`, `iso_country_code`, `postal_code`, `polygon_wkt`, `includes_parking_lot`, `open_hours`, `region`, `phone_number`。

| 結合キー | 使う教材 |
| --- | --- |
| `location_id`（`orders_v.location_id` または `shift_sales.location_id`） | FY25 地理空間、Snowpark 101 |
| `location_id` と `iso_country_code` | Zero to Snowflake v2（`harmonized.tastybytes_poi_v`） |
| `placekey` | Power BI（`raw_pos.location.placekey` と比較） |

`frostbyte_tb_safegraph_s` が `location_id` 列を持つことから、**[推測]** この共有データは Tasty Bytes の販売場所に合わせて用意された教材用のデータです。

価格最適化教材は、Marketplace ではなく S3 から SafeGraph 形式のテーブル `raw_safegraph.core_poi_geometry` を読み込みます（[教材固有のテーブル](tutorial-specific-tables.md#price-optimization)）。

## 3. Snowflake Public Data（祝日）

出典: [`ml-forecasting-ad.md`](../../snowflake_contents/training/data_science_machine_learning/ml-forecasting-ad.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/ml-forecasting-ad/ml-forecasting-ad.md)）

ML 予測・異常検知の教材は、Snowflake Public Data のリスティングを `FROSTBYTE_CS_PUBLIC` という名前で取得し、`PUBLIC_DATA_FREE.public_holiday_calendar` から `date`, `holiday_name`, `is_financial` を使います（`ISO_ALPHA2 LIKE 'CA'` などで Canada の祝日に絞り込み）。Vancouver の売上予測に、祝日を外部変数として加えるためです。

## 関連ページ

- [ソースデータの全体像](source-data-overview.md)
- [整合・分析レイヤのビュー](harmonized-analytics-views.md)
- [版による差異・矛盾](version-differences.md)
