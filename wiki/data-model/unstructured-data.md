# 非構造化データ

Tasty Bytes 教材で使われる自由記述テキスト・文書・画像・音声・動画を、データの種類ごとにまとめます。各項目で「どこにあるか（S3・同梱ファイル・内部ステージ）」「どのテーブル・ステージに入るか」「どの機能で処理されるか」を示します。

## 一覧

| 種類 | データ | 置き場所 | Snowflake 側 | 主な処理 |
| --- | --- | --- | --- | --- |
| テキスト | [トラックのレビュー](#truck-reviews) | `s3://sfquickstarts/tastybytes-voc/raw_support/truck_reviews/` | `raw_support.truck_reviews.review` | 翻訳・感情分析・分類・要約・検索 |
| テキスト | [四半期別レビューファイル](#review-files) | リポジトリ同梱 ZIP／利用者の S3 バケット | 外部テーブル・Iceberg テーブル | 外部テーブル・Iceberg の演習 |
| テキスト | [サポートメール](#emails) | `s3://sfquickstarts/tastybytes-ece/`、`s3://sfquickstarts/frostbyte_tastybytes/fine_tuning/` | `email_status_app`, `SUPPORT_EMAILS` | RAG による自動返信、ファインチューニング |
| 文書 | [社内文書・チャットログ（RAG）](#rag-documents) | `s3://sfquickstarts/tastybytes-cx/app/`、`s3://sfquickstarts/tastybytes-ece/harmonized/` | `documents`, `chunk_text`, `vector_store` | 埋め込み・ベクトル検索・回答生成 |
| 画像 | [検査レポート](#inspection-reports) | `s3://sfquickstarts/tastybytes-ece/raw_doc/inspection_report/` | 内部ステージ `raw_doc.inspection_reports` | Document AI（抽出済み結果を読み込み） |
| 画像・音声・動画 | [マルチモーダル教材のメディア](#images-audio) | リポジトリ同梱 `data.zip` | 内部ステージ `tb_voc.media.images` / `audio` / `video` | `AI_COMPLETE`, `AI_TRANSCRIBE`, `AI_EXTRACT` |
| 音声 | [音声注文](#voice-orders) | Notebook で生成 | 内部ステージ `TASTY_AUDIO_DB.ORDERS.AUDIO_STAGE` | `AI_TRANSCRIBE` → `AI_COMPLETE` |
| テキスト | [映画レビュー（IMDB）](#imdb-reviews) | リポジトリ同梱 TXT 100 件 | 内部ステージ `movie_reviews.movie_stage` | Python UDF で読み込み、要約・感情分析 |
| テキスト | [EC 商品レビュー](#ecommerce-reviews) | `s3://sfquickstarts/misc/aisql/ecommerce_customer_review/`（リポジトリにも同梱） | `product_reviews.review_text` | AISQL（`AI_FILTER`, `AI_AGG` など） |
| 表計算 | [価格設定シート](#excel) | `s3://sfquickstarts/frostbyte_tastybytes/excel`（リポジトリにも同梱） | ステージ `excel_s3` | pandas で読み込み |

<a id="truck-reviews"></a>

## 1. トラックのレビュー（`truck_reviews`）

### データ

`raw_support.truck_reviews` は顧客がフードトラックについて書いたレビューのテーブルです（列定義は [中核データモデル](core-pos-model.md#truck-reviews)）。`order_id` で `raw_pos.order_header` と結び付き、ビュー `truck_reviews_v` でトラック・都市・ブランド・日付が付きます（[ビュー](harmonized-analytics-views.md#truck-reviews-v)）。

- 本文 `review` は多言語です。教材は `language` が `'en'` でない行を `SNOWFLAKE.CORTEX.TRANSLATE(REVIEW, LANGUAGE, 'en')` で英語に翻訳します（[`gaining_insights_from_unstructured_data.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/gaining_insights_from_unstructured_data.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/gaining_insights_from_unstructured_data.ipynb)））。
- 同じ形式のレビューファイル（[次節](#review-files)）の先頭行では、ポルトガル語（`pt`）と韓国語（`ko`）のレビューを確認できます。
- `source` 列の値の一覧は、ソースからは確認できません。四半期別ファイルでは `SOURCE` が数値（例: `6`）で、フォルダ名は `Google Maps` / `Internal Platform` / `Trip Advisor` / `Yelp` です。**[推測]** `source` はレビューの投稿元を表す列です。

### 読み込む教材

| データベース | 出典 |
| --- | --- |
| `tb_101`（Zero to Snowflake v2） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |
| `tb_voc`（顧客レビュー分析） | [`tb_voc_setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-customer-reviews-analytics-using-snowflake-cortex/setup/tb_voc_setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-customer-reviews-analytics-using-snowflake-cortex/blob/661f0f868b8cec0789e6b01579f33fa4b484955e/setup/tb_voc_setup.sql)） |
| `tb_voc`（非構造化データからの洞察） | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/setup.sql)）、[`setup.sql`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)） |
| `tb_voc`（Hex） | [`analyzing-customer-reviews-using-hex-and-snowflake-cortex.md`](../../snowflake_contents/training/bi_analytics/analyzing-customer-reviews-using-hex-and-snowflake-cortex.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/analyzing-customer-reviews-using-hex-and-snowflake-cortex/analyzing-customer-reviews-using-hex-and-snowflake-cortex.md)） |
| スキーマ指定なし（翻訳テンプレート） | [`Step 1 -- Setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/translate-customer-reviews-template/Step%201%20--%20Setup.sql)（[原本](https://github.com/Snowflake-Labs/translate-customer-reviews-template/blob/27ed5cae9b746ef7c2df82e87f6c34454f97a53f/Step%201%20--%20Setup.sql)） |

### 処理と派生データ

| 処理 | 内容 | 出典 |
| --- | --- | --- |
| Cortex Search | `harmonized.tasty_bytes_review_search`（`ON REVIEW`） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/setup.sql)） |
| 感情分析・分類・抽出・要約 | `SENTIMENT()`、`AI_CLASSIFY()`、`EXTRACT_ANSWER()`、`AI_SUMMARIZE_AGG()` | [`vignette-3-aisql.sql`](../../snowflake_contents/github/common_resources/sfguide-getting-started-from-zero-to-snowflake/scripts/vignette-3-aisql.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake/blob/e12f556e2c23c155ddc6ac8a1be4953bb93332b0/scripts/vignette-3-aisql.sql)） |
| 推薦の分類 | `AI_CLASSIFY(REVIEW, ['Likely', 'Unlikely', 'Unsure'], ...)` | [`gaining_insights_from_unstructured_data.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/gaining_insights_from_unstructured_data.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/gaining_insights_from_unstructured_data.ipynb)） |
| ブランド別の連結 | `analytics.CONCATENATED_REVIEWS`（ブランドごとに先頭 20 件を `ARRAY_AGG` して空白で連結） | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/setup.sql)） |
| サンプルビュー | `analytics.TRUCK_REVIEWS_V_SAMPLE`（ブランドごとに英語を優先して無作為に抽出） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)） |
| 評価用データ | `analytics.EXTRACTION_EVAL_DATA`（レビュー文と期待される抽出結果 `EXPECTED_OUTPUT VARIANT` を `INSERT` で作成） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)） |
| 事前計算済みの分析結果 | `analytics.review_analysis_output`（感情・翻訳・評価・推薦・カテゴリ別感情） | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-experience-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-experience-app/setup/setup.sql)） |

`EXTRACTION_EVAL_DATA` のレビュー文は SQL 内に直接書かれた例文で、S3 のレビューデータとは別のものです。`review_analysis_output` の `CATEGORY_SENTIMENT` の構造は [半構造化データ](semi-structured-data.md#category_sentiment) を参照してください。

<a id="review-files"></a>

## 2. 四半期別レビューファイル（外部テーブル・Iceberg 用）

出典: [`2022.zip`](../../snowflake_contents/github/bi_applications_sharing/visual_analytics_powered_by_snowflake_and_tableau/data/2022.zip)（[原本](https://github.com/Snowflake-Labs/visual_analytics_powered_by_snowflake_and_tableau/blob/8104683d3efd98c543da1db56898ab0a4756474f/data/2022.zip)）、[`tasty-bytes-working-with-iceberg-tables.md`](../../snowflake_contents/training/data_engineering/tasty-bytes-working-with-iceberg-tables.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-working-with-iceberg-tables/tasty-bytes-working-with-iceberg-tables.md)）、[`visual-analytics-powered-by-snowflake-and-tableau.md`](../../snowflake_contents/training/bi_analytics/visual-analytics-powered-by-snowflake-and-tableau.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/visual-analytics-powered-by-snowflake-and-tableau/visual-analytics-powered-by-snowflake-and-tableau.md)）

Tableau 教材のリポジトリに同梱された `2022.zip` には、レビューの CSV が 48 個入っています（4 四半期 × 投稿元 4 フォルダ × 各 3 ファイル）。

```text
2022/
├── Q1/
│   ├── Google Maps/        reviews_2022_1.csv ～ reviews_2022_3.csv
│   ├── Internal Platform/  …
│   ├── Trip Advisor/       …
│   └── Yelp/               …
├── Q2/ …
├── Q3/ …
└── Q4/ …
```

ファイルはパイプ（`|`）区切りで、ヘッダーは `ORDER_ID|TRUCK_ID|LANGUAGE|SOURCE|REVIEW|PRIMARY_CITY|CUSTOMER_ID|YEAR|MONTH|TRUCK_BRAND` です。

Iceberg 教材は、Google Drive からダウンロードした `truck_reviews` フォルダを利用者自身の S3 バケットに置き、ストレージ統合 `int_tastybytes_truckreviews` 経由で次のオブジェクトを作ります。

| オブジェクト | 内容 |
| --- | --- |
| ファイル形式 `raw.ff_csv` | `FIELD_DELIMITER = '\|'`, `SKIP_HEADER = 1` |
| ステージ `raw.stg_truck_reviews` | `s3://<bucket_name>/truck_reviews/` |
| 外部テーブル `raw.ext_survey_data` | ファイルパスから `source`（4 番目の要素）と `quarter`（2・3 番目の要素）を取り出し、`PARTITION BY (quarter, source)` |
| Iceberg テーブル `raw.icb_truck_reviews` | `source_name`, `quarter`, `order_id`, `truck_id`, `review`, `language`（`CATALOG = 'SNOWFLAKE'`） |

**[推測]** Iceberg 教材が Google Drive から配布するファイルと、Tableau リポジトリの `2022.zip` は同じ形式（パスの構造と列順が一致）ですが、同じファイルかどうかは確認できません。

<a id="emails"></a>

## 3. サポートメール

### カスタマーサポートメールアプリ

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-support-email-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-support-email-app/setup/setup.sql)）、[`tasty-bytes-customer-support-email-app.md`](../../snowflake_contents/training/cortex_generative_ai/tasty-bytes-customer-support-email-app.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-customer-support-email-app/tasty-bytes-customer-support-email-app.md)）

顧客からのメールは `raw_support.email_status_app.email_object`（`VARIANT`）に入り、返信は `email_response_app.email_response` に入ります。初期データは `s3://sfquickstarts/tastybytes-ece/raw_support/email_status_app/` と `.../email_response_app/` から読み込みます。JSON の構造は [半構造化データ](semi-structured-data.md#email_object) を参照してください。

教材原本によれば、メールが届くと Cortex LLM が知識ベースで回答できるかを判断し、回答できれば自動返信、できなければエージェントに回します。エージェントの返信は知識ベースに追加できます。

### ファインチューニング用メール

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-enhancing-customer-experiences-using-cortex-finetuning/scripts/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-enhancing-customer-experiences-using-cortex-finetuning/blob/3b782b2b15883d2581eb554a4d9013e93592ba2d/scripts/setup.sql)）

`s3://sfquickstarts/frostbyte_tastybytes/fine_tuning/CFT_QUICKSTART.csv` を `SUPPORT_EMAILS` に読み込みます（`FIELD_OPTIONALLY_ENCLOSED_BY = '"'`, `SKIP_HEADER = 1`）。本文 `BODY` に、正解ラベル（`LABELED_LOCATION`, `LABELED_TRUCK`）と模範回答（`SUPPORT_RESPONSE`）が付いた教師データです。列の詳細は [半構造化データ](semi-structured-data.md#support_emails) を参照してください。

<a id="rag-documents"></a>

## 4. 社内文書・チャットログ（RAG）

出典: [`tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md`](../../snowflake_contents/training/cortex_generative_ai/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-rag-chatbot-using-cortex-and-streamlit/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md)）、[`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-support-email-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-support-email-app/setup/setup.sql)）

RAG チャットボット教材は、取り出し対象を「previous agent support chat logs and public-facing documents (Annual Reports, FAQs)」と説明しています。データは文書そのものではなく、テキスト化・チャンク化・埋め込み済みの結果として配布されます。

| テーブル | 列 | 読み込み元 |
| --- | --- | --- |
| `documents` | `RELATIVE_PATH`, `RAW_TEXT` | チャットボット: `tastybytes-cx/app/documents/`、メールアプリ: `tastybytes-ece/harmonized/documents/` |
| `array_table` → `vector_store` | `SOURCE`, `SOURCE_DESC`, `FULL_TEXT`, `SIZE`, `CHUNK`, `INPUT_TEXT`, `CHUNK_EMBEDDING` | `.../vector_store/` |
| `chunk_text`（メールアプリのみ） | `SOURCE`, `SOURCE_DESC`, `FULL_TEXT`, `SIZE`, `CHUNK`, `META`, `INPUT_TEXT` | `tastybytes-ece/harmonized/chunk_text/` |

- チャットボットは `documents` から `relative_path = 'tasty_bytes_who_we_are.pdf'` の `raw_text` を読み、背景情報としてプロンプトに入れます。**[推測]** `documents` は PDF などの文書から取り出したテキストを、ファイルのパスごとに保存したものです。
- メールアプリは Python UDTF `harmonized.text_chunker` を定義しています。LangChain の `RecursiveCharacterTextSplitter`（区切り `"\n"`、`chunk_size = 5000`、`chunk_overlap = 3000`）で文章を分割します。
- 埋め込みと検索の仕組みは [半構造化データ](semi-structured-data.md#embeddings) を参照してください。

<a id="inspection-reports"></a>

## 5. フードトラック検査レポート（画像）

出典: [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience/customer-experience-app/setup/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience/blob/e62390203119710f8bbe8abe095c53f663c3581b/customer-experience-app/setup/setup.sql)）、[`tasty-bytes-customer-experience-app.md`](../../snowflake_contents/training/cortex_generative_ai/tasty-bytes-customer-experience-app.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/tasty-bytes-customer-experience-app/tasty-bytes-customer-experience-app.md)）

- ステージ `raw_doc.inspection_reports`（コメント「Inspection reports images」、ディレクトリテーブル有効、`SNOWFLAKE_SSE` 暗号化）を作り、`COPY FILES` で `s3://sfquickstarts/tastybytes-ece/raw_doc/inspection_report/` からファイルをコピーします。
- 抽出結果は `raw_doc.inspection_report_raw_extract` に読み込み済みのデータとして配布されます。教材内で Document AI を実行するわけではありません。教材原本は、検査レポートを「handwritten, unstructured inspection documents」と説明し、その処理は別の Document AI 教材で行ったとしています。
- ビュー `harmonized.inspection_reports_v` は、各ファイルの `BUILD_SCOPED_FILE_URL` と `GET_PRESIGNED_URL` を列として持ちます。アプリはこれで元の画像を表示できます。

抽出項目と判定ロジックは [半構造化データ](semi-structured-data.md#inspection_report_object) を参照してください。

<a id="images-audio"></a>

## 6. マルチモーダル教材のメディア（画像・音声・動画）

「非構造化データからの洞察」教材には、取得元によって内容の違う 2 つの版があります。

| 項目 | GitHub リポジトリ版 | sfquickstarts 版（教材 Markdown 原本と同じ場所） |
| --- | --- | --- |
| 出典 | [`setup.sql`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/setup.sql)）、[`data.zip`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/data.zip)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/blob/f5ce635e7638198d72a3211518d8c03406bba670/data.zip)） | [`setup.sql`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/setup.sql)）、[`setup-post-upload.sql`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/setup-post-upload.sql)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/setup-post-upload.sql)）、[`data.zip`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/data.zip)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/data.zip)） |
| ステージ | `tb_voc.media.images`, `tb_voc.media.audio` | `images`, `audio`, `video` |
| 画像 | `pexels-luizclas-170497-1848565.jpg`, `office_objects.PNG`, `faces.PNG`, `car_ad_1.PNG`, `car_ad_2.PNG` | `ft_01.jpeg` ～ `ft_06.jpeg` |
| 音声 | `consultation.wav`（30,890,958 バイト） | `consultation.wav`（同じサイズ） |
| 動画 | なし | `food_truck_clip_1.mp4` ～ `food_truck_clip_4.mp4` |
| 参照テーブル | Notebook が `CREATE TABLE ... AS SELECT RELATIVE_PATH, TO_FILE(...) FROM DIRECTORY(...)` で `IMAGE_TABLE` / `AUDIO_TABLE` を作る | setup.sql が `IMAGE_TABLE` / `AUDIO_TABLE` / `VIDEO_TABLE`（`*_PATH`, `UPLOAD_DATE`）を作り、アップロード後に `setup-post-upload.sql` で `DIRECTORY()` から挿入 |
| AI 関数 | `AI_COMPLETE`（`claude-3-5-sonnet` に画像を渡す）、`AI_TRANSCRIBE`、`AI_SENTIMENT`、`AI_CLASSIFY`、`AI_SUMMARIZE_AGG` | `AI_COMPLETE`、`AI_EXTRACT`、`AI_TRANSCRIBE`（Notebook [`batch_data_extraction.ipynb`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/gain-insights-from-unstructured-data/batch_data_extraction.ipynb)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/gain-insights-from-unstructured-data/batch_data_extraction.ipynb)）） |

リポジトリ版の `multimodal/` フォルダには、`car_ad_1.PNG`、`ai_transcribe.mp3`（109,547 バイト）と、1 バイトの `test.txt` も入っています（[`multimodal`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/multimodal)（[原本](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai/tree/f5ce635e7638198d72a3211518d8c03406bba670/multimodal)））。

どちらの版も、メディアファイルは S3 からではなく、利用者が Snowsight でステージにアップロードします。ZIP 内のファイル名と大きさは `unzip -l` で確認したものです。画像の中身はこのウィキでは確認していません。

<a id="voice-orders"></a>

## 7. 音声注文（MP3）

出典: [`build-voice-ai-analytics-pipeline-snowflake-cortex.md`](../../snowflake_contents/training/cortex_generative_ai/build-voice-ai-analytics-pipeline-snowflake-cortex.md)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/build-voice-ai-analytics-pipeline-snowflake-cortex/build-voice-ai-analytics-pipeline-snowflake-cortex.md)）、[`setup.sql`](../../snowflake_contents/github/common_resources/sfquickstarts/site/sfguides/src/build-voice-ai-analytics-pipeline-snowflake-cortex/assets/setup.sql)（[原本](https://github.com/Snowflake-Labs/sfquickstarts/blob/b186c148d09b971fcf99e693ffa70312b196e0ec/site/sfguides/src/build-voice-ai-analytics-pipeline-snowflake-cortex/assets/setup.sql)）

電話注文の音声を、音声 → テキスト → 構造化データの順に処理する教材です。

1. setup.sql が `TASTY_AUDIO_DB.ORDERS` に内部ステージ `AUDIO_STAGE`（ディレクトリテーブル有効）と、テーブル `ORDER_PHRASES`（`phrase_id`, `order_text`）、`CUSTOMER_ORDERS` を作り、注文フレーズを `INSERT` します（例: `(1, 'I want a hamburger with pickles and onion.')`）。教材原本は「75 seed phrases across 9 categories」と説明しています。
2. Notebook が各フレーズを Google Translate TTS API で MP3（`order_01.mp3` など）に変換し、`@AUDIO_STAGE` にアップロードします。
3. `AI_TRANSCRIBE(TO_FILE('@AUDIO_STAGE', filename))` で文字起こしし、`AI_COMPLETE` で品目・数量などを取り出して `CUSTOMER_ORDERS` に挿入します。

`CUSTOMER_ORDERS` の列: `order_id`（自動採番）, `order_timestamp`, `audio_file`, `raw_transcript`, `item_name`, `quantity`, `size`, `special_instructions`, `order_status`（既定値 `'PENDING'`）。

<a id="imdb-reviews"></a>

## 8. 映画レビュー（IMDB、Horizon 組織内共有）

出典: [`100_setup_data_model.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/100_setup_data_model.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/100_setup_data_model.sql)）、[`unstructured_data_vignette.sql`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/code/sql/reference/unstructured_data_vignette.sql)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/blob/0ba4522ade55766828420d069de1698860208ed4/code/sql/reference/unstructured_data_vignette.sql)）、[`imdb_reviews`](../../snowflake_contents/github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing/data/imdb_reviews)（[原本](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing/tree/0ba4522ade55766828420d069de1698860208ed4/data/imdb_reviews)）

Horizon 組織内共有教材は、`frostbyte_tasty_bytes` データベースに `movie_reviews` スキーマと内部ステージ `movie_stage`（ディレクトリテーブル有効）を作ります。リポジトリの `data/imdb_reviews/` には `413_0.txt` のような名前のテキストファイルが 100 個あり、中身は英語の映画・ドラマのレビューです。

参考 SQL（`reference/unstructured_data_vignette.sql`）は、`SnowflakeFile` でファイルを読む Python UDF `extract_review` を作り、`DIRECTORY(@movie_stage)` と `build_scoped_file_url` を使って `movie_reviews_v` を定義します。その後、`SNOWFLAKE.CORTEX.SUMMARIZE` と `SNOWFLAKE.CORTEX.SENTIMENT` を適用します。

このデータは Tasty Bytes の業務データではありません。同じスキーマ構成で作られる `menu_reviews` スキーマには、ソース内でオブジェクトが作られていません。

<a id="ecommerce-reviews"></a>

## 9. EC 商品レビュー（AISQL サンプル）

出典: [`README.md`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/README.md)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/README.md)）、[`customer_reviews_insight.ipynb`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/customer_reviews_insight.ipynb)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/customer_reviews_insight.ipynb)）

README は「Using an e-commerce company (Tasty Bytes) as an example」と書いていますが、データはフードトラックではなく EC の商品（例: `Toys` カテゴリの `ImagineIt Essential Action Figures`）です。

| ファイル（同梱） | データ行数 | 列 |
| --- | --- | --- |
| [`product_reviews.csv`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/data/product_reviews.csv)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/data/product_reviews.csv)） | 5,000 | `REVIEW_ID`, `PRODUCT_ID`, `CUSTOMER_ID`, `REVIEW_TEXT`, `RATING`, `REVIEW_DATE`, `PURCHASE_DATE`, `VERIFIED_PURCHASE`, `HELPFUL_VOTES` |
| [`product_catalog.csv`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/data/product_catalog.csv)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/data/product_catalog.csv)） | 200 | `PRODUCT_ID`, `PRODUCT_NAME`, `CATEGORY`, `SUBCATEGORY`, `MANUFACTURER`, `PRICE`, `RELEASE_DATE`, `REVIEW_COUNT` |
| [`customer_data.csv`](../../snowflake_contents/github/common_resources/sf-samples/samples/aisql/ecommerce_customer_review/data/customer_data.csv)（[原本](https://github.com/Snowflake-Labs/sf-samples/blob/a291149cf20f8b52fc2cd31f92b09671c415bee2/samples/aisql/ecommerce_customer_review/data/customer_data.csv)） | 1,000 | `CUSTOMER_ID`, `CUSTOMER_SEGMENT`, `JOIN_DATE`, `LIFETIME_VALUE`, `PREVIOUS_PURCHASES`, `AGE_RANGE`, `GENDER`, `PREFERRED_CATEGORY` |

行数は `wc -l` からヘッダー行を引いた値です。Notebook は同じ 3 ファイルを `s3://sfquickstarts/misc/aisql/ecommerce_customer_review/` から読み込み、`SENTIMENT`、`AI_FILTER`、`AI_AGG`、`AI_CLASSIFY`、`AI_COMPLETE` を使います（README の記載）。

<a id="excel"></a>

## 10. 価格設定シート（Excel）

出典: [`pricing_guac_roll_04_2023.xlsx`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/scripts/pricing_guac_roll_04_2023.xlsx)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/scripts/pricing_guac_roll_04_2023.xlsx)）、[`0_start_here.ipynb`](../../snowflake_contents/github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/notebooks/0_start_here.ipynb)（[原本](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit/blob/ea6f0cf42587e4b238f24a6514f8e2c1a1b89f08/notebooks/0_start_here.ipynb)）

価格最適化教材は、ブランドマネージャーが新価格を入力した Excel を想定しています。同梱ファイルは `Sheet1` の 1 シートで、列は（先頭の番号列を除き）`BRAND`, `ITEM`, `DAY_OF_WEEK`, `CURRENT_PRICE`, `NEW_PRICE`, `COMMENT` です（例: `Guac n' Roll`, `Two Taco Combo Plate`, `5 - Friday`）。Notebook はステージ `TB_PO_PROD.PUBLIC.EXCEL_S3`（`s3://sfquickstarts/frostbyte_tastybytes/excel`）から `pd.read_excel` で読み込み、デプロイしたモデルで新価格の需要を予測します。

## 関連ページ

- [半構造化データ](semi-structured-data.md)
- [中核データモデル](core-pos-model.md)
- [版による差異・矛盾](version-differences.md)
- [教材別データソース対応表](../tutorials/data-sources-by-tutorial.md)
