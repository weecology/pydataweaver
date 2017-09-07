-- <start id="code_ch15_alpha"/> --
SELECT restaurant_name 
FROM restaurants 
WHERE ST_DWithin(ST_GeogFromText(...),restaurants.geog,10*1609) 
ORDER BY ST_Distance(ST_GeogFromText(...),restaurants.geog) 
LIMIT 5;
-- <end id="code_ch15_alpha"/> --

-- <start id="code_ch15_beta"/> --
SELECT restaurant_name 
FROM restaurants 
ORDER BY ST_Distance(ST_GeogFromText(…),restaurants.geog) 
LIMIT 5;
-- <end id="code_ch15_beta"/> --

-- <start id="code_ch15_charlie"/> --
SELECT restaurant_name
FROM restaurants LEFT JOIN roads 
ON ST_DWithin(restaurants.geog,roads.geog,100)
WHERE roads.gid IS NULL;
-- <end id="code_ch15_charlie"/> --

-- <start id="code_ch15_delta"/> --
WITH x AS (
    SELECT restaurant_name, geom FROM restaurants
    ORDER BY ST_GeomFromText(...) <#> restaurants.geom
    LIMIT 100
) 
SELECT restaurant_name FROM x
ORDER BY ST_Distance(ST_GeomFromText(…), restaurants.geom) LIMIT 5;
-- <end id="code_ch15_delta"/> --

-- start id="code_planner_statistics_query" --
SELECT 
	attname As colname, 
	n_distinct, 
	array_to_string(most_common_vals, E'\n') AS common_vals,
	array_to_string(most_common_freqs, E'\n') As dist_freq
FROM pg_stats
WHERE schemaname = 'ch01' AND tablename = 'restaurants';
-- end id="code_planner_statistics_query"  --

-- <start id="code_plan_no_index"/> --
EXPLAIN 
SELECT t.town, r.rt_number
FROM 
	ch15.ma_towns AS t 
	INNER JOIN 
	ch15.ma_roads As r 
	ON ST_Intersects(t.geom,r.geom)
WHERE r.rt_number = '9';
-- <end id="code_plan_no_index"/> --

-- <start id="code_plan_no_index_explain_analyze"/> --
EXPLAIN ANALYZE 
SELECT t.town, r.rt_number
FROM 
	ch15.ma_towns AS t 
	INNER JOIN 
	ch15.ma_roads As r 
	ON ST_Intersects(t.geom,r.geom)
WHERE r.rt_number = '9';
-- <end id="code_plan_no_index_explain_analyze"/> --

-- <start id="code_plan_no_index_explain_analyze_verbose"/> --
EXPLAIN ANALYZE VERBOSE 
SELECT t.town, r.rt_number
FROM 
	ch15.ma_towns AS t 
	INNER JOIN 
	ch15.ma_roads As r 
	ON ST_Intersects(t.geom,r.geom)
WHERE r.rt_number = '9';
-- <end id="code_plan_no_index_explain_analyze_verbose"/> --

-- <start id="code_plan_index_explain_analyze_verbose"/> --
CREATE INDEX idx_ch15_ma_towns_geom
ON ch15.ma_towns USING gist (geom) WITH (FILLFACTOR=90); -- <co id="co_code_plan_index_explain_analyze_verbose_1"/>

CREATE INDEX idx_ch15_ma_roads_geom
ON ch15.ma_roads USING gist (geom) WITH (FILLFACTOR=90);

EXPLAIN ANALYZE VERBOSE 
SELECT t.town, r.rt_number -- <co id="co_code_plan_index_explain_analyze_verbose_2"/>
FROM 
	ch15.ma_towns AS t 
	INNER JOIN 
	ch15.ma_roads As r 
	ON ST_Intersects(t.geom, r.geom)
WHERE r.rt_number = '9';
-- <end id="code_plan_index_explain_analyze_verbose"/> --

-- <start id="code_ch15_echo"> --
CREATE INDEX idx_sometable_active_type 
ON sometable 
USING btree (type) WHERE active = true;
-- <end id="code_ch15_echo"> --

-- <start id="code_ch15_foxtrot"> --
CREATE INDEX idx_ch15_ma_roads_geom_rt_number 
ON ch15.ma_roads
USING gist(geom, rt_number);
-- <end id="code_ch15_foxtrot"> --

-- <start id="code_ch15_gulf"> --
CREATE INDEX idx_sometable_geom_2163 
ON sometable 
USING gist(ST_Transform(geom,2163));
-- <end id="code_ch15_gulf"> --


-- <start id="code_streets_intersect_neighborhoods"/> --
EXPLAIN ANALYZE 
SELECT 
	n.neighborho, 
	(
		SELECT COUNT(*) AS cnt 
        FROM ch15.stclines_streets As s 
        WHERE ST_Intersects(n.geom,s.geom)
	) As cnt
FROM ch15.planning_neighborhoods As n
ORDER BY n.neighborho;
-- <end id="code_streets_intersect_neighborhoods"/> --

-- <start id="code_streets_intersect_neighborhoods_no_subs"/> --
EXPLAIN ANALYZE 
SELECT n.neighborho, COUNT(n.gid) AS cnt
FROM 
	ch15.planning_neighborhoods As n
	LEFT JOIN 
	ch15.stclines_streets As s 
ON ST_Intersects(n.geom,s.geom)
GROUP BY n.neighborho
ORDER BY n.neighborho;
-- <end id="code_streets_intersect_neighborhoods_no_subs"/> --

-- <start id="code_subselect_too_far"/> --
EXPLAIN ANALYZE 
SELECT 
	n.neighborho, 
	(
		SELECT COUNT(*) AS cnt FROM ch15.stclines_streets As s 
			WHERE ST_Intersects(n.geom,s.geom)
	) As cnt,
	(
		SELECT COUNT(*) AS cnt 
		FROM ch15.stclines_streets As s 
		WHERE ST_Intersects(n.geom,s.geom) AND ST_Length(s.geom) > 1000
	) As cnt_gt_1000
FROM ch15.planning_neighborhoods As n
WHERE EXISTS (
    SELECT s.gid 
    FROM ch15.stclines_streets As s 
    WHERE ST_Intersects(n.geom,s.geom)
)
ORDER BY n.neighborho;
-- <end id="code_subselect_too_far"/> --

-- <start id="code_case_instead_subselect"/> --
EXPLAIN ANALYZE 
SELECT 
	n.neighborho, 
	COUNT(s.gid) AS cnt, 
	COUNT(
        CASE WHEN ST_Length(s.geom) > 1000 THEN 1 ELSE NULL END
    ) As cnt_gt_1000
FROM 
	ch15.planning_neighborhoods As n
	INNER JOIN 
	ch15.stclines_streets As s
ON ST_Intersects(n.geom,s.geom)
GROUP BY n.neighborho
ORDER BY n.neighborho;
-- <end id="code_case_instead_subselect"/> --

-- <start id="code_selfjoin_rank_neighbors"/> --
WITH main AS ( -- <co id="co_code_selfjoin_rank_neighbors_1"/>
	SELECT 
		p1.neighborho As nei_1, 
		p2.neighborho As nei_2, 
		p1.geom As p1_geom, 
		p2.geom As p2_geom, 
		p2.gid As p2_gid,
		ST_Distance(p1.geom,p2.geom) As dist, 
		p1.gid As p1_gid
	FROM 
	(
		SELECT neighborho, gid, geom 
        FROM ch15.planning_neighborhoods
        WHERE neighborho = 'Chinatown'
	) As p1
	INNER JOIN 
	ch15.planning_neighborhoods AS p2 
	ON p1.gid <> p2.gid AND ST_DWithin(p1.geom,p2.geom,2500)    
)

SELECT COUNT(p3.gid) As rank, main.nei_2, main.dist
FROM                      
	main -- <co id="co_code_selfjoin_rank_neighbors_2"/>
    INNER JOIN 
	ch15.planning_neighborhoods As p3 
    ON ST_DWithin(main.p1_geom,p3.geom,2500) -- <co id="co_code_selfjoin_rank_neighbors_3"/>
WHERE 
	(main.p2_gid = p3.gid 
		OR ST_Distance(main.p1_geom,p3.geom) < main.dist) 
    AND 
	main.p1_gid <> p3.gid
GROUP BY main.p2_gid, main.nei_2, main.dist
ORDER BY rank, main.nei_2;
-- <end id="code_selfjoin_rank_neighbors"/> --

-- <start id="code_window_frame_rank_neighbors"/> --
SELECT 
	RANK() OVER w_dist As rank, -- <co id="co_code_window_frame_rank_neighbors_1"/>
    p2.neighborho As nei_2, ST_Distance(p1.geom, p2.geom) As dist
FROM 
	ch15.planning_neighborhoods As p1 
	INNER JOIN 
	ch15.planning_neighborhoods As p2
	ON p1.gid <> p2.gid AND ST_DWithin(p1.geom,p2.geom,2500)
WHERE p1.neighborho = 'Chinatown' 
WINDOW w_dist AS (
    PARTITION BY p1.gid ORDER BY ST_Distance(p1.geom, p2.geom)
) -- <co id="co_code_window_frame_rank_neighbors_2"/>
ORDER BY RANK() OVER w_dist, nei_2;
-- <end id="code_window_frame_rank_neighbors"/> --

-- <start id="code_explode_no_subselect_no_lateral"/> --
EXPLAIN ANALYZE VERBOSE 
SELECT 
	p1.neighborho As nei_1,
	(ST_DumpPoints(p1.geom)).geom As geom,
	(ST_DumpPoints(p1.geom)).path[1] As poly_index,
	(ST_DumpPoints(p1.geom)).path[2] As poly_ring_index,
	(ST_DumpPoints(p1.geom)).path[3] As pt_index
FROM ch15.planning_neighborhoods As p1;
-- <end id="code_explode_no_subselect_no_lateral"/> --

-- <start id="code_explode_subselect"/> --
EXPLAIN ANALYZE VERBOSE 
SELECT 
	nei_1, 
	(gp).geom, 
	(gp).path[1] As poly_index, 
	(gp).path[2] As poly_ring_index, 
	(gp).path[3] As pt_index
FROM (
	SELECT p1.neighborho As nei_1, ST_DumpPoints(p1.geom) As gp
	FROM ch15.planning_neighborhoods As p1
) As x;
-- <end id="code_explode_subselect"/> --

-- <start id="code_explode_lateral"/> --
EXPLAIN ANALYZE VERBOSE 
SELECT 
	p1.neighborho As nei_1, 
	(gp).geom, 
	(gp).path[1] As poly_index, 
	(gp).path[2] As poly_ring_index, 
	(gp).path[3] As pt_index
FROM 
	ch15.planning_neighborhoods As p1,
	LATERAL
	ST_DumpPoints(p1.geom) As gp;
-- <end id="code_explode_lateral"/> --

-- <start id="code_ch15_india"/> --
ALTER DATABASE postgis_in_action SET work_mem=120000;
ALTER FUNCTION somefunction(text, text) SET work_mem=10000;
-- <end id="code_ch15_india"/> --

-- <start id="code_ch15_hotel"/> --
CREATE OR REPLACE FUNCTION somefunction(arg1,arg2 ..)
RETURNS type1 AS
....
LANGUAGE 'c' IMMUTABLE STRICT
COST 100 ROWS 2;
-- <end id="code_ch15_hotel"/> --

-- <start id="code_geohash_street"/> --
CREATE INDEX idx_stclines_streets_ghash_street -- <co id="co_code_geohash_street_1"/>
ON ch15.stclines_streets (ST_GeoHash(ST_Transform(geom,4326)),street);
 
CLUSTER ch15.stclines_streets 
	USING idx_stclines_streets_ghash_street; -- <co id="co_code_geohash_street_2"/> 
-- <end id="code_geohash_street"/> --