-- Listing: Common GRANT options --
-- <start id="code_grant_priviledges" /> --
GRANT ALL PRIVILEGES  -- <co id="co_code_grant_priviledges_1" /> --
ON DATABASE postgis_in_action to leo
WITH GRANT OPTION;

GRANT ALL PRIVILEGES ON SCHEMA world to leo;    -- <co id="co_code_grant_priviledges_2" /> --
GRANT SELECT ON geometry_columns TO public; -- <co id="co_code_grant_priviledges_3" /> --
GRANT SELECT ON spatial_ref_sys TO public;  -- <co id="co_code_grant_priviledges_4" /> --
GRANT UPDATE(proj4text,srtext)    -- <co id="co_code_grant_priviledges_5" /> --
ON spatial_ref_sys TO leo;
-- <end id="code_grant_priviledges" /> --

-- Listing: Create a simple type and use it
-- <start id="code_create_vertex_type" /> --
CREATE TYPE vertex AS   -- <co id="co_code_create_vertex_type_1" /> --
(x double precision,
y double precision);
SELECT CAST(ROW(x,y*0.02) As vertex) As myvert -- <co id="co_code_create_vertex_type_2" /> --
FROM generate_series(1,10) As x
CROSS JOIN generate_series(10,20,2) As y;

SELECT (myvert).y     -- <co id="co_code_create_vertex_type_3" /> --
FROM (
SELECT CAST(ROW(x,y*0.02) As vertex) As myvert
FROM generate_series(1,10) As x
CROSS JOIN generate_series(10,20,2) As y
) As foo;
-- <end id="code_create_vertex_type" /> --
-- #1 Create type
-- #2 Convert row to type
-- #3 Get element of typed object

-- Listing: Creating a table and a view
-- <start id="code_create_assets_poi_view" /> --
CREATE TABLE 
	assets.poi(poi_gid serial PRIMARY KEY,  -- <co id="co_code_create_assets_poi_view_1" /> --
geog geography(POINT,4326),
poi_name varchar(100),
is_active boolean DEFAULT true NOT NULL);

CREATE VIEW assets.vwpoi_active AS  -- <co id="co_code_create_assets_poi_view_2" /> --
SELECT poi_gid, geog, poi_name,is_active
  FROM assets.poi
  WHERE is_active = true;
DROP TABLE assets.poi CASCADE;   -- <co id="co_code_create_assets_poi_view_3" /> --
-- <end id="code_create_assets_poi_view" /> --
-- #1 Create table with geography field
-- #2 Create view against table
-- #3 Drop Table


-- Listing: sql square function
-- <start id="code_fnsquare" /> --
CREATE OR REPLACE FUNCTION 
 fnsquare(param_start integer, -- <co id="co_code_fnsquare_1" /> --
		param_end integer)
  RETURNS SETOF integer
AS
$$
SELECT CAST(POWER(i,2) As integer)
  FROM generate_series($1,$2) As i;
$$
language sql
IMMUTABLE;
SELECT i, fnsquare(i,i + 3) As squared_range   -- <co id="co_code_fnsquare_2" /> --
FROM generate_series(1,3) As i;

SELECT *               -- <co id="co_code_fnsquare_3" /> --
FROM fnquare(1,10) As foo;
-- <end id="code_fnsquare" /> --
-- #1 Define set returning function
-- #2 Use function in SELECT
-- #3 Use function in FROM

--informal - view --
-- <start id="code_poi_active_view" /> --
CREATE OR REPLACE VIEW assets.vwpoi_active AS
SELECT poi.poi_gid, poi.geog
 , poi.poi_name, poi.is_active
FROM poi
WHERE poi.is_active = true;
-- <end id="code_poi_active_view" /> --

-- <start id="code_poi_active_view_rule" /> --
CREATE OR REPLACE RULE "_RETURN" AS
ON SELECT TO vwpoi_active
DO INSTEAD
SELECT poi.poi_gid, poi.geog
 , poi.poi_name, poi.is_active
 FROM poi  WHERE poi.is_active = true;
-- <end id="code_poi_active_view_rule" /> --

-- Listing - Creating first and last aggregate functions
-- <start id="code_first_last_agg" /> --
CREATE OR REPLACE FUNCTION 
 first_element_state(     -- <co id="co_code_first_last_agg_1" /> --
  anyarray, anyelement)
RETURNS anyarray AS
$$
SELECT CASE WHEN array_upper($1,1) IS NULL
 THEN array_append($1,$2) ELSE $1 END;
$$
LANGUAGE 'sql' IMMUTABLE;

CREATE OR REPLACE FUNCTION first_element(anyarray) -- <co id="co_code_first_last_agg_2" /> --
RETURNS anyelement AS
$$  SELECT ($1)[1] ;$$  LANGUAGE 'sql' IMMUTABLE;

CREATE OR REPLACE FUNCTION last_element(    -- <co id="co_code_first_last_agg_3" /> --
 anyelement, anyelement)
RETURNS anyelement AS
$$  SELECT $2;  $$ LANGUAGE 'sql' IMMUTABLE;

CREATE AGGREGATE first(anyelement) (    -- <co id="co_code_first_last_agg_4" /> --
SFUNC=first_element_state,STYPE=anyarray,
FINALFUNC=first_element);

CREATE AGGREGATE last(anyelement) (   -- <co id="co_code_first_last_agg_5" /> --
SFUNC=last_element,STYPE=anyelement);
-- <end id="code_first_last_agg" /> --
--	#1 State function
--	#2 Finalfunc function
--	#3 State function
--	#4 Aggregate for first
--	#5 Aggregate for last 

-- Informal listing testing first and last --
-- <start id="code_first_last_agg_test" /> --
SELECT max(age) As oldest_age, min(age) As youngest_age,
count(*) As numinfamily, family,
first(name) As firstperson, last(name) as lastperson
FROM (SELECT 2 As age , 'jimmy' As name, 'jones' As family
UNION ALL SELECT 50 As age, 'c' As name , 'jones' As family
UNION ALL SELECT 3 As age, 'aby' As name, 'jones' As family
UNION ALL SELECT 35 As age, 'Bartholemu' As name,
  'Smith' As family
) As foo
GROUP BY family;
-- <end id="code_first_last_agg_test" /> --


-- Listing utmzone function --
-- <start id="code_utmzone" /> --
CREATE OR REPLACE 
	FUNCTION utmzone(geometry)   -- <co id="co_code_utmzone_1" /> --
    RETURNS integer AS
$$
DECLARE                -- <co id="co_code_utmzone_2" /> --
 geomgeog geometry;
 zone int;
 pref int;
BEGIN              -- <co id="co_code_utmzone_3" /> --
 geomgeog:= ST_Transform($1,4326);
 IF (ST_Y(geomgeog))&gt;0 THEN
	pref:=32600;
 ELSE
	pref:=32700;
 END IF;
 zone:=floor((ST_X(geomgeog)+180)/6)+1;
 RETURN zone+pref;
END;
$$ LANGUAGE 'plpgsql' IMMUTABLE
COST 100;
-- <end id="code_utmzone" /> --
-- #1 Function envelope
-- #2 Variables
-- #3 Function body

-- Listing geography trigger function --
-- <start id="code_geography_trigger_function" /> --
CREATE TABLE 
	poi(gid serial PRIMARY KEY,  -- <co id="co_code_geography_trigger_function_1" /> --
 geog geography(POINT,4326),
 poi_name varchar(100),
 longitude float, latitude float);

CREATE TABLE poi_log(logid SERIAL PRIMARY KEY,
 logdt timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
 logtype varchar(20), geogtable varchar(100), geog_gid integer,
 old_geog geography, new_geog geography);

CREATE OR REPLACE FUNCTION trig_set_thegeog_pt()   -- <co id="co_code_geography_trigger_function_2" /> --
RETURNS trigger AS $$
DECLARE
changed boolean := false;
oldgeog geography := NULL;
BEGIN
IF tg_op = 'INSERT' AND NEW.longitude IS NOT NULL  -- <co id="co_code_geography_trigger_function_3" /> --
  AND NEW.latitude IS NOT NULL THEN
 changed = true;
ELSIF COALESCE(NEW.longitude, -1000)    -- <co id="co_code_geography_trigger_function_4" /> --
	 != COALESCE(old.longitude, -1000)
OR COALESCE(NEW.latitude, -1000)
  != COALESCE(old.latitude, -1000) THEN
	changed = true;
END IF;
IF changed THEN
  IF NEW.longitude IS NOT NULL AND NEW.latitude IS NOT NULL THEN
	NEW.geog :=
		ST_GeographyFromText('SRID=4326;POINT('
	   || NEW.longitude || ' ' || NEW.latitude || ')');
ELSE
NEW.geog = NULL;
END IF;
INSERT INTO poi_log(logtype, geogtable, geog_gid,-- <co id="co_code_geography_trigger_function_5" /> --
	old_geog, new_geog)
VALUES(TG_OP, TG_TABLE_NAME, NEW.gid, oldgeog, NEW.geog);
END IF;
RETURN NEW;
END;
$$
LANGUAGE 'plpgsql' VOLATILE;

CREATE TRIGGER step01_trigupdpt  -- <co id="co_code_geography_trigger_function_6" /> --
BEFORE INSERT OR UPDATE
ON poi
FOR EACH ROW
EXECUTE PROCEDURE trig_set_thegeog_pt();

INSERT INTO poi(poi_name, longitude, latitude) -- <co id="co_code_geography_trigger_function_7" /> --
VALUES('My back yard', -72.1234, 41.3456);

SELECT gid, ST_AsText(geog) As wktgeog
FROM poi;

UPDATE poi SET longitude = -72.555 WHERE gid = 1;

SELECT gid, ST_AsText(geog) As wktgeog
FROM poi;
SELECT * FROM poi_log;
-- <end id="code_geography_trigger_function" /> --
-- #1 Table
-- #2 Trigger function
-- #3 Insert conditional code
-- #4 Update conditional code
-- #5 Log change
-- #6 Bind trigger to table events
-- #7 Test trigger
