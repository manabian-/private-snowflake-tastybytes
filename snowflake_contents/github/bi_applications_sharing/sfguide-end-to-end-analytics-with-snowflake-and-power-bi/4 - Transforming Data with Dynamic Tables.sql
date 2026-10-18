/*-------------------------------------------------

--SECTION 4 - STAR SCHEMAS & DYNAMIC TABLES

-------------------------------------------------*/

/* set worksheet context */
use role sysadmin;
use schema tb_101.powerbi;
use warehouse tb_dev_wh;


/*-------------------------------------------------

--CREATE STATIC DATE & TIME DIMENSIONS

-------------------------------------------------*/

/*
    --let's temporarily scale up our tb_de_wh to quickly create the fact tables and perform the initital data load
    --we'll scale this back down at the end
    --notice how Snowflake's elastic compute is available instantly!
*/
alter warehouse tb_de_wh set warehouse_size = '4x-large';


/*--------------------------------------------
--dim_date
--simple date dimension script sourced from - https://community.snowflake.com/s/question/0D50Z00008MprP2SAJ/snowflake-how-to-build-a-calendar-dim-table
--Can also easily source a free date dimension sourced from Marketplace providers
--------------------------------------------*/

/* set the date range to build date dimension */
set min_date = to_date('2018-01-01');
set max_date = to_date('2024-12-31');
set days = (select $max_date - $min_date);

create or replace table tb_101.powerbi.dim_date
(
   date_id int,
   date date,
   year string, 
   month smallint,  
   month_name string,  
   day_of_month smallint,  
   day_of_week  smallint,  
   weekday string,
   week_of_year smallint,  
   day_of_year  smallint,
   weekend_flag boolean
)
as
  with dates as 
  (
    select dateadd(day, SEQ4(), $min_date) as my_date
    from TABLE(generator(rowcount=> $days))  -- Number of days after reference date in previous line
  )
  select 
        to_number(replace(to_varchar(my_date), '-')),
        my_date,
        year(my_date),
        month(my_date),
        monthname(my_date),
        day(my_date),
        dayofweek(my_date),
        dayname(my_date),
        weekofyear(my_date),
        dayofyear(my_date),
        case when dayofweek(my_date) in (0,6) then 1 else 0 end as weekend_flag
    from dates;



/*--------------------------------------------
--dim_time
--simple time dimension (hour:min:seconds) script 
--------------------------------------------*/

--set the date range to build date dimension
set min_time = to_time('00:00:00');
set max_time = to_time('11:59:59');
set seconds = 86400;

create or replace table tb_101.powerbi.dim_time
(
  time_id int,
  time time,
  hour smallint,   
  minute smallint,  
  second smallint,   
  am_or_pm string,   
  hour_am_pm  string  
)
as
  with seconds as 
  (
    select timeadd(second, SEQ4(), $min_time) as my_time
    from table(generator(rowcount=> $seconds))  -- Number of seconds in a day
  )
  select
         to_number(left(to_varchar(my_time), 2) || substr(to_varchar(my_time),4, 2) || right(to_varchar(my_time), 2)),
         my_time,
         hour(my_time),
         minute(my_time),
         second(my_time),
         case
            when hour(my_time) < 12 THEN 'AM'
            else 'PM'
         end as am_or_pm,
         case
             when hour(my_time) = 0 THEN '12AM'
             when hour(my_time) < 12 THEN hour(my_time) || 'AM'
             when hour(my_time) = 12 THEN '12PM'
             when hour(my_time) = 13 THEN '1PM'
             when hour(my_time) = 14 THEN '2PM'
             when hour(my_time) = 15 THEN '3PM'
             when hour(my_time) = 16 THEN '4PM'
             when hour(my_time) = 17 THEN '5PM'
             when hour(my_time) = 18 THEN '6PM'
             when hour(my_time) = 19 THEN '7PM'
             when hour(my_time) = 20 THEN '8PM'
             when hour(my_time) = 21 THEN '9PM'
             when hour(my_time) = 22 THEN '10PM'
             when hour(my_time) = 23 THEN '11PM'
         end as Hour_am_pm
    from seconds;  


/*-------------------------------------------------

--DYNAMIC TABLES FOR OUR BUSINESS DIMENSIONS AND FACTS

-------------------------------------------------*/

/* dim_truck */
create or replace dynamic table dt_dim_truck
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = incremental
  initialize = on_create
  as
    select distinct
        t.truck_id,
        t.franchise_id,
        m.truck_brand_name,
        t.primary_city as truck_city,
        t.region as truck_region,
        t.iso_region as truck_region_iso,
        t.country as truck_country,
        t.iso_country_code as truck_country_iso,
        t.franchise_flag,
        year as truck_year,
        (2023 - year) as truck_age,
        replace(t.make, 'Ford_', 'Ford') as truck_make,
        t.model as truck_model,
        t.ev_flag,
        t.truck_opening_date
    from tb_101.raw_pos.truck t
    join tb_101.raw_pos.menu m on m.menu_type_id = t.menu_type_id;

  
/* dim_franchise */
create or replace dynamic table dt_dim_franchise
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = incremental
  initialize = on_create
  as
  with remove_duplicates as
  (
    select distinct
        f.franchise_id,
        f.first_name as franchise_first_name,
        f.last_name as franchise_last_name,
        f.city as franchise_city,
        f.country as franchise_country,
        f.e_mail as franchise_email,
        f.phone_number as franchise_phone_number,
        row_number()over(partition by franchise_id order by franchise_city ) as row_num
    from tb_101.raw_pos.franchise f
    )

    select *
    from remove_duplicates
    where row_num = 1;


/* dim_menu_item */
create or replace dynamic table dt_dim_menu_item
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = incremental
  initialize = on_create
  as
     select 
        menu_item_id,
        menu_type_id,
        menu_type,
        item_category as menu_item_category,
        item_subcategory as menu_item_subcategory,
        menu_item_name,
        cost_of_goods_usd as cogs_usd,
        sale_price_usd,
        menu_item_health_metrics_obj:menu_item_health_metrics[0].ingredients as ingredients,
        menu_item_health_metrics_obj:menu_item_health_metrics[0].is_dairy_free_flag as is_dairy_free_flag,
        menu_item_health_metrics_obj:menu_item_health_metrics[0].is_gluten_free_flag as is_gluten_free_flag,
        menu_item_health_metrics_obj:menu_item_health_metrics[0].is_healthy_flag as is_healthy_flag,
        menu_item_health_metrics_obj:menu_item_health_metrics[0].is_nut_free_flag as is_nut_free_flag
    from tb_101.raw_pos.menu m;


/* dim_location */
create or replace dynamic table dt_dim_location
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = incremental
  initialize = on_create
  as
    select
        l.location_id,
        l.location,
        l.city as location_city,
        case
            when l.country in ('England', 'France', 'Germany', 'Poland', 'Spain', 'Sweden') then 'EMEA'
            when l.country in ('Canada', 'Mexico', 'United States') then 'North America'
            when l.country in ('Australia', 'India', 'Japan', 'South Korea') then 'APAC'
            else 'Other'
        end as location_region,
        l.country as location_country,
        l.iso_country_code as location_country_iso,
/*
    Commented out the SafeGraph data points as not every user following this guide
    will have the ability to leverage the Snowflake Marketplace and create new
    shared databases if they are working out of their organization's Snowflake account
  
        sg.top_category as location_category,
        sg.sub_category as location_subcategory,
        sg.latitude as location_latitude,
        sg.longitude as location_longitude,
        sg.street_address as location_street_address,
        sg.postal_code as location_postal_code
*/
    from tb_101.raw_pos.location l;
/*    left join tb_101.raw_pos.safegraph_frostbyte_location sg on sg.placekey = l.placekey; */


/* dim_customer */
create or replace dynamic table dt_dim_customer
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = incremental
  initialize = on_create
  as
    select
        cl.customer_id,
        cl.first_name as customer_first_name,
        cl.last_name as customer_last_name,
        cl.first_name || ' ' || cl.last_name as customer_full_name,
        cl.last_name || ', ' || cl.first_name as customer_last_first_name,
        cl.city as customer_city,
        cl.country as customer_country,
        cl.postal_code as customer_postal_code,
        cl.preferred_language as customer_preferred_language,
        cl.gender as customer_gender,
        cl.favourite_brand as customer_favorite_band,
        cl.marital_status as customer_marital_status,
        cl.children_count as customer_children_count,
        cl.sign_up_date as customer_signup_date,
        cl.birthday_date as customer_dob,
        cl.e_mail as customer_email,
        cl.phone_number as customer_phone_number
    from tb_101.raw_customer.customer_loyalty cl;


/* fact_order_detail */
create or replace dynamic table dt_fact_order_detail
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = incremental
  initialize = on_create
  as

    with natural_keys
    as
    (
        select 
        od.order_id,
        od.order_detail_id,
        oh.truck_id,
        t.franchise_id,
        cast(oh.location_id as int) as location_id,
        od.menu_item_id,
        to_date(oh.order_ts) as date_id,
        to_time(oh.order_ts) as time_id,
        oh.customer_id,
        od.quantity,
        od.unit_price,
        od.price as line_total
    from tb_101.raw_pos.order_detail od
    join tb_101.raw_pos.order_header oh on oh.order_id = od.order_id
    join tb_101.raw_pos.truck t on t.truck_id = oh.truck_id
    )


    select
        nk.order_id,
        nk.order_detail_id,
        dt.truck_id, 
        df.franchise_id, 
        dl.location_id, 
        dmi.menu_item_id, 
        dc.customer_id, 
        dd.date_id, 
        ti.time_id, 
        --measures
        nk.quantity,
        nk.unit_price,
        nk.line_total
    from natural_keys nk
    --dimension joins to enforce downstream dependencies in DT graph
    join powerbi.dt_dim_truck dt on dt.truck_id = nk.truck_id and dt.franchise_id = nk.franchise_id
    join powerbi.dt_dim_franchise df on df.franchise_id = nk.franchise_id
    join powerbi.dt_dim_location dl on dl.location_id = nk.location_id
    join powerbi.dt_dim_menu_item dmi on dmi.menu_item_id = nk.menu_item_id
    join powerbi.dim_date dd on dd.date = nk.date_id
    join powerbi.dim_time ti on ti.time = nk.time_id
    left join powerbi.dt_dim_customer dc on dc.customer_id = nk.customer_id;


  
/* fact_order_header */
create or replace dynamic table dt_fact_order_header
  target_lag = 'DOWNSTREAM'
  warehouse = tb_de_wh
  refresh_mode = full
  initialize = on_create
  as
    select
        order_id, 
        truck_id,
        franchise_id,
        location_id,
        customer_id,
        date_id,
        time_id,
        count(order_detail_id) as order_line_count,
        sum(quantity) as order_qty,
        sum(line_total) as order_total
    from dt_fact_order_detail
    group by 
        order_id, 
        truck_id,
        franchise_id,
        location_id,
        customer_id,
        date_id,
        time_id;


/* fact_order_agg */
create or replace dynamic table dt_fact_order_agg
  target_lag = '1 hour'
  warehouse = tb_de_wh
  refresh_mode = full
  initialize = on_create
  as
    select 
        truck_id,
        franchise_id,
        location_id,
        customer_id,
        date_id,
        count(order_id) as order_count, 
        sum(order_line_count) as order_line_count,
        sum(order_qty) as order_qty,
        sum(order_total) as order_total 
    from dt_fact_order_header
    group by
        truck_id,
        franchise_id,
        location_id,
        customer_id,
        date_id;


/* scale the data engineering warehouse back down */
alter warehouse tb_de_wh set warehouse_size = 'medium';
alter warehouse tb_de_wh suspend;