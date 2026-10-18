-- Step 1: Import sample data
-- In this next SQL query, we will populate sample data that is used in this template.

USE ROLE SNOWFLAKE_LEARNING_ROLE;

-- use the existing database, schema and warehouse
USE DATABASE SNOWFLAKE_LEARNING_DB;

SET schema_name = CONCAT(current_user(), '_TRANSLATE_MULTILINGUAL_CUSTOMER_REVIEWS');
USE SCHEMA IDENTIFIER($schema_name);

/*--
• file format and stage creation
--*/

CREATE OR REPLACE FILE FORMAT csv_ff 
  TYPE = 'csv';

CREATE OR REPLACE STAGE s3load
  COMMENT = 'Quickstarts S3 Stage Connection'
  URL = 's3://sfquickstarts/tastybytes-voc/'
  FILE_FORMAT = csv_ff;


/*--
• raw zone table build 
--*/

-- truck_reviews table
CREATE OR REPLACE TABLE truck_reviews
(
    order_id NUMBER(38,0),
    language VARCHAR(16777216),
    source VARCHAR(16777216),
    review VARCHAR(16777216),
    review_id NUMBER(18,0)
);

/*--
• raw zone table load 
--*/

-- truck_reviews table load
COPY INTO truck_reviews
FROM @s3load/raw_support/truck_reviews/;

-- setup completion note
SELECT 'Setup is complete' AS note;
