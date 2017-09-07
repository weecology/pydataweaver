-- creating a new spatial database --
-- start id="code_create_template_database_pre91"  --
CREATE DATABASE template_postgis_21        -- <co id="co_code_create_template_database_pre91_1a" /> --
 WITH TEMPLATE = template1 ENCODING = 'UTF8'; -- <co id="co_code_create_template_database_pre91_1b" /> --
\c template_postgis_20; -- <co id="co_code_create_template_database_pre91_1c" /> --
\cd /usr/share/pgsql/contrib/postgis-2.1  -- <co id="co_code_create_template_database_pre91_2" /> --
\i postgis.sql;    -- <co id="co_code_create_template_database_pre91_3a" /> --
\i spatial_ref_sys.sql;  -- <co id="co_code_create_template_database_pre91_3b" /> --
\i postgis_comments.sql;  -- <co id="co_code_create_template_database_pre91_4" /> --

\i rtpostgis.sql; -- <co id="co_code_create_template_database_pre91_5" /> --
\i raster_comments.sql;

-- for topology support --
\i topology.sql   -- <co id="co_code_create_template_database_pre91_6" /> --
\i topology_comments.sql
UPDATE pg_database SET datistemplate = TRUE  -- <co id="co_code_create_template_database_pre91_7" /> --
 WHERE datname = 'template_postgis_21';
GRANT ALL ON geometry_columns TO PUBLIC;
GRANT ALL ON spatial_ref_sys TO PUBLIC;
\q
-- end id="code_create_template_database_pre91"  --
