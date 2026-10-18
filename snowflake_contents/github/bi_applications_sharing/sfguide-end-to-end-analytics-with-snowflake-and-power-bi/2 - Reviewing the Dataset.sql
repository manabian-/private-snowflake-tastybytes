/*-------------------------------------------------

--SECTION 2 - REVIEWING THE DATASET

-------------------------------------------------*/

/* set database schema, role, and warehouse context */
use role sysadmin;
use database tb_101;
use schema raw_pos;
use warehouse tb_dev_wh;

/*-------------------------------------------------

--BASIC DATA PROFILING

-------------------------------------------------*/

/* Review the volume of data in each table */
show tables in schema tb_101.raw_pos;


/* Sample the data */
select *
from order_header
where customer_id is not null
limit 1000;


/**** Identify if a table contains duplicate records ****/
with dupes as
(
    -- Find franchise_ids that appear more than once
    select franchise_id, count(*)
    from tb_101.raw_pos.franchise
    group by franchise_id
    having count(*) > 1
)
-- Select all records from the franchise table that have duplicate franchise_ids
select * 
from tb_101.raw_pos.franchise f 
where exists (select 1 from dupes d where d.franchise_id = f.franchise_id);





/*-------------------------------------------------

--CREATE POWERBI SCHEMA AND WAREHOUSE

-------------------------------------------------*/

/*
Now, that we've profiled the dataset, let's create a new schema to store our 
Dynamic Tables that will be queried by our Power BI semantic model.
*/
use role sysadmin;

create or replace schema tb_101.powerbi;

use schema tb_101.powerbi;

/*
-create a warehouse for Power BI if it doesn't already exist
-we won't use this warehouse just yet, but it will be the warehouse used within our Power BI semantic model
*/
create or replace warehouse tb_powerbi_wh
warehouse_size = 'MEDIUM'
max_cluster_count = 1
min_cluster_count = 1
auto_suspend = 300
initially_suspended = true
resource_constraint = standard_gen_2 --omit this parameter if Gen2 warehouses are unavailable in your region; Gen1 will work just fine too
comment = 'Warehouse used for the TB Power BI DQ semantic model';


/* ensure we're still using our tb_dev_wh */
use warehouse tb_dev_wh;



-------------------------------------------------

--CREATE TEST USER, ROLES, AND GRANT PPRIVILEGES

-------------------------------------------------
/*
Create a new user called tb_bi_analyst that will be used to connect to Snowflake from Power BI

Use a strong, randomly generated password
*/
use role useradmin;

create or replace user tb_bi_analyst
  default_role = 'tb_bi_analyst_global'
  type = 'PERSON';

alter user if exists tb_bi_analyst 
add programmatic access token tb_bi_analyst_PAT
days_to_expiry = 365;

/* 
Blog on whitelisting Power BI IP addresses in a Snowflake network rule
https://medium.com/@daria.rostovtseva/how-to-automate-power-bi-ip-allowlisting-in-snowflake-4cfa8e1769e9

sample script for applying a user-level network policy:
use role accountadmin;
alter user tb_bi_analyst set network_policy = 'BI_ANALYST_NETWORK_POLICY';
*/


/* create testing roles */
use role securityadmin;

create or replace role tb_bi_analyst_global;
create or replace role tb_bi_analyst_emea;
create or replace role tb_bi_analyst_na;
create or replace role tb_bi_analyst_apac;

/* grant the roles to the user we created above */
grant role tb_bi_analyst_global to user tb_bi_analyst;
grant role tb_bi_analyst_emea to user tb_bi_analyst;
grant role tb_bi_analyst_na to user tb_bi_analyst;
grant role tb_bi_analyst_apac to user tb_bi_analyst;

/* assign roles to sysadmin */ 
grant role tb_bi_analyst_global to role sysadmin;
grant role tb_bi_analyst_emea to role sysadmin;
grant role tb_bi_analyst_na to role sysadmin;
grant role tb_bi_analyst_apac to role sysadmin;

/* grant permissions to database */
grant usage on database tb_101 to role tb_bi_analyst_global;
grant usage on database tb_101 to role tb_bi_analyst_emea;
grant usage on database tb_101 to role tb_bi_analyst_na;
grant usage on database tb_101 to role tb_bi_analyst_apac;

/* next, we'll add permissions to our powerbi schema */
grant all on schema tb_101.powerbi to role tb_data_engineer;
grant all on schema tb_101.powerbi to role tb_bi_analyst_global;
grant all on schema tb_101.powerbi to role tb_bi_analyst_emea;
grant all on schema tb_101.powerbi to role tb_bi_analyst_na;
grant all on schema tb_101.powerbi to role tb_bi_analyst_apac;

/* next, we'll add future grants so our analyst roles have access to any newly created objects */
grant all on future tables in schema tb_101.powerbi to role tb_data_engineer;
grant all on future tables in schema tb_101.powerbi to role tb_bi_analyst_global;
grant all on future tables in schema tb_101.powerbi to role tb_bi_analyst_emea;
grant all on future tables in schema tb_101.powerbi to role tb_bi_analyst_na;
grant all on future tables in schema tb_101.powerbi to role tb_bi_analyst_apac;

/* future grants for Dynamic Tables */
grant all on future dynamic tables in schema tb_101.powerbi to role tb_data_engineer;
grant all on future dynamic tables in schema tb_101.powerbi to role tb_bi_analyst_global;
grant all on future dynamic tables in schema tb_101.powerbi to role tb_bi_analyst_emea;
grant all on future dynamic tables in schema tb_101.powerbi to role tb_bi_analyst_na;
grant all on future dynamic tables in schema tb_101.powerbi to role tb_bi_analyst_apac;

/* lastly, grant usage on the tb_powerbi_wh and the tb_dev_wh so they can be used by each role */
grant usage on warehouse tb_powerbi_wh to role tb_bi_analyst_global;
grant usage on warehouse tb_powerbi_wh to role tb_bi_analyst_emea;
grant usage on warehouse tb_powerbi_wh to role tb_bi_analyst_na;
grant usage on warehouse tb_powerbi_wh to role tb_bi_analyst_apac;

grant usage on warehouse tb_dev_wh to role tb_bi_analyst_global;
grant usage on warehouse tb_dev_wh to role tb_bi_analyst_emea;
grant usage on warehouse tb_dev_wh to role tb_bi_analyst_na;
grant usage on warehouse tb_dev_wh to role tb_bi_analyst_apac;