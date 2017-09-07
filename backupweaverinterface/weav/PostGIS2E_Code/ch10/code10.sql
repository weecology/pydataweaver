-- <start id="code_airports_dwithin"/> --
SELECT name, iso_country, iso_region
FROM ch10.airports
WHERE ST_DWithin(geog, ST_Point(-75.0664, 40.2003)::geography, 100000);
-- <end id="code_airports_dwithin"/> --

-- <start id="code_airports_dwithin_limit"/> --
SELECT ident, name
FROM 
    ch10.airports 
    CROSS JOIN 
    (SELECT ST_Point(-75.0664, 40.2003)::geography AS ref_geog) As r
WHERE ST_DWithin(geog, ref_geog, 100000)
ORDER BY ST_Distance(geog, ref_geog)
LIMIT 5;
-- <end id="code_airports_dwithin_limit"/> --

-- <start id="code_airports_dwithin_distinct_on"> --
SELECT DISTINCT ON (a.ident) -- <co id="co_code_airports_dwithin_distinct_on_1"/> --
    a.ident, a.name As airport, n.name As closest_navaid, 
	(ST_Distance(a.geog,n.geog)/1000)::integer As dist_km
FROM ch10.airports As a LEFT JOIN ch10.navaids As n 
ON ST_DWithin(a.geog, n.geog,100000) -- <co id="co_code_airports_dwithin_distinct_on_2"/> -- 
ORDER BY a.ident, dist_km; -- <co id="co_code_airports_dwithin_distinct_on_3"/> -- 
   
-- <end id="code_airports_dwithin_distinct_on"> --

-- <start id="code_intersect_with_tolerance"/> --
SELECT ST_DWithin(
    ST_GeomFromText(
        'LINESTRING(1 2, 3 4)'
    ),
    ST_Point(3.00001, 4.000001),
    0.0001
);
-- <end id="code_intersect_with_tolerance"/> --



-- Section Intersects with tolerance
SELECT 
    ST_DWithin(
        ST_GeomFromText('LINESTRING(1 2, 3 4)'), 
            ST_Point(3.00001,4.000001),
        0.0001
 ) ;
 
-- <start id="code_indexed_dist_search_1"/> --
SELECT 
    pid, 
    geom 
    <-> 
    ST_Transform(ST_SetSRID(ST_Point(-71.09368, 42.35857),4326),26986)

FROM ch10.land
WHERE land_type = 'apartment'
ORDER BY 
    geom 
    <-> 
    ST_Transform(ST_SetSRID(ST_Point(-71.09368, 42.35857),4326),26986)
LIMIT 10;
--<end id="code_indexed_dist_search_1"/> --

-- <start id="code_indexed_dist_search_2"/> --
SELECT pid
FROM ch10.land
WHERE land_type = 'apartment'
ORDER BY geom <-> (SELECT geom FROM ch10.land WHERE pid = '58-162')
LIMIT 10;
--<end id="code_indexed_dist_search_2"/> --


-- <start id="code_indexed_dist_search_3"/> --
SELECT 
    l.pid, (
        SELECT s.pid 
        FROM ch10.land As s 
        WHERE s.land_type = 'shopping' 
        ORDER BY s.geom <-> l.geom LIMIT 1
    ) As closest_shopping
FROM ch10.land AS l;
-- <end id="code_indexed_dist_search_3"/> --



-- <start id="code_indexed_dist_search_4"/> --
SELECT l.pid, r.pid As n_closest_shopping
FROM 
    ch10.land As l 
    CROSS JOIN LATERAL 
    (
        SELECT s.pid 
        FROM ch10.land AS s
        WHERE s.land_type = 'shopping'
        ORDER BY s.geom <-> l.geom
        LIMIT 3
    ) As r;
-- <end id="code_indexed_dist_search_4"/> --



-- <start id="code_indexed_dist_search_dist_1"/> --
WITH x AS ( -- <co id="code_indexed_dist_search_dist_1_1"/> --
    SELECT 
        pid, 
        geom, 
        (SELECT geom FROM ch10.land WHERE pid = '58-162') As ref_geom
    FROM ch10.land
    WHERE land_type = 'apartment'
    ORDER BY geom <#> 
        (SELECT geom FROM ch10.land AS l WHERE pid = '58-162')
    LIMIT 100
  )
SELECT 
    pid, 
    RANK() OVER(ORDER BY ST_Distance(geom, ref_geom)) As act_r, -- <co id="code_indexed_dist_search_dist_1_2"/> --
    ST_Distance(geom, ref_geom)::numeric(10,3) As act_dist,
    RANK() OVER(ORDER BY geom <#> ref_geom) As bb_r, -- <co id="code_indexed_dist_search_dist_1_3"/> --
    (geom <#> ref_geom)::numeric(10,3) As bb_dist,
    RANK() OVER(ORDER BY geom <-> ref_geom) As bbc_r, -- <co id="code_indexed_dist_search_dist_1_4"/> --
   (geom <-> ref_geom)::numeric(10,3) As bbc_dist
FROM X
ORDER BY act_r  -- <co id="code_indexed_dist_search_dist_1_5"/> --
LIMIT 5;
-- <end id="code_indexed_dist_search_dist_1"/> --

-- <start id="code_school_road_dwithin_n"/> --
SELECT 
    pid, land_type, row_num, road_name, 
    round(CAST(dist_km As numeric),2) As dist_km
FROM (
    SELECT 
        ROW_NUMBER() OVER (
            PARTITION BY l.pid 
            ORDER BY ST_Distance(r.geom,l.geom)
		) As row_num, -- <co id="co_code_school_road_dwithin_n_1" />
		l.pid, l.land_type, r.road_name, 
		ST_Distance(r.geom,l.geom)/1000 As dist_km
    FROM 
		ch10.land As l 
	LEFT JOIN -- <co id="code_school_road_dwithin_n_2" />
        ch10.road As r
	ON ST_DWithin(r.geom,l.geom,500) 
	WHERE l.land_type = 'education'
) As X
WHERE X.row_num < 3 -- <co id="code_school_road_dwithin_n_4" />
ORDER BY pid, row_num;
-- <end id="code_school_road_dwithin_n"/> --

-- <start id="code_indexed_airports_geom_geog"> --
CREATE INDEX idx_airports_geom_gist_cast 
    ON ch10.airports USING gist (geometry(geog));
-- <end id="code_indexed_airports_geom_geog"> --

-- <start id="code_geog_cast_dist_op"/> --
WITH ref As (
    SELECT ST_Point(-75.0664, 40.2003)::geography AS ref_geog ) -- <co id="co_code_geog_cast_dist_op_1"/> --
SELECT ident, name
FROM (
    SELECT ident, name, geog
    FROM ch10.airports
    ORDER BY 
        (SELECT ref_geog::geometry FROM ref) <-> geog::geometry -- <co id="co_code_geog_cast_dist_op_2"/> --
    LIMIT 20
) AS x
ORDER BY ST_Distance(geog,(SELECT ref_geog FROM ref))  -- <co id="co_code_geog_cast_dist_op_4"/> --
LIMIT 5;
-- <end id="code_geog_cast_dist_op"/> --

-- <start id="code_tag_airport_tz"/> --
ALTER TABLE ch10.airports ADD COLUMN tz varchar(30);
UPDATE ch10.airports
SET tz = t.tzid
FROM ch10.tz_world As t
WHERE ST_Intersects(ch10.airports.geog, t.geog);
-- <end id="code_tag_airport_tz"/> --

-- <start id="code_timestamp_airport_tz"/> --
SELECT ident, name, CURRENT_TIMESTAMP AT TIME ZONE tz AS ts_at_airport
FROM ch10.airports
WHERE ident IN('KBOS','KSAN','LIRF','OMDB','ZLXY');
-- <end id="code_timestamp_airport_tz"/> --

-- <start id="code_snap_closest_point"/> --
SELECT DISTINCT ON (p.pid) 
    p.addr_num || ' ' || full_str AS parcel, 
    r.road_name AS road,
    ST_ClosestPoint(p.geom,r.geom) As snapped_point
FROM ch10.land AS p INNER JOIN ch10.road AS r
ON ST_DWithin(p.geom,r.geom,20.0)
ORDER BY p.gid, ST_Distance(p.geom,r.geom);
-- <end id="code_snap_closest_point"/> --
