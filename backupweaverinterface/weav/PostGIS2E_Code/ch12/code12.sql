-- <start id="code_chap_raster_processing_schema"/> --
CREATE SCHEMA ch12;
-- <end id="code_chap_raster_processing_schema"/> 

-- <start id="code_add_attribute_rast_climate"/> --
ALTER TABLE ch12.prec ADD COLUMN month smallint; -- <co id="co_code_add_attribute_rast_climate_1"/>
UPDATE ch12.prec 
SET month = regexp_replace(
    filename,
    E'[a-z]+([0-9]+)\\_[0-9]+.bil', E'\\\\1'
)::integer; -- <co id="co_code_add_attribute_rast_climate_2"/>
-- <end id="code_add_attribute_rast_climate"/> --

--Correct code --
ALTER TABLE ch12.prec ADD COLUMN month smallint;
UPDATE ch12.prec 
SET month = regexp_replace(filename,
    E'[a-z]+([0-9]+)\_[0-9]+.bil', E'\\1')::integer; 
    
ALTER TABLE ch12.tmean ADD COLUMN month smallint; 
UPDATE ch12.tmean 
SET month = regexp_replace(filename, 
    E'[a-z]+([0-9]+)\_[0-9]+.bil', E'\\1')::integer;

-- <start id="code_basic_reconstitute_file"/> --
SELECT 
    filename,
    COUNT(rast) As num_tiles,
    ST_Union(rast) As rast -- <co id="co_code_basic_reconstitute_file_1"/>
FROM ch12.prec
WHERE filename IN ('prec1_16.bil','prec2_16.bil') -- <co id="co_code_basic_reconstitute_file_2"/>
GROUP BY filename;
-- <end id="code_basic_reconstitute_file"/>

-- <start id="code_union_clipping"/> --
SELECT ST_Union(ST_Clip(rast,geom)) AS rast -- <co id="co_code_union_clipping_1"/>
FROM 
    ch12.alt 
    CROSS JOIN 
    ST_MakeEnvelope(8,47,8.5,47.5,4326) As geom -- <co id="co_code_union_clipping_2"/>
WHERE ST_Intersects(rast,geom); -- <co id="co_code_union_clipping_3"/>
-- <end id="code_union_clipping"/>

-- <start id="code_basic_union_mean"/> --
SELECT ST_Union(ST_Clip(rast,geom), 'MEAN') As rast -- <co id="co_code_basic_union_mean_1"/>
FROM 
    ch12.prec  
    CROSS JOIN 
    ST_MakeEnvelope(8,47,8.5,47.5,4326) As geom 
WHERE ST_Intersects(rast,geom) AND month BETWEEN 1 and 12;
-- <end id="code_basic_union_mean"/> --

-- <start id="code_add_raster_bands"/> --
CREATE TABLE ch12.tmean_prec (
    rid serial primary key,
    rast raster, 
    filename_tmean text, 
    filename_prec text,
    month smallint
); -- <co id="co_code_add_raster_bands_1"/>
 
INSERT INTO ch12.tmean_prec (rast, filename_tmean, filename_prec, month)
SELECT 
    ST_AddBand(t.rast, p.rast) As rast, -- <co id="co_code_add_raster_bands_2"/>
    t.filename As filename_tmean, p.filename As filename_prec, t.month
FROM ch12.tmean As t INNER JOIN ch12.prec As p
ON t.rast ~= p.rast AND t.month = p.month; -- <co id="co_code_add_raster_bands_3"/>
  
CREATE INDEX idx_tmean_prec_rast_gist ON ch12.tmean_prec -- <co id="co_code_add_raster_bands_4"/>
USING gist (ST_ConvexHull(rast));
-- <end id="code_add_raster_bands"/> --

-- <start id="code_subset_band"/> --
SELECT rid, ST_Band(rast,1) As rast
INTO ch12.tmean2
FROM ch12.tmean_prec;

CREATE INDEX idx_tmean2_rast_gist ON ch12.tmean2
USING gist (ST_ConvexHull(rast));
-- <end id="code_subset_band"/>

-- <start id="code_st_tile_even_block"/> --
CREATE TABLE ch12.tmean_prec_128_128 (
    rid serial primary key, 
    rast raster, 
    month smallint
); -- <co id="co_code_st_tile_even_block_1"/>

INSERT INTO ch12.tmean_prec_128_128 (rast,month)
SELECT ST_Tile(rast, 128, 128, true) AS rast, month -- <co id="co_code_st_tile_even_block_2"/> --
FROM ch12.tmean_prec;

CREATE INDEX idx_tmean_prec_128_128_rast_gist 
  ON ch12.tmean_prec_128_128 USING gist (ST_ConvexHull(rast));
  
SELECT AddRasterConstraints(
    'ch12'::name, 
    'tmean_prec_128_128'::name, 
    'rast'::name
); -- <co id="co_code_st_tile_even_block_3"/> --
-- <end id="code_st_tile_even_block"/> --


-- <start id="code_st_intersection_rast_geom_1"/> --
SELECT 
    CAST((gval).val As integer) AS val,  -- <co id="co_code_st_intersection_rast_geom_1_1"/>
    ST_Union((gval).geom) As geom  -- <co id="co_code_st_intersection_rast_geom_1_1a"/>
FROM (
    SELECT ST_Intersection(  -- <co id="co_code_st_intersection_rast_geom_1_2"/>
        ST_Clip(rast,ST_Envelope(buf.geom)),
        1,
        buf.geom
    ) As gval -- <co id="co_code_st_intersection_rast_geom_1_3"/>
    FROM ch12.kauai
    INNER JOIN (
    SELECT ST_Buffer(
        ST_GeomFromText('POINT(444205 2438785)',26904),100
    ) As geom) As buf 
    ON ST_Intersects(rast,buf.geom)   -- <co id="co_code_st_intersection_rast_geom_1_4"/>
) As foo
GROUP BY (gval).val
ORDER BY (gval).val;
-- <end id="code_st_intersection_rast_geom_1"/>

-- [1] pixel val 
-- [1a] geometry
-- [2] intersected output
-- [3,3a] only consider portion of each raster that is in buffer bounding box
-- [4] only consider tiles that intersect the buffer



-- <start id="code_st_intersection_rast_geom_2"/> --
SELECT 
    SUM((gval).val * ST_Area((gval).geom)) / 
    ST_Area(ST_Union((gval).geom)) As avg_elesqm
FROM (
    SELECT ST_Intersection(rast,1,buf.geom) As gval FROM ch12.kauai 
     INNER JOIN 
    (
        SELECT ST_Buffer(
            ST_GeomFromText('POINT(444205 2438785)',26904),100
        ) As geom
    ) As buf
ON ST_Intersects(rast,buf.geom)) As foo;
-- <end id="code_st_intersection_rast_geom_2"/>

-- <start id="code_st_value_3d"/> --
SELECT 
    ST_AsText(                              
        ST_MakeLine( -- <co id="co_code_st_value_3d_1"/>
            ST_Translate( -- <co id="co_code_st_value_3d_2"/>
                ST_Force3D((gd).geom),  -- <co id="co_code_st_value_3d_3"/>
                0,0,
                COALESCE(ST_Value(rast,(gd).geom),0) -- <co id="co_code_st_value_3d_4"/>
            )
        )
    ) As line_3dwkt
FROM 
    (
        SELECT ST_DumpPoints(
            ST_GeomFromText(
                'LINESTRING(
                    444210 2438785,434125 2448785,
                    466666 2449780,47000 2459000
                )',
                26904
            )
        ) As gd
    ) As trail -- <co id="co_code_st_value_3d_5"/>
    LEFT JOIN 
    ch12.kauai 
    ON ST_Intersects(rast,(gd).geom); -- <co id="co_code_st_value_3d_6"/>
-- <end id="code_st_value_3d"/>

-- <start id="code_create_kauai_poly_table"/> --
CREATE TABLE ch12.kauai_polys (
    gid serial primary key,
    geom geometry(POLYGON,26904)
);
INSERT INTO ch12.kauai_polys (geom)
SELECT ST_Buffer(ST_GeomFromText('POINT(444205 2438785)',26904),100)
UNION ALL
SELECT ST_Buffer(ST_GeomFromText('POINT(444005 2438485)',26904),10);
-- <end id="code_create_kauai_poly_table"/>

-- <start id="code_st_intersection_rast_geom_3"/> --  
SELECT 
    p.gid, 
    ST_Translate( -- <co id="co_code_st_intersection_rast_geom_3_1"/>
        ST_Force3D((r.gval).geom), 0, 0, (r.gval).val -- <co id="co_code_st_intersection_rast_geom_3_2"/>
    ) As geom3d 
FROM 
    ch12.kauai_polys As p, 
    LATERAL (
        SELECT ST_Intersection(ST_Clip(rast,1,p.geom),1,p.geom) AS gval 
        FROM ch12.kauai
        WHERE ST_Intersects(rast,p.geom) -- <co id="co_code_st_intersection_rast_geom_3_4"/> 
    ) As r; -- <co id="co_code_st_intersection_rast_geom_3_3"/>
-- <end id="code_st_intersection_rast_geom_3"/>

-- <start id="code_st_value_temp_precip"/> --
SELECT 
    month, 
    ST_Value(rast,1,pt)/10 As temp_c, -- <co id="co_code_st_value_temp_precip_1"/>
    ST_Value(rast,2,pt) As precip -- <co id="co_code_st_value_temp_precip_2"/>
FROM
    ch12.tmean_prec INNER JOIN ST_SetSRID(ST_Point(8,47),4326) AS pt -- <co id="co_code_st_value_temp_precip_3"/>
ON month IN (1,7) AND ST_Intersects(rast,pt)) -- <co id="co_code_st_value_temp_precip_4"/>
ORDER BY month;
-- <end id="code_st_value_temp_precip"/>

-- <start id="code_st_dumpvalues_precip"/> --
SELECT 
    ST_DumpValues( -- <co id="co_code_st_dumpvalues_precip_1"/>
        ST_Union(ST_Clip(rast,2,geom,false)),
        1
    ) AS ary_precip -- <co id="co_code_st_dumpvalues_precip_2"/>
FROM
    ch12.tmean_prec 
    INNER JOIN  
     (
        SELECT 
            ST_Buffer(
                ST_GeogFromText('POINT(8.00 47.00)'),1200
            )::geometry AS geom
    ) AS f -- <co id="co_code_st_dumpvalues_precip_3"/>
    ON month = 7 AND ST_Intersects(rast,geom); -- <co id="co_code_st_dumpvalues_precip_4"/>
-- <end id="code_st_dumpvalues_precip"/>



-- <start id="code_st_histogram_5bin"/> --
WITH 
    cte AS (
        SELECT 
            ST_Histogram(    -- <co id="co_code_st_histogram_5bin_1"/>
                ST_Union(    -- <co id="co_code_st_histogram_5bin_2"/>
                    ST_Reclass(  -- <co id="co_code_st_histogram_5bin_3"/>
                        ST_Clip(p.rast,geom), -- <co id="co_code_st_histogram_5bin_4"/>
                        1,
                        '-1000-9000:-100-900',
                        '32BF',-9999
                    ),
                    'MAX'
                ),
                1,
                5
            ) As hg
        FROM 
            ch12.tmean AS p 
            INNER JOIN 
            ST_MakeEnvelope(8,47,8.5,47.5,4326) As geom -- <co id="co_code_st_histogram_5bin_5"/>
        ON ST_Intersects(p.rast,geom)
        WHERE month between 1 and 3
)
SELECT 
    (hg).min::numeric(5,2) As min, -- <co id="co_code_st_histogram_5bin_6"/>
    (hg).max::numeric(5,2) As max, 
    (hg).count, 
    (hg).percent::numeric(5,2) As percent
FROM cte;
-- <end id="code_st_histogram_5bin"/> --

-- <start id="code_st_valuecount_area"/> --
WITH 
    cte AS (
        SELECT 
            ST_ValueCount( -- <co id="co_code_st_valuecount_area_1"/>
                ST_Clip(p.rast,geom)  -- <co id="co_code_st_valuecount_area_2"/>
            ) As pv
        FROM 
            ch12.alt AS p 
            INNER JOIN 
            ST_MakeEnvelope(8,47,8.5,47.5,4326) As geom -- <co id="co_code_st_valuecount_area_3"/>
        ON ST_Intersects(p.rast, geom)
    )
SELECT (pv).value, sum((pv).count) As total_count -- <co id="co_code_st_valuecount_area_4"/>
FROM cte
GROUP BY (pv).value
ORDER by total_count DESC -- <co id="co_code_st_valuecount_area_5"/>
LIMIT 5;
-- <end id="code_st_valuecount_area" /> --

-- <start id="code_st_mapalgebra_expression"/> --
CREATE TABLE ch12.tmean_cel (
    rid integer primary key, 
    rast raster,
    month integer
); -- <co id="co_code_st_mapalgebra_expression_1"/>
 
INSERT INTO ch12.tmean_cel(rid, month, rast)
SELECT 
    rid, month,
    ST_MapAlgebra(
        rast, 
        1,
        '32BF'::text, -- <co id="co_code_st_mapalgebra_expression_2"/>
        '[rast.val]/10.0'::text,
        -999
    ), 
FROM ch12.tmean AS t
WHERE 
    NOT EXISTS (
        SELECT c.rid 
        FROM ch12.tmean_cel As c -- <co id="co_code_st_mapalgebra_expression_3"/>
        WHERE c.rid = t.rid
    ) 
LIMIT 10;
-- <end id="code_st_mapalgebra_expression"/> -- 

-- <start id="code_st_mapalgebra_callbackfunc_1"/> --
CREATE OR REPLACE FUNCTION ch12.tempdiv_cbf (
    value double precision[][][], 
    pos integer[][], 
    VARIADIC userargs text[]
)  -- <co id="co_code_st_mapalgebra_callbackfunc_1_1"/>
RETURNS double precision AS 
$$
BEGIN
    RETURN value[1][1][1]/10.0;
END;
$$ 
LANGUAGE 'plpgsql' IMMUTABLE COST 1000;
  
INSERT INTO ch12.tmean_cel (rid, month, rast)
SELECT 
    rid, month,
    ST_MapAlgebra(
        rast, 
        1, 
        'ch12.tempdiv_cbf(
            double precision[],integer[],text[]
        )'::regprocedure, -- <co id="co_code_st_mapalgebra_callbackfunc_1_2"/>
        '32BF'::text)
FROM ch12.tmean AS t
WHERE 
    NOT EXISTS (
        SELECT c.rid 
        FROM ch12.tmean_cel As c 
        WHERE c.rid = t.rid
    ) 
LIMIT 10;
-- <end id="code_st_mapalgebra_callbackfunc_1"/>

-- <start id="code_st_mapalgebra_neighborhood"/> --
SELECT 
    ST_MapAlgebra( -- <co id="co_code_st_mapalgebra_neighborhood_1"/>
        ST_Union(
            ST_Clip(rast,ST_Envelope(buf.geom)) -- <co id="co_code_st_mapalgebra_neighborhood_2"/>
        ), 
        1, 
        'ST_Max4ma(
            double precision[][][],
            integer[][],
            text[]
        )'::regprocedure, -- <co id="co_code_st_mapalgebra_neighborhood_3"/>
        '32BF',
        'FIRST',
        NULL,
        2,
        2 -- <co id="co_code_st_mapalgebra_neighborhood_4"/>
    )
FROM 
    ch12.kauai
    INNER JOIN 
    (
        SELECT 
            ST_Buffer(
                ST_GeomFromText('POINT(444205 2438785)',26904),100
            ) As geom
    ) As buf 
ON ST_Intersects(rast,buf.geom) 
GROUP BY buf.geom;
-- <end id="code_st_mapalgebra_neighborhood"/>




-- making a geometry grid --
-- <start id="code_st_tile_geom_grid"/> --
WITH cte_ext AS 
    (SELECT ST_SetSRID(ST_Extent(rast::geometry), ST_SRID(rast)) 
 FROM ch12.tmean GROUP BY ST_SRID(rast))
SELECT ST_MakeEmptyRaster(integer width, integer height, 
    float8 upperleftx, float8 upperlefty, float8 pixelsize); 
--<end id="code_st_tile_geom_grid"/>




-- old way --
SELECT CAST((gval).val As integer) AS val,  
     (gval).geom As geom                  
FROM (
SELECT ST_Intersection(rast,1,buf.geom) As gval  
FROM ch12.kauai 
     INNER JOIN (
     SELECT ST_Buffer(
     ST_GeomFromText('POINT(444205 2438785)',26904),100)   
     As geom) As buf ON
    ST_Intersects(rast,buf.geom) )      As foo    
ORDER BY (gval).val
-- end old way










SELECT ST_AsText(ST_Union(
        ST_Translate(ST_Force3D((gd).geom),
          0,0, (gd).val)
        ) ) As geom
FROM ST_GeomFromText('LINESTRING(444210 2438785,                 
          434125 2448785,  466666 2449780, 
          47000 2459000)',
          26904 ) AS geom
     , 
     LATERAL ( 
  SELECT ST_Intersection(geom,ST_Clip(rast,geom)) As gd
    FROM ch12.kauai 
   WHERE ST_Intersects(rast, geom) 
     ) AS k; 

