-- <start id="code_get_rast_tile" > --
CREATE OR REPLACE FUNCTION ch17.get_rast_tile(
    param_format text,
    param_width integer,
    param_height integer,
    param_srid integer,
    param_bbox text, 
    param_schema text, 
    param_table text
) 
RETURNS bytea AS
$$
DECLARE 
    var_sql text; var_result raster; var_srid integer; 
    var_env geometry; var_erast raster;
BEGIN
    EXECUTE 
        'SELECT ST_MakeEnvelope(' || array_to_string(('{' || 
        param_bbox || '}')::float8[],',') || ',' || param_srid ||
        ')' 
    INTO var_env; -- <co id="co_code_get_rast_tile_1a"/>
    var_sql := 
        'SELECT srid, ST_AsRaster($4,$5,$6,pixel_types,nodata_values,nodata_values) As erast 
        FROM raster_columns 
        WHERE r_table_schema = $1 AND r_table_name = $2 AND r_raster_column=$3'; 
    EXECUTE var_sql INTO var_srid, var_erast 
    USING param_schema, param_table, 'rast', var_env, param_width, param_height; -- <co id="co_code_get_rast_tile_2a"/>
  
    var_sql := 
        'WITH r AS (SELECT ST_Clip(rast,' || 
        CASE 
            WHEN var_srid = param_srid THEN '$3' 
            ELSE 'ST_Transform($3,$2)' 
        END || ') As rast FROM  ' || 
        quote_ident(param_schema) || '.' || 
        quote_ident(param_table) || ' 
        WHERE ST_Intersects(rast,' || 
        CASE 
            WHEN var_srid = param_srid THEN '$3' 
            ELSE 'ST_Transform($3,$2)' 
        END || ') limit 15) 
        SELECT ST_Clip(ST_Union(rast), $3) As rast 
        FROM (SELECT ST_Resample(' || 
        CASE 
            WHEN var_srid = param_srid THEN 'rast' 
            ELSE 'ST_Transform(rast,$1)' 
        END || 
        ',$6,true,''CubicSpline'') As rast FROM r) As final'; -- <co id="co_code_get_rast_tile_3a"/>
  
    EXECUTE var_sql INTO var_result 

    USING 
        param_srid, 
        var_srid, 
        var_env, 
        param_width, 
        param_height, 
        var_erast; -- <co id="co_code_get_rast_tile_4a"/>
  
    IF var_result IS NULL THEN
        var_result := var_erast;
    End If;
  
    RETURN 
        CASE 
            WHEN param_format ILIKE 'jp' THEN ST_AsJPEG(var_result) 
            ELSE ST_AsPNG(var_result) 
        END;
END;
$$
LANGUAGE plpgsql IMMUTABLE;
-- <end id="code_get_rast_tile" > --

-- <start id="code_get_features" > --
CREATE OR REPLACE FUNCTION ch17.get_features(
    param_geom json,
    param_table text,
    param_props text,
    param_limit integer DEFAULT 10
) 
RETURNS json AS 
$$
DECLARE 
    var_sql text; var_result json; var_srid integer; var_geo geometry; 
    var_table text; var_cols text; var_input_srid integer; 
    var_geom_col text;
BEGIN
    SELECT 
        f_geometry_column, 
        quote_ident(f_table_schema) || '.' || quote_ident(f_table_name) 
    FROM geometry_columns
    INTO var_geom_col, var_table -- <co id="co_code_get_features_1a"/>
    WHERE f_table_schema || '.' || f_table_name = param_table  -- <co id="co_code_get_features_1b"/>
    LIMIT 1;  
 
    IF var_geom_col IS NULL THEN
        RAISE EXCEPTION 'No such geometry table as %', param_table;
    END IF;
    var_geo := ST_GeomFromGeoJSON($1::text); -- <co id="co_code_get_features_2a"/>
    var_input_srid := ST_SRID(var_geo); -- <co id="co_code_get_features_3a"/>
    If var_input_srid < 1 THEN -- <co id="co_code_get_features_3b"/>
        var_input_srid = 4326; -- <co id="co_code_get_features_3c"/>
        var_geo := ST_SetSRID( -- <co id="co_code_get_features_3d"/>
        ST_GeomFromGeoJSON($1::text),var_input_srid); -- <co id="co_code_get_features_3e"/>
    END IF; -- <co id="co_code_get_features_3f"/> --
  
    var_sql := 'SELECT ST_SRID(geom) FROM ' || var_table || ' LIMIT 1'; -- <co id="co_code_get_features_4a"/>

    EXECUTE var_sql INTO var_srid; -- <co id="co_code_get_features_4b"/>
  
    SELECT string_agg(quote_ident(trim(a)), ',') 
    INTO var_cols -- <co id="co_code_get_features_5a"/>
    FROM unnest(string_to_array(param_props, ',')) As a; -- <co id="co_code_get_features_5b"/>
     
    var_sql := 
        'SELECT row_to_json(fc) 
        FROM (
            SELECT 
                ''FeatureCollection'' As type, 
                array_to_json(array_agg(f)) As features
            FROM (
                SELECT 
                    ''Feature'' As type, 
                    ST_AsGeoJSON(ST_Transform(
                        lg.' || quote_ident(var_geom_col) || ', $4)
                    )::json As geometry,
                    row_to_json(
                        (SELECT l FROM (SELECT ' || var_cols || ') As l)
                    ) As properties 
                FROM ' || var_table || ' AA lg 
                WHERE ST_Intersects(lg.geom,ST_Transform($1,$2)) LIMIT $3
            ) As f
        ) As fc;'; -- <co id="co_code_get_features_6a"/>

    EXECUTE var_sql INTO var_result 
    USING var_geo, var_srid, param_limit, var_input_srid; -- <co id="co_code_get_features_7a"/>
     
    RETURN var_result; -- <co id="co_code_get_features_7b"/>
END;
$$
LANGUAGE plpgsql;
-- <end id="code_get_features" > --