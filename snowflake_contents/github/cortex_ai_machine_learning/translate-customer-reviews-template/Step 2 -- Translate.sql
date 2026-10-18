-- Using Cortex Translate in SQL
-- Translate runs fully in SQL by calling SNOWFLAKE.CORTEX.TRANSLATE. In this query, we are translating non-English reviews directly into a new TRANSLATED_REVIEW column.

/* 
Make sure we are using the correct roles! 
*/ 
USE ROLE SNOWFLAKE_LEARNING_ROLE;

-- use the existing database, schema and warehouse
USE DATABASE SNOWFLAKE_LEARNING_DB;

SET schema_name = CONCAT(current_user(), '_TRANSLATE_MULTILINGUAL_CUSTOMER_REVIEWS');
USE SCHEMA IDENTIFIER($schema_name);

/* 
Do the translation!
*/

SELECT 
  REVIEW,
  LANGUAGE,
  CASE 
    WHEN LANGUAGE != 'en' THEN SNOWFLAKE.CORTEX.TRANSLATE(REVIEW, LANGUAGE, 'en')
    ELSE REVIEW
  END AS TRANSLATED_REVIEW
FROM TRUCK_REVIEWS
WHERE LANGUAGE != 'en'
LIMIT 20;
