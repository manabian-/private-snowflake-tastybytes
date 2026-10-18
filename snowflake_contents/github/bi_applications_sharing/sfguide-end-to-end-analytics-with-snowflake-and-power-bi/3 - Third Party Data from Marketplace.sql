/*-------------------------------------------------

--SECTION 3 - THIRD PARTY DATA FROM SNOWFLAKE MARKETPLACE

-------------------------------------------------*/

/*Dependent on getting the SafeGraph: frostbyte listing from marketplace */

/* set the worksheet context */
use role tb_dev;
use schema safegraph_frostbyte.public;
use warehouse tb_dev_wh;


/* sample the dataset */
select *
from frostbyte_tb_safegraph_s;

/* view location counts by country */
select 
    country,
    count(*)
from frostbyte_tb_safegraph_s
group by all;

/* issue a cross-database join to the raw_pos.location table and try joining on placekey */
select
    l.location_id,
    l.location,
    l.city as location_city,
    l.country as location_country,
    l.iso_country_code as location_country_iso,
    sg.top_category as location_category,
    sg.sub_category as location_subcategory,
    sg.latitude as location_latitude,
    sg.longitude as location_longitude,
    sg.street_address as location_street_address,
    sg.postal_code as location_postal_code
from tb_101.raw_pos.location l
left join safegraph_frostbyte.public.frostbyte_tb_safegraph_s sg
    ON sg.placekey = l.placekey;


/* create a copy of the shared SafeGraph data in the raw_pos schema so 
it can be included in our Dynamic Table definition in the next section */
create or replace table tb_101.raw_pos.safegraph_frostbyte_location
as
select *
from safegraph_frostbyte.public.frostbyte_tb_safegraph_s;