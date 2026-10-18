# Snowflake コンテンツ

このディレクトリでは、Snowflake 社が提供している Tasty Bytes 関連コンテンツを整理します。

## 保存形式

- `introduction/`: 紹介・教材目次
- `training/`: トレーニング教材（分野ごとの英語フォルダ）
- `github/`: アーカイブ済み・旧教材を除いた GitHub ソース（分類ごとの英語フォルダ）
- `import_policy.json`: Coursera・アーカイブ済み・廃止教材の除外ルール
- `catalog.json`: 対象リンク85件の元データ
- `manifest.json`・`_provenance/`: 出典・取得結果・コミット・チェックサム
- [`_tools/`](_tools/README.md): 取得・目次生成の手順

GitHub ソースはアーカイブ済み・旧教材を除き、`.git` や履歴を含まない通常ファイルとして保存しています。除外したソースのパスは `_provenance/` の各リポジトリの記録に残しています。重複する参照はこのディレクトリ内の相対シンボリックリンクです。原本のライセンス等は各ソース内に保持しています。

画像・添付ファイルは取得済み原本へのローカル参照を優先し、それ以外は元の Web URL を保持します。動画・ログイン後の講座・外部データセット・Git LFS/サブモジュールの実体は含みません。教材の実行環境や Snowflake リソースは作成していません。

## 取得状況

- GitHub リポジトリ: 29/29 件取得
- 対象リンク: 取得済み 39 件、公式 Markdown 原本による代替 43 件、未取得 3 件

**公式 Markdown 原本による代替**は、公開ページそのものを取得・変換したものではありません。Web ページの直接取得はネットワーク制限により未完了です。未取得項目はリンクだけを記載し、本文を取得済みとは扱いません。

## ローカル目次

### [introduction](introduction/README.md)

- [Tasty Bytes の紹介・教材目次（日本語）](introduction/tasty-bytes-introduction-ja.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/ja/developers/guides/tasty-bytes-introduction-ja/)
- [Zero to Snowflake](introduction/zero-to-snowflake.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/zero-to-snowflake/)
- [Tasty Bytes 共通サンプルの README](introduction/tasty_bytes_common_readme.md) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/blob/main/samples/tasty_bytes/README.md)

### [training/fundamentals](training/fundamentals/README.md)

- SQL によるサンプルデータのロード・クエリ — 未取得 / [出典](https://docs.snowflake.com/ja/user-guide/tutorials/tasty-bytes-sql-load)
- [Zero to Snowflake 日本語ハンズオン](training/fundamentals/zero-to-snowflake-ja) — 取得済み / [出典](https://github.com/Snowflake-Labs/zero-to-snowflake-ja#readme)
- [コスト管理](training/fundamentals/tasty-bytes-zero-to-snowflake-cost-management.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-zero-to-snowflake-cost-management/)
- [データ変換](training/fundamentals/tasty-bytes-zero-to-snowflake-transformation.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-zero-to-snowflake-transformation/)
- [データ変換（日本語）](training/fundamentals/tasty-bytes-zero-to-snowflake-transformation-ja.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/ja/developers/guides/tasty-bytes-zero-to-snowflake-transformation-ja/)
- [半構造化データ](training/fundamentals/tasty-bytes-zero-to-snowflake-semi-structured-data.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-zero-to-snowflake-semi-structured-data/)
- [半構造化データ（日本語）](training/fundamentals/tasty-bytes-zero-to-snowflake-semi-structured-data-ja.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/ja/developers/guides/tasty-bytes-zero-to-snowflake-semi-structured-data-ja/)
- [Marketplace・外部データ連携](training/fundamentals/tasty-bytes-zero-to-snowflake-collaboration.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-zero-to-snowflake-collaboration/)
- [Marketplace・外部データ連携（日本語）](training/fundamentals/tasty-bytes-zero-to-snowflake-collaboration-ja.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/ja/developers/guides/tasty-bytes-zero-to-snowflake-collaboration-ja/)
- [地理空間分析・H3](training/fundamentals/tasty-bytes-zero-to-snowflake-geospatial.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-zero-to-snowflake-geospatial/)

### [training/data_engineering](training/data_engineering/README.md)

- [Data Engineering with Snowflake](training/data_engineering/snowflake-northstar-data-engineering.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/snowflake-northstar-data-engineering/)
- [Snowpark Python によるデータパイプライン](training/data_engineering/data-engineering-pipelines-with-snowpark-python.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/data-engineering-pipelines-with-snowpark-python/)
- [Dynamic Tables による SQL パイプライン・AI Agent](training/data_engineering/snowflake-dynamic-tables-data-pipeline.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/snowflake-dynamic-tables-data-pipeline/)
- [Dynamic Tables 総合ガイド](training/data_engineering/comprehensive-guide-to-dynamic-tables.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/comprehensive-guide-to-dynamic-tables/)
- [CoCo による取り込み・変換・配信](training/data_engineering/data-ingestion-transformation-delivery-coco.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/data-ingestion-transformation-delivery-coco/)
- [Iceberg Tables](training/data_engineering/tasty-bytes-working-with-iceberg-tables.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-working-with-iceberg-tables/)
- [Snowpark Connect for Apache Spark](training/data_engineering/intro-to-snowpark-connect-for-apache-spark.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/intro-to-snowpark-connect-for-apache-spark/)

### [training/dbt](training/dbt/README.md)

- [dbt Projects on Snowflake ハンズオン](training/dbt/dbt-projects-on-snowflake.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/dbt-projects-on-snowflake/)
- dbt Projects 入門チュートリアル — 未取得 / [出典](https://docs.snowflake.com/en/user-guide/tutorials/dbt-projects-on-snowflake-getting-started-tutorial)
- dbt Projects の CI/CD — 未取得 / [出典](https://docs.snowflake.com/en/user-guide/tutorials/dbt-projects-on-snowflake-ci-cd-tutorial)

### [training/cortex_generative_ai](training/cortex_generative_ai/README.md)

- [Cortex Analyst：Tasty Bytes デモ](training/cortex_generative_ai/cortex_analyst_tasty_bytes_readme.md) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/blob/main/samples/cortex-analyst/Cortex%20Analyst%20Tasty%20Bytes/README.md)
- [Cortex による顧客レビュー分析](training/cortex_generative_ai/customer-reviews-analytics-using-snowflake-cortex.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/customer-reviews-analytics-using-snowflake-cortex/)
- [Cortex による顧客レビューの理解](training/cortex_generative_ai/understanding-customer-reviews-using-snowflake-cortex.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/understanding-customer-reviews-using-snowflake-cortex/)
- [Cortex・Streamlit による RAG チャットボット](training/cortex_generative_ai/tasty-bytes-rag-chatbot-using-cortex-and-streamlit.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-rag-chatbot-using-cortex-and-streamlit/)
- [カスタマーサポートメールアプリ](training/cortex_generative_ai/tasty-bytes-customer-support-email-app.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-customer-support-email-app/)
- [非構造化データを使った顧客体験改善アプリ](training/cortex_generative_ai/tasty-bytes-customer-experience-app.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-customer-experience-app/)
- [Cortex Fine-Tuning による顧客体験改善](training/cortex_generative_ai/enhancing-customer-experiences-using-cortex-finetuning.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/enhancing-customer-experiences-using-cortex-finetuning/)
- [Cortex AI による一括データ抽出](training/cortex_generative_ai/gain-insights-from-unstructured-data.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/gain-insights-from-unstructured-data/)
- [音声注文処理・Cortex AI](training/cortex_generative_ai/build-voice-ai-analytics-pipeline-snowflake-cortex.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/build-voice-ai-analytics-pipeline-snowflake-cortex/)

### [training/data_science_machine_learning](training/data_science_machine_learning/README.md)

- [Snowpark 101 for Data Science](training/data_science_machine_learning/tasty-bytes-snowpark-101-for-data-science.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-snowpark-101-for-data-science/)
- [価格最適化・Notebooks・Streamlit](training/data_science_machine_learning/tasty-bytes-price-optimization-using-snowflake-notebooks-and-streamlit.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-price-optimization-using-snowflake-notebooks-and-streamlit/)
- [ML Functions：異常検知・予測](training/data_science_machine_learning/ml-forecasting-ad.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/ml-forecasting-ad/)
- [分散 PyTorch によるレコメンデーション](training/data_science_machine_learning/getting-started-with-running-distributed-pytorch-models-on-snowflake.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/getting-started-with-running-distributed-pytorch-models-on-snowflake/)
- [カスタムモデルの Model Registry 配備](training/data_science_machine_learning/deploying-custom-models-to-snowflake-model-registry.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/deploying-custom-models-to-snowflake-model-registry/)
- [VS Code 拡張によるリモート開発・ML](training/data_science_machine_learning/get-started-with-remote-development-snowflake-vscode-extension.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/get-started-with-remote-development-snowflake-vscode-extension/)

### [training/bi_analytics](training/bi_analytics/README.md)

- [Power BI：データモデル構築・分析](training/bi_analytics/end-to-end-analytics-with-snowflake-and-power-bi.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/end-to-end-analytics-with-snowflake-and-power-bi/)
- [Tableau：ビジュアル分析](training/bi_analytics/visual-analytics-powered-by-snowflake-and-tableau.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/visual-analytics-powered-by-snowflake-and-tableau/)
- [Hex・Cortex による顧客レビュー分析](training/bi_analytics/analyzing-customer-reviews-using-hex-and-snowflake-cortex.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/analyzing-customer-reviews-using-hex-and-snowflake-cortex/)
- [Sigma による予測モデル](training/bi_analytics/partner-snowflake-predictive-model-using-sigma.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/partner-snowflake-predictive-model-using-sigma/)

### [training/application_development](training/application_development/README.md)

- [Node.js・React によるデータアプリ](training/application_development/build-a-data-app-with-snowflake.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/build-a-data-app-with-snowflake/)
- [Snowpark Container Services へのアプリ配備](training/application_development/build-a-data-app-and-run-it-on-snowpark-container-services.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/build-a-data-app-and-run-it-on-snowpark-container-services/)
- [React Native・SQL API](training/application_development/developing-tasty-bytes-react-native-application-with-snowflake-sql-api.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/developing-tasty-bytes-react-native-application-with-snowflake-sql-api/)

### [training/governance_sharing](training/governance_sharing/README.md)

- [Horizon によるガバナンス](training/governance_sharing/tasty-bytes-zero-to-snowflake-governance-with-horizon.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/tasty-bytes-zero-to-snowflake-governance-with-horizon/)
- [Private Listings によるクロスクラウド共有](training/governance_sharing/horizon-intra-org-sharing.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/horizon-intra-org-sharing/)
- [Internal Marketplace による社内共有](training/governance_sharing/internal-marketplace-intra-org-sharing.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/internal-marketplace-intra-org-sharing/)
- [Microsoft Purview 連携](training/governance_sharing/getting-started-with-microsoft-purview-and-snowflake.md) — 公式 Markdown 原本（代替） / [出典](https://www.snowflake.com/en/developers/guides/getting-started-with-microsoft-purview-and-snowflake/)

### [github/common_resources](github/common_resources/README.md)

- [Snowflake-Labs/sfquickstarts](github/common_resources/sfquickstarts) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfquickstarts)
- [Snowflake-Labs/sf-samples](github/common_resources/sf-samples) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples)
- [Snowflake-Labs/snowflake-demo-notebooks](github/common_resources/snowflake-demo-notebooks) — 取得済み / [出典](https://github.com/Snowflake-Labs/snowflake-demo-notebooks)
- [Snowflake-Labs/sfguides](github/common_resources/sfguides) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguides)
- [Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake](github/common_resources/sfguide-getting-started-from-zero-to-snowflake) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-getting-started-from-zero-to-snowflake)
- [Snowflake-Labs/zero-to-snowflake-ja](github/common_resources/zero-to-snowflake-ja) — 取得済み / [出典](https://github.com/Snowflake-Labs/zero-to-snowflake-ja)

### [github/data_engineering_dbt](github/data_engineering_dbt/README.md)

- [modern-data-engineering-snowflake](github/data_engineering_dbt/modern-data-engineering-snowflake) — 取得済み / [出典](https://github.com/Snowflake-Labs/modern-data-engineering-snowflake)
- [sfguide-snowflake-northstar-data-engineering](github/data_engineering_dbt/sfguide-snowflake-northstar-data-engineering) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-snowflake-northstar-data-engineering)
- [sfguide-data-engineering-with-snowpark-python](github/data_engineering_dbt/sfguide-data-engineering-with-snowpark-python) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-snowpark-python)
- [sfguide-declarative-pipelines-dynamic-tables](github/data_engineering_dbt/sfguide-declarative-pipelines-dynamic-tables) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-declarative-pipelines-dynamic-tables)
- [getting-started-with-dbt-on-snowflake](github/data_engineering_dbt/getting-started-with-dbt-on-snowflake) — 取得済み / [出典](https://github.com/Snowflake-Labs/getting-started-with-dbt-on-snowflake)
- [sfguide-scai-e2e-ssis-migration](github/data_engineering_dbt/sfguide-scai-e2e-ssis-migration) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-scai-e2e-ssis-migration)
- [snowflake-dcm-projects](github/data_engineering_dbt/snowflake-dcm-projects) — 取得済み / [出典](https://github.com/Snowflake-Labs/snowflake-dcm-projects)

### [github/cortex_ai_machine_learning](github/cortex_ai_machine_learning/README.md)

- [sfguide-tasty-bytes-enhancing-customer-experience](github/cortex_ai_machine_learning/sfguide-tasty-bytes-enhancing-customer-experience) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-enhancing-customer-experience)
- [sfguide-customer-reviews-analytics-using-snowflake-cortex](github/cortex_ai_machine_learning/sfguide-customer-reviews-analytics-using-snowflake-cortex) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-customer-reviews-analytics-using-snowflake-cortex)
- [sfguide-gaining-insights-from-unstructured-data-with-cortex-ai](github/cortex_ai_machine_learning/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-gaining-insights-from-unstructured-data-with-cortex-ai)
- [sfguide-enhancing-customer-experiences-using-cortex-finetuning](github/cortex_ai_machine_learning/sfguide-enhancing-customer-experiences-using-cortex-finetuning) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-enhancing-customer-experiences-using-cortex-finetuning)
- [translate-customer-reviews-template](github/cortex_ai_machine_learning/translate-customer-reviews-template) — 取得済み / [出典](https://github.com/Snowflake-Labs/translate-customer-reviews-template)
- [sfguide-tasty-bytes-snowpark-101-for-data-science](github/cortex_ai_machine_learning/sfguide-tasty-bytes-snowpark-101-for-data-science) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-snowpark-101-for-data-science)
- [sfguide-price-optimization-using-snowflake-notebooks-and-streamlit](github/cortex_ai_machine_learning/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-price-optimization-using-snowflake-notebooks-and-streamlit)
- [sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake](github/cortex_ai_machine_learning/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-getting-started-with-running-distributed-pytorch-models-on-snowflake)
- [sfguide-deploying-custom-models-snowflake-model-registry](github/cortex_ai_machine_learning/sfguide-deploying-custom-models-snowflake-model-registry) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-deploying-custom-models-snowflake-model-registry)
- [sfguide-getting-started-with-remote-development-vscode-extension](github/cortex_ai_machine_learning/sfguide-getting-started-with-remote-development-vscode-extension) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-getting-started-with-remote-development-vscode-extension)

### [github/bi_applications_sharing](github/bi_applications_sharing/README.md)

- [sfguide-end-to-end-analytics-with-snowflake-and-power-bi](github/bi_applications_sharing/sfguide-end-to-end-analytics-with-snowflake-and-power-bi) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-end-to-end-analytics-with-snowflake-and-power-bi)
- [visual_analytics_powered_by_snowflake_and_tableau](github/bi_applications_sharing/visual_analytics_powered_by_snowflake_and_tableau) — 取得済み / [出典](https://github.com/Snowflake-Labs/visual_analytics_powered_by_snowflake_and_tableau)
- [sfguide-tasty-bytes-zero-to-app](github/bi_applications_sharing/sfguide-tasty-bytes-zero-to-app) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-zero-to-app)
- [sfguide-tasty-bytes-zero-to-app-with-spcs](github/bi_applications_sharing/sfguide-tasty-bytes-zero-to-app-with-spcs) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-tasty-bytes-zero-to-app-with-spcs)
- [sfguide-horizon-intra-organization-sharing](github/bi_applications_sharing/sfguide-horizon-intra-organization-sharing) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-horizon-intra-organization-sharing)
- [sfguide-intra-company-data-sharing-with-the-snowflake-internal-marketplace](github/bi_applications_sharing/sfguide-intra-company-data-sharing-with-the-snowflake-internal-marketplace) — 取得済み / [出典](https://github.com/Snowflake-Labs/sfguide-intra-company-data-sharing-with-the-snowflake-internal-marketplace)

### [github/tasty_bytes_samples](github/tasty_bytes_samples/README.md)

- [Tasty Bytes 共通 SQL](github/tasty_bytes_samples/tasty_bytes) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/tasty_bytes)
- [FY25 Zero to Snowflake](github/tasty_bytes_samples/FY25_Zero_To_Snowflake) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/tasty_bytes/FY25_Zero_To_Snowflake)
- [Cortex Analyst：Notebook・Streamlit・セマンティックモデル](github/tasty_bytes_samples/Cortex%20Analyst%20Tasty%20Bytes) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/cortex-analyst/Cortex%20Analyst%20Tasty%20Bytes)
- [開発者・データサイエンティスト・データエンジニア向け入門](github/tasty_bytes_samples/intro-to-snowflake-for-devs-data-scientists-data-engineers) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/intro-to-snowflake-for-devs-data-scientists-data-engineers)
- [AISQL による顧客レビュー分析](github/tasty_bytes_samples/ecommerce_customer_review) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/aisql/ecommerce_customer_review)
- [Snowpark Connect](github/tasty_bytes_samples/snowpark_connect) — 取得済み / [出典](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/snowpark_connect)
- [DCM：Tasty Bytes サンプル](github/tasty_bytes_samples/dcm-full-demo-project) — 取得済み / [出典](https://github.com/Snowflake-Labs/snowflake-dcm-projects/tree/main/sample-projects/dcm-full-demo-project)
