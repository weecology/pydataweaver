-- Listing create schemaas to partition data
-- <start id="code_regional_schemas"/> --
CREATE SCHEMA us; 
CREATE SCHEMA canada; 
CREATE SCHEMA staging; 
ALTER DATABASE postgis_in_action 
 SET search_path=public,"$user",us,canada;
-- <end id="code_regional_schemas"/> --

-- <start id="code_query_hstore_tags"/> --
SELECT name, array_to_string(akeys(tags), '|') As keys 
  ,tags -> 'cycleway' As cycleway
FROM planet_osm_line 
WHERE tags ? 'cycleway' ;
-- <end id="code_query_hstore_tags"/> --

-- <start id="code_expand_osm_tags"/> --
SELECT osm_id, (foo.e).key, (foo.e).value
INTO osm_key_values
FROM 
 (SELECT osm_id, each(tags) As e 
  FROM planet_osm_line ) As foo ;
-- <end id="code_expand_osm_tags"/> --


--<start id="code_list_gdaldrivers"/> --
SELECT short_name, long_name
FROM ST_GdalDrivers()
ORDER BY short_name;
--<end id="code_list_gdaldrivers"/> --

--<start id="code_export_osm_roads_png"/> --
SELECT ST_AsPNG( --<co id="co_code_export_osm_roads_png_1"/>
	ST_AsRaster( --<co id="co_code_export_osm_roads_png_2"/>
		ST_Union(way), --<co id="co_code_export_osm_roads_png_3"/>
		400,400, --<co id="co_code_export_osm_roads_png_4"/>
		ARRAY['8BUI','8BUI','8BUI'], --<co id="co_code_export_osm_roads_png_5"/>
		ARRAY[200,0,0], --<co id="co_code_export_osm_roads_png_6"/>
		ARRAY[0,0,0] --<co id="co_code_export_osm_roads_png_7"/>
	)
)
FROM planet_osm_roads;
--<end id="code_export_osm_roads_png"/> --
-- #1 postgis raster to PNG
-- #2 geometry to postgis raster
-- #3 union roads
-- #4 400x400 pixels 
-- #5 3 bands
-- #6 RGB array (very red)
-- #7 nodata value 0,0,0 pixel