-- <start id="code_count_geoms_union"/> --
SELECT 
    city, 
    COUNT(city) AS num_records, 
    SUM(ST_NumGeometries(geom)) AS numpoly_before,
    ST_NumGeometries(ST_Multi(ST_Union(geom))) AS num_poly_after
FROM ch11.cities
GROUP BY city
HAVING COUNT(city) > 1;
-- <end id="code_count_geoms_union"/> --

-- <start id="code_union_one_per_city"/> --
SELECT city, ST_Multi(
    ST_Union(geom))::geometry(multipolygon,2227) AS geom -- <co id="co_code_union_one_per_city_1"/> -- 
INTO ch11.distinct_cities -- <co id="co_code_union_one_per_city_2"/> --
FROM ch11.cities
GROUP BY city, ST_SRID(geom);

ALTER TABLE ch11.distinct_cities 
ADD CONSTRAINT pk_distinct_cities 
PRIMARY KEY (city); -- <co id="co_code_union_one_per_city_3"/> --

CREATE INDEX idx_distinct_cities_geom 
    ON ch11.distinct_cities USING gist(geom); -- <co id="co_code_union_one_per_city_4"/> --
-- <end id="code_union_one_per_city"/> --

-- <start id="code_make_path_gps"/> --
SELECT 
    DATE_TRUNC('minute',time) - -- <co id="co_code_make_path_gps_1a"/> --
        CAST(
            mod(
                CAST(DATE_PART('minute',time) AS integer),15
            ) ||' minutes' AS interval
        ) AS track_period, -- <co id="co_code_make_path_gps_1b"/> --
    MIN(time) AS t_start, 
    MAX(time) AS t_end, 
    ST_MakeLine(geom ORDER BY time) AS geom  -- <co id="co_code_make_path_gps_2"/> --
INTO ch11.aussie_run
FROM ch11.aussie_track_points
GROUP BY track_period -- <co id="co_code_make_path_gps_3"/> --
HAVING COUNT(time) > 1; -- <co id="co_code_make_path_gps_4"/> --

SELECT 
    CAST(track_period AS timestamp), -- <co id="co_code_make_path_gps_5"/> --
    CAST(t_start AS timestamp) AS t_start,    
    CAST(t_end AS timestamp) AS t_end, 
    ST_NPoints(geom) AS np, 
    CAST(ST_Length(geom::geography) AS integer) AS dist_m, -- <co id="co_code_make_path_gps_6"/> --
    (t_end - t_start) AS dur               
FROM ch11.aussie_run;  
-- <end id="code_make_path_gps"/> --


-- <start id="code_diff_symdiff"/> --
SELECT 
    ST_Intersects(g1.geom1,g1.geom2) AS they_intersect, -- <co id="co_code_diff_symdiff_1"/> --
    GeometryType(
        ST_Difference(g1.geom1,g1.geom2) ) AS intersect_geom_type
FROM (
    SELECT ST_GeomFromText(
        'POLYGON((
            2 4.5,3 2.6,3 1.8,2 0,-1.5 2.2,
            0.056 3.222,-1.5 4.2,2 6.5,2 4.5
        ))'
    ) AS geom1, 
    ST_GeomFromText('LINESTRING(-0.62 5.84,-0.8 0.59)') AS geom2
) AS g1;

SELECT 
    ST_Intersects(g1.geom1,g1.geom2) AS they_intersect, -- <co id="co_code_diff_symdiff_2"/> --
    GeometryType(
        ST_Difference(g1.geom2,g1.geom1) ) AS intersect_geom_type
FROM (
    SELECT ST_GeomFromText(
        'POLYGON((
            2 4.5,3 2.6,3 1.8,2 0,-1.5 2.2,
            0.056 3.222,-1.5 4.2,2 6.5,2 4.5
        ))'
    ) AS geom1, 
    ST_GeomFromText('LINESTRING(-0.62 5.84,-0.8 0.59)') AS geom2) AS g1;

SELECT 
    ST_Intersects(g1.geom1,g1.geom2) AS they_intersect, -- <co id="co_code_diff_symdiff_3"/> --
    GeometryType(
        ST_SymDifference(g1.geom1,g1.geom2)
    ) AS intersect_geom_type
FROM (
    SELECT ST_GeomFromText(
        'POLYGON((
            2 4.5,3 2.6,3 1.8,2 0,-1.5 2.2,
            0.056 3.222,-1.5 4.2,2 6.5,2 4.5
        ))'
    ) AS geom1, 
    ST_GeomFromText('LINESTRING(-0.62 5.84,-0.8 0.59)') AS geom2) AS g1;
-- <end id="code_diff_symdiff"/> --

-- <start id="code_split_poly_line"/> --
SELECT (ST_Dump(ST_Split(g1.geom1, g1.geom2))).geom AS geom  -- <co id="co_code_split_poly_line_1"/> --
FROM ( -- <co id="co_code_split_poly_line_2"/> --
    SELECT 
        ST_GeomFromText(
            'POLYGON((
                2 4.5,3 2.6,3 1.8,2 0,-1.5 2.2,0.056 
                3.222,-1.5 4.2,2 6.5,2 4.5
            ))'
        ) AS geom1, 
        ST_GeomFromText('LINESTRING(-0.62 5.84,-0.8 0.59)') AS geom2
) AS g1;
-- <end id="code_split_poly_line"/> --

-- <start id="code_grid_states"/> --
WITH 
    usext AS (
        SELECT 
            ST_SetSRID(CAST(ST_Extent(geom) AS geometry),
            2163) AS geom_ext, 60 AS x_gridcnt, 40 AS y_gridcnt
        FROM us.states
    ),
    grid_dim AS (
        SELECT 
            (
                ST_XMax(geom_ext)-ST_XMin(geom_ext)
                ) / x_gridcnt AS g_width, 
            ST_XMin(geom_ext) AS xmin, ST_xmax(geom_ext) AS xmax,
            (
                ST_YMax(geom_ext)-ST_YMin(geom_ext)
                ) / y_gridcnt AS g_height,     
            ST_YMin(geom_ext) AS ymin, ST_YMax(geom_ext) AS ymax
        FROM usext                                    
    ), -- <co id="co_code_grid_states_2a"/> --
    grid AS (                    
        SELECT 
            x, y, 
            ST_MakeEnvelope(  
                xmin + (x - 1) * g_width, ymin + (y - 1) * g_height,  
                xmin + x * g_width, ymin + y * g_height,
                2163
            ) AS grid_geom -- <co id="co_code_grid_states_3a"/> 
        FROM 
            (SELECT generate_series(1,x_gridcnt) FROM usext) AS x(x)    
            CROSS JOIN 
            (SELECT generate_series(1,y_gridcnt) FROM usext) AS y(y) 
            CROSS JOIN 
            grid_dim                                                 
    )   
SELECT 
    g.x, g.y, state, state_fips, 
    ST_Intersection(s.geom, grid_geom) AS geom -- <co id="co_code_grid_states_4a"/> 
INTO ch11.grid_throwaway                    
FROM us.states AS s INNER JOIN grid AS g 
ON ST_Intersects(s.geom,g.grid_geom); 

CREATE INDEX idx_us_grid_throwaway_geom 
ON ch11.grid_throwaway 
USING gist(geom); -- <co id="co_code_grid_states_5a"/> --
-- <end id="code_grid_states"/> --

-- <start id="code_equal_area_slices_idaho"/> --
WITH RECURSIVE 
x (geom,env) AS (
	SELECT 
		geom, ST_Envelope(geom) AS env, ST_Area(geom)/2 AS targ_area,
		1000 AS nit                   
    FROM us.states                  
    WHERE state = 'Idaho'       
),                                  
T (n,overlap) AS (
	VALUES (CAST(0 AS float), CAST(0 AS float))
	UNION ALL                              
	SELECT 
		n+nit, 
		ST_Area(ST_Intersection(geom,ST_Translate(env,n+nit,0)))     
	FROM T CROSS JOIN x                
	WHERE 
		ST_Area(ST_Intersection(geom,ST_Translate(env,n+nit,0))) 
		> 
		x.targ_area               
),
bi(n) AS (SELECT n FROM T ORDER BY n DESC LIMIT 1) 
SELECT
	bi.n, 
	ST_Difference(geom,ST_Translate(x.env, n,0)) AS geom_part1,
    ST_Intersection(geom,ST_Translate(x.env, n,0)) AS geom_part2
FROM bi CROSS JOIN x;      
-- <end id="code_equal_area_slices_idaho"/> --

-- <start id="code_oklahoma"/> --
SELECT bucket, geom, ST_Area(geom) AS the_area
FROM utility.upgis_slicegeometry(
    (SELECT geom FROM ch11.states WHERE state = 'Oklahoma'), 
    4
) AS x;
-- <end id="code_oklahoma"/> --

-- <start id="code_upgis_slicegeometry"/> --
CREATE OR REPLACE FUNCTION 
    utility.upgis_slicegeometry(
        ageom geometry,numsections integer, 
        OUT bucket integer, OUT geom geometry)
RETURNS SETOF record AS
$$

WITH RECURSIVE
    
ref (geom,the_box,targ_area,x_mov,y_mov,  --  <co id="co_code_upgis_slicegeometry_1" /> -- 
    x_length,y_length,xmin,ymin) AS ( 
    SELECT 
        geom, 
        ST_MakeEnvelope(
            xmin, ymin, 
            xmin + CAST(x_length/ngrid_xy AS integer), 
            ymin + CAST(y_length/ngrid_xy AS integer), 
            ST_SRID(s.geom)
        ) AS the_box, 
        ST_Area(geom)/$2 AS targ_area, 
        CAST(x_length/ngrid_xy AS integer) AS x_mov,  
        CAST(y_length/ngrid_xy AS integer) y_mov, 
        s.x_length, s.y_length, xmin, ymin        
    FROM (
        SELECT 
            $1 AS geom, ST_XMin($1) AS xmin, ST_YMin($1) AS ymin, 
            ST_XMax($1) - ST_XMin($1) AS x_length, 
            ST_YMax($1) - ST_YMin($1) AS y_length, 
            15*$2 AS ngrid_xy) AS s                   
    ),                                                         

X(x) AS ( -- <co id="co_code_upgis_slicegeometry_2" /> --
    VALUES (CAST(0 AS float))
    UNION ALL                                         
    SELECT x + ref.x_mov FROM X CROSS JOIN ref WHERE x <  ref.x_length
),              
       
       
Y(y) AS ( 
    VALUES (CAST(0 AS float))       
    UNION ALL         
    SELECT y + ref.y_mov FROM Y CROSS JOIN ref WHERE y < ref.y_length
),        
   
diced AS (  -- <co id="co_code_upgis_slicegeometry_3" /> --
    SELECT ROW_NUMBER() OVER(ORDER BY x,y) AS row_num, g.x, g.y, g.geom
    FROM (
        SELECT 
            x, y, 
            ST_Intersection(ref.geom,
                ST_Translate(ref.the_box,x,y)) AS geom
        FROM x CROSS JOIN y CROSS JOIN ref        
        WHERE ST_Intersects(ref.geom, ST_Translate(ref.the_box,x,y))
    ) AS g                                    
),                                                    

T (bucket, row_num, geom, total_area, targ_area, 
 remaining_area) AS ( -- <co id="co_code_upgis_slicegeometry_4" /> 
      SELECT 
        1 AS bucket, row_num, diced.geom, 
        ST_Area(diced.geom) AS total_area,  
        ref.targ_area, 
        ST_Area(ref.geom) - ST_Area(diced.geom) AS remaining_area
    FROM diced CROSS JOIN ref 
    WHERE diced.row_num = 1            
    UNION ALL    
    SELECT 
        CASE 
            WHEN 
                T2.total_area + ST_Area(diced.geom) < T2.targ_area 
                OR 
                T2.remaining_area < T2.targ_area/4 
            THEN 
                T2.bucket 
            ELSE T2.bucket + 1 END AS bucket, 
        diced.row_num, 
        diced.geom,                            
        CASE 
            WHEN T2.total_area + ST_Area(diced.geom) < T2.targ_area 
            THEN T2.total_area + ST_Area(diced.geom) 
            ELSE ST_Area(diced.geom) 
        END AS total_area, 
        T2.targ_area, 
        T2.remaining_area - ST_Area(diced.geom) AS remaining_area
    FROM 
        diced INNER JOIN 
        (SELECT * FROM T ORDER BY row_num DESC LIMIT 1) AS T2
    ON diced.row_num = T2.row_num + 1 
)
    
SELECT bucket, ST_Union(geom) AS geom  -- <co id="co_code_upgis_slicegeometry_5" /> --
    FROM T GROUP BY T.bucket, T.targ_area  

$$
LANGUAGE 'sql' IMMUTABLE;
-- <end id="code_upgis_slicegeometry"/> --

-- <start id="code_segmentize_geog"/> --
SELECT 
	ST_NPoints(geog::geometry) AS np_before,
	ST_NPoints(ST_Segmentize(geog,10000)::geometry) AS np_after
FROM ST_GeogFromText(
	'LINESTRING(-117.16 32.72,-71.06 42.35,8.67 9.08,120.96 23.70)'
) AS geog;
-- <end id="code_segmentize_geog"/> --
-- <start id="code_two_point_line"/> --
SELECT 
	ogc_fid, n AS pt_id, (sl.g).path[1] AS nline, 
    ST_MakeLine( -- <co id="co_code_two_point_line_1" /> --
		ST_PointN((sl.g).geom,n),
		ST_PointN((sl.g).geom,n+1)
	) AS geom 
FROM 
	(SELECT ogc_fid, ST_Dump(geom) AS g -- <co id="co_code_two_point_line_2"/> --
	    FROM ch11.aussie_tracks) AS sl 
	CROSS JOIN 
	generate_series(1,10000) AS n -- <co id="co_code_two_point_line_3"/> --
WHERE n < ST_NPoints((sl.g).geom) -- <co id="co_code_two_point_line_4"/> --
ORDER by ogc_fid, nline, pt_id;
-- <end id="code_two_point_line"/> --

-- <start id="code_two_point_line_lateral"/> --
SELECT ogc_fid, n AS pt_id,(sl.g).path[1] AS nline,
	ST_MakeLine(  
		ST_PointN((sl.g).geom,n),
		ST_PointN((sl.g).geom,n + 1)
	) AS geom
FROM 
	(SELECT ogc_fid, ST_Dump(geom) AS g FROM ch11.aussie_tracks) AS sl
	CROSS JOIN LATERAL    
	generate_series(1,ST_NPoints((sl.g).geom) -  1) AS n
ORDER by ogc_fid, nline, pt_id;
-- <end id="code_two_point_line_lateral"/> --

-- doing with just ST_DumpPoints --
SELECT
     ogc_fid, (sl.g).path[1] As nline, (sl.g).path[2] AS pt_id,
ST_AsText(ST_MakeLine( -- --
        (sl.g).geom,
        lead((sl.g).geom) 
          OVER(PARTITION BY (sl.g).path[1] 
            ORDER BY (sl.g).path[2] )
)) AS geom
FROM
(SELECT ogc_fid, ST_DumpPoints(geom) AS g -- --
FROM ch11.aussie_tracks) AS sl
ORDER BY ogc_fid, nline, pt_id;

-- <start id="code_upgis_cutlineatpoints"/> --
CREATE OR REPLACE FUNCTION ch11.upgis_cutlineatpoints(
	param_mlgeom geometry, 
	param_mpgeom geometry, 
	param_tol double precision
)
RETURNS geometry AS
$$
DECLARE
    var_resultgeom geometry;
    var_sline geometry;
    var_eline geometry;
    var_perc_line double precision;
    var_refgeom geometry;
    var_pset geometry[] :=  -- <co id="co_code_upgis_cutlineatpoints_1" /> --
		ARRAY(SELECT geom FROM ST_Dump(param_mpgeom));             
    var_lset geometry[] := 
		ARRAY(SELECT geom FROM ST_Dump(param_mlgeom));  
BEGIN

FOR i in 1 .. array_upper(var_pset,1) LOOP -- <co id="co_code_upgis_cutlineatpoints_2" /> --
	FOR j in 1 .. array_upper(var_lset,1) LOOP -- <co id="co_code_upgis_cutlineatpoints_3" /> --
		IF 
			ST_DWithin(var_lset[j],var_pset[i],param_tol) AND -- <co id="co_code_upgis_cutlineatpoints_4" />
			NOT ST_Intersects(ST_Boundary(var_lset[j]),var_pset[i])
		THEN                                 -- <co id="co_code_upgis_cutlineatpoints_5" />
			IF ST_NumGeometries(ST_Multi(var_lset[j])) = 1 THEN 
				var_perc_line := 
				ST_Line_Locate_Point(var_lset[j],var_pset[i]);
				IF var_perc_line BETWEEN 0.0001 and 0.9999 THEN
					var_sline := 
						ST_Line_Substring(var_lset[j],0,var_perc_line);
					var_eline := 
						ST_Line_Substring(var_lset[j],var_perc_line,1);
					var_eline := 
						ST_SetPoint(var_eline,0,ST_EndPoint(var_sline));
					var_lset[j] := ST_Collect(var_sline,var_eline);
				END IF;
			ELSE
				var_lset[j] :=   -- <co id="co_code_upgis_cutlineatpoints_6" />
					upgis_cutlineatpoints(var_lset[j],var_pset[i]);
			END IF;
		END IF;
	END LOOP;
END LOOP;
  
RETURN ST_Union(var_lset);

END;
$$
LANGUAGE 'plpgsql' IMMUTABLE STRICT;
-- <end id="code_upgis_cutlineatpoints"/> --

-- <start id="code_cutlinatpoints_use"/> --
SELECT 
	gid, geom AS orig_geom, 
	(ST_Dump(
	    ch11.upgis_cutlineatpoints(geom, foo.the_pt, 100 )
	    )
	 ).geom AS changed
FROM 
	ch11.stclines_streets AS s 
	CROSS JOIN
    (SELECT ST_SetSRID(ST_Point(6011200,2113500),2227) AS the_pt) AS x
WHERE ST_DWithin(s.geom,x.the_pt,100);
-- <end id="code_cutlinatpoints_use"/> --

-- <start id="code_hexagonal_grid"/> --
WITH 
	center_point(x,y) AS (SELECT -288499, -2718), -- <co id="co_code_hexagonal_grid_1"/> --
	paintbrush(the_hex,the_rect) AS ( -- <co id="co_code_hexagonal_grid_2"/>
		SELECT 
			ST_SetSRID(
				ST_Translate(              
					ST_GeomFromText(
						'POLYGON((
							0 0,64 64,64 128,0 192,   
							-64 128,-64 64,0 0
						))'
					), x, y
				), 2163
			) AS the_hex,
			ST_SetSRID(ST_Translate(CAST(ST_MakeBox2D(ST_Point(-64,0), 
			ST_Point(64,192)) AS geometry), x, y), 2163) AS the_rect
		FROM center_point                              
	)   
SELECT xf.x, yf.y, -- <co id="co_code_hexagonal_grid_3"/> --
	ST_Translate(paintbrush.the_hex, xf.x_hex, yf.y_hex) AS hex_tile,
	ST_Translate(paintbrush.the_rect, xf.x_rect,yf.y_rect) AS rect_tile
FROM 
	(
        SELECT x,
            x*(ST_XMax(the_hex) - ST_XMin(the_hex)) AS x_hex,
            x*(ST_XMax(the_rect) - ST_XMin(the_rect)) AS x_rect
        FROM generate_series(-50, 50) AS x CROSS JOIN paintbrush
    ) AS xf      
	CROSS JOIN 
	(
        SELECT y, 
            y*(ST_YMax(the_hex) - ST_YMin(the_hex)) AS y_hex, 
            y*(ST_YMax(the_rect) - ST_YMin(the_rect)) AS y_rect 
        FROM generate_series(-50, 50) AS y CROSS JOIN paintbrush
    ) AS yf  
    CROSS JOIN 
    paintbrush; 
-- <end id="code_hexagonal_grid"/> --

-- <start id="code_hex_scaling"/> --
SELECT 
    xfactor, yfactor, 
	ST_Scale(hex.geom, xfactor, yfactor) AS scaled_geometry
FROM 
    (
        SELECT ST_GeomFromText(
            'POLYGON((0 0,64 64,64 128,0 192, -64 128,-64 64,0 0))' --  <co id="co_code_hex_scaling_1b"/>
        ) AS geom
    ) AS hex 
    CROSS JOIN 
    (SELECT x*0.5 AS xfactor FROM generate_series(1,4) AS x) AS xf 
    CROSS JOIN
    (SELECT y*0.5 AS yfactor FROM generate_series(1,4) AS y) AS yf; -- <co id="co_code_hex_scaling_2b"/>
-- <end id="code_hex_scaling"/> --

-- <start id="code_scaling_translating"/> --
SELECT xfactor, yfactor, 
    ST_Translate(
        ST_Scale(hex.geom, xfactor, yfactor),
        ST_X(ST_Centroid(geom))*(1 - xfactor),
        ST_Y(ST_Centroid(geom))*(1 - yfactor) 
    ) AS scaled_geometry
FROM
	(
        SELECT ST_GeomFromText(
            'POLYGON((0 0,64 64,64 128,0 192,-64 128, -64 64,0 0))'
        ) AS geom
    ) AS hex 
    CROSS JOIN 
	(SELECT x*0.5 AS xfactor FROM generate_series(1,4) AS x) AS xf 
    CROSS JOIN 
	(SELECT y*0.5 AS yfactor FROM generate_series(1,4) AS y) AS yf;
-- <end id="code_scaling_translating"/> --

-- rotate about centroid --
-- <start id="code_rotate_hex_centroid"/> --
SELECT 
    rotrad/pi()*180 AS deg, 
    ST_Rotate(hex.geom,rotrad, 
    ST_Centroid(hex.geom)) AS rotated_geometry
FROM 
    (
        SELECT ST_GeomFromText(
            'POLYGON((0 0,64 64,64 128,0 192,-64 128,-64 64,0 0))'
        ) AS geom
    ) AS hex
    CROSS JOIN 
    (
        SELECT 2*pi()*x*45.0/360 AS rotrad 
            FROM generate_series(0,6) AS x
    ) AS xf;
-- <end id="code_rotate_hex_centroid"/> --

-- <start id="code_st_collect_geog"/> --
SELECT somefield, ST_Collect(geog::geometry)::geography AS geog 
FROM sometable 
GROUP BY somefield;
-- <end id="code_st_collect_geog"/> --

-- <start id="code_ugeog_simplifypreservetopology"/> --
CREATE OR REPLACE FUNCTION 
    ugeog_SimplifyPreserveTopology(geography, double precision)
RETURNS geography AS
$$
SELECT 
    geography(
        ST_Transform(
            ST_SimplifyPreserveTopology(
                ST_Transform(geometry($1),_ST_BestSRID($1,$1)), -- <co id="co_code_ugeog_simplifypreservetopology_1"/> 
                $2
            ),
        4326)
    )
$$
LANGUAGE sql IMMUTABLE STRICT
COST 300;
-- <end id="code_ugeog_simplifypreservetopology"/> --