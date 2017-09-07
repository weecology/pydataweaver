-- <start id="code_bag_o_rasters"/> --
CREATE SCHEMA ch07;
CREATE TABLE ch07.bag_o_rasters(
    rid serial primary key, rast_name text, rast raster
);
-- <end id="code_bag_o_rasters"/>

-- <start id="code_geom_st_asraster_fixed"/> --
INSERT INTO ch07.bag_o_rasters(rast_name, rast)  
WITH a1 AS (
	SELECT ST_Buffer(
		ST_GeomFromText(
			'LINESTRING(
				448252 5414206,448289 5414317,448293 5414330,
				448324 5414417,448351 5414495
			)', 
			32631), 
		10
	) As geom
)   -- <co id="co_geom_st_asraster_fixed_1"/> --
SELECT 'disprop road', ST_AsRaster(geom,50,500) FROM a1 -- <co id="co_geom_st_asraster_fixed_2"/> --
UNION ALL
SELECT 
    'proport fixed w road', 
    ST_AsRaster(geom,200,(
        (ST_YMax(geom) - ST_YMin(geom)) *  200 / 
        (ST_XMax(geom) - ST_XMin(geom))
    )::integer 
FROM a1; -- <co id="co_geom_st_asraster_fixed_3"/> --
-- <end id="code_geom_st_asraster_fixed"/> --

-- <start id="code_geom_st_asraster_aligned"/> --
WITH 
    r AS 
        (SELECT 
            ST_MakeEmptyRaster(
                500,500,445000,5415000,2,-2,0,0,32631
            ) As rast
        ), -- <co id="co_geom_st_asraster_aligned_1"/> --
    g AS 
        (SELECT ST_Buffer(
            ST_GeomFromText(
                'LINESTRING(
                    448252 5414206,448289 5414317,448293 5414330,
                    448324 5414417,448351 5414495)',
                32631), 
            10) As geom
        ) -- <co id="co_geom_st_asraster_aligned_2"/> --
INSERT INTO ch07.bag_o_rasters(rast_name, rast)     
SELECT 'canvas aligned road', ST_AsRaster(geom,rast,'8BUI'::text) -- <co id="co_geom_st_asraster_aligned_3"/> --
FROM r CROSS JOIN g;
-- <end id="code_geom_st_asraster_aligned"/> --

-- code_stamp_raster_as_Reo --
UPDATE ch07.bag_o_rasters SET rast_name = 'Reo' 
WHERE rast_name IS NULL;
-- code_stamp_raster_as_Reo --




-- <start id="code_rast_scratch"/> --  
INSERT INTO ch07.bag_o_rasters(rast_name, rast) 
SELECT 
    'Raster 1 band scratch', 
    ST_AddBand( -- <co id="co_code_rast_scratch_1"/> --
        ST_MakeEmptyRaster( -- <co id="co_code_rast_scratch_2"/> --
            500,500,445000,5415000,2,-2,0,0,32631
        ),
        '8BUI'::text,255,0 -- <co id="co_code_rast_scratch_3"/> --
    ) As rast;
-- <end id="code_rast_scratch"/> --


-- code_rast_st_setvalue_cr"/> --  
UPDATE ch07.bag_o_rasters AS b
SET rast = ST_SetValue(rast,1,10,20,146)
WHERE b.rast_name = 'Raster 1 band scratch';
-- code_rast_st_setvalue_cr --

-- <start id="code_rast_heatmap" /> -- 
WITH heatmap As ( -- <co id="co_code_rast_heatmap_1"/> --
    SELECT array_agg( -- <co id="co_code_rast_heatmap_2"/> --
        (ST_Buffer(  
            ST_Translate(
                ST_SetSRID(
                    ST_Point(445500,5414500), 32631
                ),
                -500 + i * 150,
                -200 + 160 * i
            ),
            i * 50),
            50 + i * 15.0
        )::geomval 
    ) As gvals
    FROM generate_series(-3,4) As i
)
INSERT INTO ch07.bag_o_rasters(rast_name, rast)  
SELECT 
    'Raster 1 band heatmap', 
    ST_SetValues(rast,1, heatmap.gvals) As rast -- <co id="co_code_rast_heatmap_3"/> --
FROM ch07.bag_o_rasters As b CROSS JOIN heatmap
WHERE b.rast_name = 'Raster 1 band scratch';
-- <end id="code_rast_heatmap"/> --


-- <start id="code_rast_st_band_clip"/> --
INSERT INTO ch07.bag_o_rasters(rast_name, rast)
SELECT 
    'Reo 1 band crop', 
    ST_Clip(
        rast,
        1,
        ST_Buffer(ST_Centroid(rast::geometry), 75),
        255
    )
FROM ch07.bag_o_rasters 
WHERE rast_name = 'Reo';
-- <end id="code_rast_st_band_clip"/> --

-- <start id="code_rast_st_band_shuffle"/> --
INSERT INTO ch07.bag_o_rasters (rast_name,rast)
SELECT 'Reo band shuffle', ST_Band(rast,ARRAY[3,1,2]) 
FROM ch07.bag_o_rasters 
WHERE rast_name = 'Reo';
-- <end id="code_rast_st_band_shuffle"/> --

-- <start id="code_st_aspng"/> --
SELECT ST_AsPNG(rast) As png
FROM ch07.bag_o_rasters 
WHERE rast_name = 'Raster 1 band heatmap';
-- <end id="code_st_aspng"/> --

-- <start id="code_gdaldrivers_writeable_formats"/> --
SELECT short_name, long_name 
FROM ST_GDALDrivers()
ORDER BY short_name;
-- <end id="code_gdaldrivers_writeable_formats"/> --

-- <start id="code_gdaldrivers_writeable_formats_options"/> --
SELECT 
    (xpath('@name', g.opt))[1]::text As oname,
    (xpath('@type', g.opt))[1]::text As otype,
    (xpath('@description', g.opt))[1]::varchar(30) As descrip
FROM (
    SELECT 
        unnest(
            xpath('/CreationOptionList/Option',create_options::xml)
        ) As opt
    FROM ST_GDALDrivers()
    WHERE short_name = 'USGSDEM'
) As g;
-- <end id="code_gdaldrivers_writeable_formats_options"/> --

-- <start id="code_st_asgdalraster_usgsdem"/> --
SELECT 
    ST_AsGDALRaster(ST_Band(rast,1),
    ARRAY[
        'PRODUCER=' || quote_literal('postgis_in_action'),
        'INTERNALNAME=' || quote_literal(rast_name)
    ]) As dem
FROM ch07.bag_o_rasters 
WHERE rast_name='Raster 1 band heatmap';
-- <end id="code_st_asgdalraster_usgsdem"/> --

-- <start id="code_st_asgdalraster_output_psql"/> --
SELECT oid, lowrite(lo_open(oid, 131072), img) As num_bytes
FROM (
    VALUES (
        lo_create(0), -- <co id="co_code_st_asgdalraster_output_psql_1"/> --
        (SELECT 
            ST_AsGDALRaster(ST_Band(rast,1), 
            'USGSDEM',
            ARRAY[
                'PRODUCER=' || quote_literal('postgis_in_action'),
                'INTERNALNAME=' || quote_literal(rast_name)]
            ) As dem
        FROM ch07.bag_o_rasters 
        WHERE rast_name = 'Raster 1 band heatmap') -- <co id="co_code_st_asgdalraster_output_psql_2"/> --
    )
) As v(oid,img);
  
\lo_export 9585208 'C:/temp/heatmap.dem' -- <co id="co_code_st_asgdalraster_output_psql_3"/> --

SELECT lo_unlink(9585208); -- <co id="co_code_st_asgdalraster_output_psql_4"/> --

-- <end id="code_st_asgdalraster_output_psql"/> --
--[1] create large object
--[2] query output to dem
--[3] use oid returned by previous query
--[4] when done delete large object


-- <start id="code_basic_raster_meta_data"/> --
SELECT 
    rid As r, rast_name, 
    ST_Width(rast) As w, 
    ST_Height(rast) As h, 
    round(ST_PixelWidth(rast)::numeric,4) AS pw, 
    round(ST_PixelHeight(rast)::numeric,4) As ph, 
    ST_SRID(rast) AS srid, 
    ST_BandPixelType(rast,1) AS bt
FROM ch07.bag_o_rasters;
-- <end id="code_basic_raster_meta_data"/>

-- <start id="code_basic_raster_st_metadata_bandmetadata"/> -- 
SELECT rid As r, (rm).upperleftx As ux, (rm).numbands As nb, (rbm).*
FROM (
    SELECT 
        rid, 
        ST_MetaData(rast) As rm,
        ST_BandMetaData(rast,1) As rbm
FROM ch07.bag_o_rasters) As r;
-- <end id="code_basic_raster_st_metadata_bandmetadata"/> --


-- <start id="code_st_histogram_single"/> --
SELECT (stats).*
FROM (
    SELECT ST_Histogram(rast,2,6) As stats
    FROM ch07.bag_o_rasters
    WHERE rast_name = 'Reo'
) As foo;
-- <end id="code_st_histogram_single"/> --


-- <start id="code_st_summarystats_single"/> --
SELECT (stats).*
FROM (
    SELECT ST_SummaryStats(rast,2) As stats
    FROM ch07.bag_o_rasters 
    WHERE rast_name = 'Reo'
) As foo;
-- <end id="code_st_summarystats_single"/> --

-- <start id="code_st_dumpaspolygons_1"/> --
WITH X AS (
    SELECT ST_DumpAsPolygons(rast) As gv
    FROM ch07.bag_o_rasters 
    WHERE rast_name = 'Raster 1 band heatmap'
)
SELECT 
    ST_AsText((gv).geom)::varchar(30) AS wkt, 
    ST_Area((gv).geom) As area, 
    (gv).val
FROM Z;
-- <end id="code_st_dumpaspolygons_1"/> --

-- <start id="code_st_georeference_single"/> --
UPDATE ch07.bag_o_rasters 
SET rast = ST_SetSRID(
    ST_SetGeoReference(rast, '1 0 0 -1 445139 5415000'),32631
)
WHERE rast_name = 'Reo 1 band crop';
-- <end id="code_st_georeference_single"/> --

-- <start id="code_raster_georeference_processing_effects"/> --
WITH 
    r As (
    SELECT rast 
    FROM ch07.bag_o_rasters 
    WHERE rast_name = 'canvas aligned road'
),
    r2 AS (
    SELECT 'orig' As op, ST_MetaData(rast) As rm FROM r
    UNION ALL
    SELECT 'resamp' AS op, 
    	ST_MetaData(ST_Resample(rast,300,300)) As rm FROM r -- <co id="co_code_raster_georeference_processing_effects_2" /> --
    UNION ALL
    SELECT 'tform' AS op, 
    		ST_MetaData(ST_Transform(rast,4326)) As rm FROM r -- <co id="co_code_raster_georeference_processing_effects_3" /> --
    UNION ALL
    SELECT 'resize' AS op, 
    		ST_MetaData(ST_Resize(rast,0.5,0.5)) As rm FROM r-- <co id="co_code_raster_georeference_processing_effects_4" /> --
    UNION ALL 
    SELECT 'rescale' AS op, 
    		ST_MetaData(ST_Rescale(rast,0.5,-0.5)) As rm FROM r -- <co id="co_code_raster_georeference_processing_effects_5" /> --
) 
SELECT 
    op,
    (rm).srid, 
    (rm).width::text || 'x' || (rm).height::Text as wh,
    (rm).scalex::numeric(7,5)::text || ',' || 
    (rm).scaley::numeric(7,5)::text as sxy, 
    (rm).upperleftx::numeric(11,2)::text || ',' || 
    (rm).upperlefty::numeric(12,2)::text As uplxy
FROM r2;
-- <end id="code_raster_georeference_processing_effects"/> --


--[2] resample 300x300 pixels
--[3] transform to long lat
--[4] resize to 50%
--[5] rescale to 0.5, -0.5 meters/pix

-- <start id="code_st_reclass_band2_Reo"/> --
INSERT INTO ch07.bag_o_rasters(rast_name, rast)
SELECT 
    'Reo 1 banded band 2 reclass', 
    ST_Reclass(
        ST_Band(rast,2), -- <co id="co_code_st_reclass_band2_Reo_1"/> --
        1, -- <co id="co_code_st_reclass_band2_Reo_2"/> -- 
        '[0-66]:0,(66-255]:255'::text , '8BUI'::text, -- <co id="co_code_st_reclass_band2_Reo_3"/> --
        255  -- <co id="co_code_st_reclass_band2_Reo_4"/> --
) 
FROM ch07.bag_o_rasters
WHERE rast_name = 'Reo';
-- <end id="code_st_reclass_band2_Reo"/> --


-- [1] create new rast with just band 2
-- [2] band 1 of single band
-- [3] reclass so val > 66 and val <= 255 are set to no data
-- [4] set 255 to no data

-- <start id="code_st_convexhull_Reo"/> --
SELECT 
    rast_name::varchar(10), 
    ST_AsText(ST_ConvexHull(rast)) As hull, 
    ST_AsText(ST_MinConvexHull(rast)) As minhull
FROM ch07.bag_o_rasters
WHERE rast_name IN('Reo','Reo 1 banded band 2 reclass');
-- <end id="code_st_convexhull_Reo"/> --