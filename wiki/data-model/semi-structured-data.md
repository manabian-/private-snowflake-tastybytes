# 半構造化データ

`VARIANT` / `OBJECT` / `ARRAY` / `VECTOR` 型の列、または JSON 文字列を持つ列を一覧にし、入れ子の構造を原本の SQL・コードから読み取れる範囲で説明します。値の実例は原本に載っているものだけを示し、構造の説明に使う図は原本の参照式（`:` や `[0]`）から組み立てたものです。

## 一覧

| テーブル.列 | 型 | 内容 | 詳細 |
| --- | --- | --- | --- |
| `raw_pos.menu.menu_item_health_metrics_obj` | `VARIANT` | 品目 ID・材料・食事制限フラグ | [下記](#menu_item_health_metrics_obj) |
| `raw_pos.truck.truck_build` / `raw_pos.truck_details.truck_build` | `OBJECT`（v2 で追加） | 製造年・メーカー・車種 | [下記](#truck_build) |
| `harmonized.customer_loyalty_metrics_v.visited_location_ids_array` | `ARRAY` | 訪問した `location_id` の配列 | [ビュー](harmonized-analytics-views.md#customer-loyalty-metrics) |
| `raw_doc.inspection_report_raw_extract.inspection_report_object` | `VARIANT` | 検査レポートから抽出した項目 | [下記](#inspection_report_object) |
| `analytics.review_analysis_output.category_sentiment` | `VARCHAR`（JSON 配列の文字列） | カテゴリ別の感情と詳細 | [下記](#category_sentiment) |
| `raw_support.email_status_app.email_object` | `VARIANT` | 受信メール | [下記](#email_object) |
| `raw_support.email_response_app.email_response` | `VARIANT` | 送信した返信 | [下記](#email_object) |
| `SUPPORT_EMAILS.TIMESTAMP` | `VARIANT` | メールのタイムスタンプ | [下記](#support_emails) |
| `harmonized.array_table.chunk_embedding` → `vector_store.chunk_embedding` | `ARRAY` → `VECTOR(FLOAT, 768)` | 文書チャンクの埋め込み | [下記](#embeddings) |
| `raw_safegraph.core_poi_geometry.open_hours` | `VARIANT` | 営業時間 | [下記](#poi) |
| `media.image_table.img_file` / `audio_table.audio_file` | `TO_FILE(...)` の結果（FILE 値） | ステージ上のファイル参照 | [非構造化データ](unstructured-data.md#images-audio) |

<a id="menu_item_health_metrics_obj"></a>

## `menu_item_health_metrics_obj`

出典: [`vignette-2.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-2.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-2.sql)）、[`tb_semi_structured_data.sql`](../../snowflake_contents/github/common_resources/sf-samples/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_semi_structured_data.sql)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/tasty_bytes/FY25_Zero_To_Snowflake/tb_semi_structured_data.sql)）

vignette-2 のコメントは、この `VARIANT` に次の 2 つのキーがあると説明しています。

- `menu_item_id`: 品目の一意な識別子（数値）
- `menu_item_health_metrics`: 健康情報のオブジェクトを持つ配列。各オブジェクトには、文字列の配列 `ingredients` と、`'Y'` / `'N'` の値を持つ複数の食事制限フラグがある

フラグのキー名は `harmonized.menu_v` の定義から分かります: `is_healthy_flag`, `is_gluten_free_flag`, `is_dairy_free_flag`, `is_nut_free_flag`。

```text
menu_item_health_metrics_obj
├── menu_item_id                 (数値)
└── menu_item_health_metrics     (配列)
    └── [n]
        ├── ingredients          (文字列の配列)
        ├── is_healthy_flag      ('Y' / 'N')
        ├── is_gluten_free_flag  ('Y' / 'N')
        ├── is_dairy_free_flag   ('Y' / 'N')
        └── is_nut_free_flag     ('Y' / 'N')
```

教材での使い方:

- `harmonized.menu_v` は `LATERAL FLATTEN (input => m.menu_item_health_metrics_obj:menu_item_health_metrics)` で配列を行に展開し、`obj.value:"ingredients"::VARIANT` と各フラグを `VARCHAR(1)` で取り出します。
- vignette-2 は `menu_item_health_metrics[0]:ingredients::ARRAY` を `FLATTEN` して材料を 1 行ずつにし、Dynamic Table `harmonized.ingredient`（材料名と、その材料を使う `menu_item_id` の配列）を作ります。
- vignette-2 は新しい品目（Banh Mi）を `menu_staging` に挿入し、Dynamic Table に新しい材料が反映されることを確かめます。

**[推測]** 原本の参照式はいずれも配列の先頭要素（`[0]`）だけを使うか、`FLATTEN` で全要素を展開しています。品目ごとに配列の要素が 1 つかどうかは、ソースからは確認できません。

<a id="truck_build"></a>

## `truck_build`

出典: [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)）、[`vignette-1.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-1.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-1.sql)）

v2 Setup がデータ読み込み後に作る列です。元データ（CSV）には含まれません。

```sql
ALTER TABLE tb_101.raw_pos.truck ADD COLUMN truck_build OBJECT;
UPDATE tb_101.raw_pos.truck
    SET truck_build = OBJECT_CONSTRUCT('year', year, 'make', make, 'model', model);
```

その後、`truck_build:make::STRING = 'Ford_'` かつ `truck_id % 2 = 0` の行だけ `make` を `'Ford'` に置き換え、`year`・`make`・`model` 列を除いた `truck_details` を作ります。vignette-1 はこの列を「VARIANT data type」と説明し、`truck_build:year::NUMBER` などで取り出して `'Ford'` / `'Ford_'` の表記ゆれを修正させます。Setup の DDL では型は `OBJECT` です。

<a id="inspection_report_object"></a>

## `inspection_report_object`

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-experience-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-experience-app/setup/setup.sql)）

フードトラック検査レポート（画像）から取り出した項目を入れた `VARIANT` 列です。テーブル `raw_doc.inspection_report_raw_extract` は `FILE_NAME`, `EXTRACTION_TIMESTAMP TIMESTAMP_LTZ(9)`, `INSPECTION_REPORT_OBJECT VARIANT` の 3 列で、抽出済みの結果が `s3://sfquickstarts/tastybytes-ece/raw_doc/inspection_report_raw_extract/` から読み込まれます。

ビュー `harmonized.inspection_reports_v` は、各項目を `inspection_report_object:"<項目名>"[0].value` で取り出します。

```text
inspection_report_object
├── "DATE"        → [0].value  (例: '-' を '/' に置換して TO_DATE)
├── "TRUCK_ID"    → [0].value  (::integer、raw_pos.truck と結合)
├── "CITY"        → [0].value  (INITCAP)
├── "COUNTRY"     → [0].value  ('USA' / 'US' は 'United States' に変換)
└── 検査項目 20 個 → [0].value  ('Y' / 'N' / 'X')
```

検査項目（列名）: `PIC_PRESENT`, `PIC_KNOWLEDGE`, `HANDS_CLEAN_WASHED`, `ADEQUATE_HW_FACILITIES`, `FOOD_APPROVED_SOURCE`, `FOOD_PROPER_TEMP`, `THERMOMETERS_ACCURATE`, `FOOD_PROTECTED`, `FOOD_SURFACE_CLEAN`, `NONFOOD_SURFACE_CLEAN`, `WATER_ICE_SOURCE_APPROVED`, `WATER_ICE_CONTAMINANT_FREE`, `UTENSILS_PROPER_STORAGE`, `GLOVES_USE_PROPER`, `WATER_PRESSURE_ADEQUATE`, `SEWAGE_DISPOSED_PROPERLY`, `GARBAGE_DISPOSED_PROPERLY`, `VENTILATION_LIGHTING_ADEQUATE`, `TIRES_ADEQUATE`, `VEHICLE_WELL_MAINTAINED`

値の変換: `'Y'` → `Pass`、`'N'` → `Fail`、`'X'` とそれ以外 → `Not Observed`。`analytics.inspection_reports_v` は `Fail` の数が 5 以上なら `overall_result` を `'Fail'`、それ以外を `'Pass'` にします。各項目の説明とカテゴリは参照表 `raw_doc.inspection_report_ref`（`IRR_ID`, `COLUMN_NAME`, `DESCRIPTION`, `CATEGORY`）にあり、`analytics.inspection_reports_unpivot_v` で項目名と結合されます。

教材原本は、この抽出に Document AI を使ったと説明しています（「We have previously used DocumentAI to structure the contents of inspection reports」、[`tasty-bytes-customer-experience-app.md`](../../snowflake_contents/training/cortex_generative_ai/tasty-bytes-customer-experience-app.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-customer-experience-app/tasty-bytes-customer-experience-app.md)））。**[推測]** `"項目名"[0].value` という形は、Document AI の抽出結果（項目ごとに値の候補を配列で返す形式）をそのまま保存したものと考えられます。

<a id="category_sentiment"></a>

## `category_sentiment`

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-experience-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-experience-app/setup/setup.sql)）

`analytics.review_analysis_output` はレビューの分析結果を事前計算したテーブルで、`s3://sfquickstarts/tastybytes-ece/analytics/review_analysis_output/` から読み込みます。列は `TRUCK_ID`, `REVIEW_ID NUMBER(18,0)`, `REVIEW`, `SENTIMENT FLOAT`, `TRANSLATED_REVIEW`, `RATING`, `CLEAN_RATING`, `RECOMMEND`, `CLEAN_RECOMMEND`, `CATEGORY_SENTIMENT` です。

`CATEGORY_SENTIMENT` は `VARCHAR` ですが、ビュー `review_analysis_output_v` が `LATERAL FLATTEN (PARSE_JSON(TO_VARIANT(rao.category_sentiment)))` で展開し、各要素から `value:category`, `value:sentiment`, `value:details` を取り出します。つまり中身は、`category` / `sentiment` / `details` を持つオブジェクトの JSON 配列です。

<a id="email_object"></a>

## `email_object` / `email_response`

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-support-email-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-support-email-app/setup/setup.sql)）、[`01_Queue.py`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-support-email-app/app/01_Queue.py)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-support-email-app/app/01_Queue.py)）

| テーブル | 列 |
| --- | --- |
| `raw_support.email_status_app` | `EMAIL_ID`（自動採番、1 から）, `EMAIL_STATUS_CODE`, `EMAIL_STATUS_DEF VARCHAR(255)`, `RESPONDED_FLAG BOOLEAN`, `LAST_UPDATED_TS`, `EMAIL_OBJECT VARIANT` |
| `raw_support.email_response_app` | `EMAIL_R_ID`（自動採番、1000 から）, `EMAIL_ID`, `EMAIL_RESPONSE VARIANT`, `SENT_TS` |

`EMAIL_OBJECT` の構造は、新規メールを登録するプロシージャとアプリのコードから分かります。

- プロシージャ `insert_new_email_app` は `{"Request": "<メール文字列>"}` という JSON を `PARSE_JSON` して保存し、`email_status_code = 1`、`email_status_def = 'new'` を設定します。
- アプリは `json.loads(data['Request'])` で `Request` の中身をもう一度 JSON として読み、`timestamp`（`%Y-%m-%dT%H:%M:%SZ` 形式）、`sender`、`subject`、`body` を使います。

```text
EMAIL_OBJECT
└── "Request"  (JSON 文字列)
    ├── timestamp
    ├── sender
    ├── subject
    └── body
```

自動応答プロシージャ `process_auto_responses_app` は、`SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', ...)` に JSON スキーマ（`responder` は `"auto"` / `"agent"`、`subject`、`body`）を渡して構造化出力を得ます。

<a id="support_emails"></a>

## `SUPPORT_EMAILS`

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-enhancing-customer-experiences-using-cortex-finetuning/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-enhancing-customer-experiences-using-cortex-finetuning/blob/3b782b2b15883d2581eb554a4d9013e93592ba2d/scripts/setup.sql)）

ファインチューニング教材のテーブルで、`TIMESTAMP` 列が `VARIANT` です。

| 列 | 型 |
| --- | --- |
| `ID` | `INTEGER` |
| `TIMESTAMP` | `VARIANT` |
| `SENDER` | `VARCHAR` |
| `SUBJECT` | `VARCHAR` |
| `BODY` | `VARCHAR` |
| `LABELED_LOCATION` | `VARCHAR` |
| `LABELED_TRUCK` | `VARCHAR` |
| `SUPPORT_RESPONSE` | `VARCHAR` |

関数 `BUILD_EXAMPLE` が `LABELED_LOCATION`・`LABELED_TRUCK`・`SUPPORT_RESPONSE` から `{ location: ..., truck: ..., response_body: ... }` 形式の文字列 `GOLDEN_JSON` を作り、`ID % 10 >= 2` を学習用、`ID % 10 < 2` を検証用に分けます。`mistral-7b` をファインチューニングしたモデルの出力は `TRY_PARSE_JSON(RESPONSE):location` などで評価します。

<a id="embeddings"></a>

## 埋め込み（`ARRAY` → `VECTOR`）

出典: [`tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md`](../../snowflake_contents/training/cortex_generative_ai/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-rag-chatbot-using-cortex-and-streamlit/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md)）、[`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-support-email-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-support-email-app/setup/setup.sql)）

RAG チャットボットとサポートメールアプリは、事前計算済みの埋め込みを `CHUNK_EMBEDDING ARRAY` 列のテーブル（`array_table`）に `COPY INTO` で読み込みます。続けて `chunk_embedding::VECTOR(FLOAT, 768)` に変換した `vector_store` を CTAS で作ります。チャットボット教材の SQL には、`ARRAY` を経由する理由として VECTOR 型のロード・アンロードに関するドキュメントの URL がコメントで書かれています。

検索時は `SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ...)` で質問やメールを埋め込み、`VECTOR_COSINE_SIMILARITY` で最も近いチャンクを 1 件選びます。

`vector_store` の列: `SOURCE VARCHAR(6)`, `SOURCE_DESC`, `FULL_TEXT`, `SIZE NUMBER(18,0)`, `CHUNK`, `INPUT_TEXT`, `CHUNK_EMBEDDING VECTOR(FLOAT, 768)`。サポートメールアプリは `SOURCE IN ('PUBLIC', 'EMAIL')` で絞り込み、エージェントが返信すると `'EMAIL'` / `'Customer support Email history with a Tasty Bytes Agent'` として知識ベースに追加します。

<a id="poi"></a>

## POI の営業時間・ポリゴン

出典: [`tb_po_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/sql/tb_po_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/sql/tb_po_setup.sql)）

価格最適化教材の `raw_safegraph.core_poi_geometry` は SafeGraph 形式の POI データで、`OPEN_HOURS VARIANT` と、ポリゴンの WKT 文字列 `POLYGON_WKT VARCHAR` を持ちます。同梱 CSV の先頭データ行では `POLYGON_WKT` が `"POLYGON ((11.632933 48.118492, ...` の形です（[`core_poi_geometry.csv`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/csv/raw_safegraph/core_poi_geometry.csv)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/csv/raw_safegraph/core_poi_geometry.csv)））。

## その他の半構造化データ

| 対象 | 内容 | 出典 |
| --- | --- | --- |
| Parquet ファイル | Snowpark Python データエンジニアリング教材は Parquet（Snappy）を `session.read.parquet()` で読み、スキーマを推論して `copy_into_table` する | [`02_load_raw.py`](../../snowflake_contents/github/data_engineering_dbt/sfguide-data-engineering-with-snowpark-python/steps/02_load_raw.py)（[原本](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python/blob/44c92001766275725eaa8c29d94e81562f00c03e/steps/02_load_raw.py)） |
| 外部テーブル `ext_survey_data` | パイプ区切り CSV のレビューを外部テーブルにし、`value:c1` などを型変換した仮想列で参照する | [`tasty-bytes-working-with-iceberg-tables.md`](../../snowflake_contents/training/data_engineering/tasty-bytes-working-with-iceberg-tables.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-working-with-iceberg-tables/tasty-bytes-working-with-iceberg-tables.md)） |
| DCM の `ALL_ITEMS.ITEM_CATEGORY` / `ALL_REGIONS.CATEGORIES` | `array` 型の列 | [`raw.sql`](../../snowflake_contents/github/data_engineering_dbt/snowflake-dcm-projects/sample-projects/dcm-full-demo-project/sources/definitions/raw.sql)（[原本](https://github.com/Snowflake-Labs/snowflake-dcm-projects/blob/92ca6a42b2aec4c7bc7405664b7a16ec349baab4/sample-projects/dcm-full-demo-project/sources/definitions/raw.sql)） |
| `AI_CLASSIFY` の戻り値 | `:labels[0]::TEXT` で最初のラベルを取り出す | [`gaining_insights_from_unstructured_data.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/gaining_insights_from_unstructured_data.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/gaining_insights_from_unstructured_data.ipynb)） |
| `AI_TRANSCRIBE` の戻り値 | Notebook は `json.loads` した結果の `audio_duration` と `text` を表示する | [`gaining_insights_from_unstructured_data.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/gaining_insights_from_unstructured_data.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/gaining_insights_from_unstructured_data.ipynb)） |

## 関連ページ

- [中核データモデル](core-pos-model.md)
- [非構造化データ](unstructured-data.md)
- [教材固有のテーブル](tutorial-specific-tables.md)
