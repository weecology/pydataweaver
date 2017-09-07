-- <start id="code_box2d_geometry"/> --
SELECT ex_name, Box2D(geom) As bbox2d , geom
FROM (
VALUES
    ('A line', ST_GeomFromEWKT('LINESTRING (0 0, 1 1)')),
    ('A multipoint', ST_GeomFromText('MULTIPOINT (4.4 4.75, 5 5)')),
    ('A square', ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))'))
)
AS x(ex_name, geom);
-- <end id="code_box2d_geometry"/> --

-- <start id="code_segment_linestring_polygon"/> --
SELECT 
	ST_Intersects(g.geom1,g.geom2) As intersect, 
	GeometryType(ST_Intersection(g.geom1,g.geom2)) As intersectione
FROM (
	SELECT 
		ST_GeomFromText('
			POLYGON((
				2 4.5,3 2.6,3 1.8,2 0,
				-1.5 2.2,0.056 3.222,
				-1.5 4.2,2 6.5,2 4.5
			))'
		) As geom1, 
		ST_GeomFromText('LINESTRING(-0.62 5.84,-0.8 0.59)') As geom2
) AS g;
-- <end id="code_segment_linestring_polygon"/> --

-- <start id="code_sales_region_dicing"/> --
SELECT 
	x || ' ' || y As grid_x_y, -- <co id="co_code_sales_region_dicing_1"/> --
	CAST(
		ST_MakeBox2d(
			ST_Point(-1.5 + x, 0 + y), 
			ST_Point(-1.5 + x + 2, 0 + y + 2)
		) As geometry
	) As geom2
FROM generate_series(0,3,2) As x CROSS JOIN generate_series(0,6,2) As y;

SELECT 
	ST_GeomFromText(
		'POLYGON((
			2 4.5,3 2.6,3 1.8,2 0,-1.5 2.2,0.056 3.222,-1.5 4.2,2 6.5,
			2 4.5
		))'
	) As geom1;  -- <co id="co_code_sales_region_dicing_2"/> --

SELECT 
	CAST(x AS text) || ' ' || CAST(y As text) As grid_xy,  -- <co id="co_code_sales_region_dicing_3"/> --
	ST_AsText(ST_Intersection(g1.geom1, g2.geom2)) As intersect_geom
FROM (
	SELECT 
		ST_GeomFromText(
			'POLYGON((
				2 4.5,3 2.6,3 1.8,2 0,
				-1.5 2.2,0.056 3.222,
				-1.5 4.2,2 6.5,2 4.5
			))'
		) As geom1
	) As g1
	INNER JOIN (
	SELECT x, y, ST_MakeEnvelope(-1.5+x,0+y,-1.5+x+2,0+y+2) As geom2
	FROM 
		generate_series(0,3,2) As x 
		CROSS JOIN 
		generate_series(0,6,2) As y
	) As g2 
ON ST_Intersects(g1.geom1,g2.geom2);
-- <end id="code_sales_region_dicing"/> --

-- <start id="code_house_red_carpet_guards"/> --
CREATE TABLE example_set(ex_name varchar(150) PRIMARY KEY,
    geom geometry);
INSERT INTO example_set(ex_name, geom)
VALUES 
    (
        'A polygon with hole', 
        ST_GeomFromText(
            'POLYGON(
                (110 180, 110 335,184 316,260 335,260 180,209 212.51,
                110 180), (160 280,200 240, 220 280,160 280)
            )'
        )
    ),
    ('A point', ST_GeomFromText('POINT(110 245)')), 
    (
        'A linestring',
        ST_GeomFromText('LINESTRING(110 245,200 260, 227 309)')
    ),
    ('A multipoint', ST_GeomFromText('MULTIPOINT(110 245,200 260)'));
-- <end id="code_house_red_carpet_guards"/> --

-- <start id="code_contains_intersects"/> --
SELECT 
    A.ex_name As a_name, B.ex_name As b_name, 
    ST_Contains(A.geom,B.geom) As a_co_b, 
    ST_Intersects(A.geom,B.geom) As a_in_b
FROM example_set As A CROSS JOIN example_set As B;
-- <end id="code_contains_intersects"/> --

-- <start id="code_covers_contains"/> --
SELECT 
    A.ex_name As a_name, B.ex_name As b_name, 
    ST_Covers(A.geom,B.geom) As a_co_b,
    ST_Intersects(A.geom,B.geom) As a_in_b
FROM example_set As A CROSS JOIN example_set As B
WHERE NOT (ST_Covers(A.geom,B.geom) = ST_Contains(A.geom,B.geom));
-- <end id="code_covers_contains"/> --

-- <start id="code_containsproperly_contains"/> --
SELECT 
    A.ex_name As a_name, B.ex_name As b_name,
    ST_ContainsProperly(A.geom,B.geom) As a_co_b,
    ST_Intersects(A.geom,B.geom) As a_in_b
FROM example_set As A CROSS JOIN example_set As B
WHERE NOT ( ST_ContainsProperly(A.geom,B.geom) = 
    ST_Contains(A.geom,B.geom) );
-- <end id="code_containsproperly_contains"/> --

-- <start id="code_touches_contains"/> --
SELECT 
    A.ex_name As a_name,B.ex_name As b_name, 
    ST_Touches(A.geom,B.geom) As a_tou_b, 
    ST_Contains(A.geom,B.geom) As a_co_b
FROM example_set As A CROSS JOIN example_set As B
WHERE ST_Touches(A.geom,B.geom) ;
-- <end id="code_touches_contains"/> --

-- <start id="code_crosses"/> --
SELECT 
    A.ex_name As a_name,B.ex_name As b_name, 
    ST_Crosses(A.geom,B.geom) As a_cr_b, 
    ST_Contains(A.geom,B.geom) As a_co_b
FROM example_set As A CROSS JOIN example_set As B
WHERE ST_Crosses(A.geom,B.geom) ;
-- <end id="code_crosses"/> --



-- <start id="code_orderingequals_equals"/> --
SELECT 
    ex_name, 
    ST_OrderingEquals(geom,geom) As g_oeq_g, 
    ST_OrderingEquals(geom, ST_Reverse(geom)) As g_oeq_rev,
    ST_OrderingEquals(geom, ST_Multi(geom)) AS g_oeq_m,
    ST_Equals(geom, geom) As g_seq_g,
    ST_Equals(geom, ST_Multi(geom)) As g_seq_m
FROM (
VALUES 
    ('A 2D linestring', ST_GeomFromText('LINESTRING(3 5,2 4,2 5)')),
    ('A point', ST_GeomFromText('POINT(2 5)')), 
    ('A triangle', ST_GeomFromText('POLYGON((3 5,2.5 4.5,2 5,3 5))')),
    (
        'An invalid polygon', 
        ST_GeomFromText('POLYGON((2 0,0 0,1 1,1 -1,2 0))')
    )
)
AS foo(ex_name, geom);
-- <end id="code_orderingequals_equals"/> --

-- <start id="code_box_equals"/> --
SELECT 
    ST_GeomFromText('LINESTRING (0 0, 1 1)') 
    = 
    ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))');
-- <end id="code_box_equals"/> --

-- <start id="code_orderingequals"/> --
SELECT ST_OrderingEquals(
    ST_GeomFromText('LINESTRING (0 0, 1 1)'),
    ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
);
-- <end id="code_orderingequals"/> --

-- <start id="code_boundingbox_distinct"/> --
SELECT ST_AsText(geom)   -- <co id="co_code_boundingbox_distinct_1"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom);

SELECT ST_AsText(geom)  -- <co id="co_code_boundingbox_distinct_2"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1)')
    UNION
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom);

SELECT DISTINCT geom -- <co id="co_code_boundingbox_distinct_3"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')

) As x(geom);

SELECT DISTINCT ST_AsText(geom)  -- <co id="co_code_boundingbox_distinct_4"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom);
-- <end id="code_boundingbox_distinct"/> --

-- <start id="code_countdistinct_notdistinct"/> --
SELECT COUNT(DISTINCT geom)  -- <co id="co_code_countdistinct_notdistinct_1"/> --
 FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom);

SELECT COUNT(DISTINCT geom)  -- <co id="co_code_countdistinct_notdistinct_2"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1.1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')

) As x(geom);

SELECT geom    -- <co id="co_code_countdistinct_notdistinct_3"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1.1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom)
GROUP BY geom;

SELECT geom  -- <co id="co_code_countdistinct_notdistinct_4"/> --
FROM (
    SELECT ST_GeomFromText('LINESTRING (0 0, 1 1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom)
GROUP BY geom;
-- <end id="code_countdistinct_notdistinct"/> --


-- <start id="code_guarantee_unique_geometries"/> --
CREATE TABLE mygeom_unique(geom geometry);
INSERT INTO mygeom_unique(geom)
SELECT CAST(geom As text)
FROM (
    SELECT ST_GeomFromEWKT('LINESTRING (0 0, 1 1)')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
    UNION ALL
    SELECT ST_GeomFromText('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
) As x(geom)
GROUP BY CAST(geom As text);
-- <end id="code_guarantee_unique_geometries"/> --

-- <start id="code_st_relate1"/> --
WITH example_set (ex_name,geom) AS (
    SELECT ex_name, geom
    FROM (
        VALUES
            ('A 2D line', 
            ST_GeomFromText('LINESTRING(3 5, 2.5 4.25, 1.6 5)')),
            ('A point', 
            ST_GeomFromText('POINT(1.6 5)')),
            ('A triangle',
            ST_GeomFromText('POLYGON((3 5, 2.5 4.25, 1.9 4.9, 3 5))'))
    ) AS x(ex_name, geom)
)

SELECT 
    A.ex_name As a_name, B.ex_name As b_name,
    ST_Relate(A.geom, B.geom) As relates,
    ST_Intersects(A.geom, B.geom) As intersects, 
    ST_Relate(A.geom, B.geom, 'FF*FF****') As relate_disjoint,
    NOT ST_Relate(A.geom, B.geom, 'FF*FF****') As relate_intersects
FROM example_set As A CROSS JOIN example_set As B;  
-- <end id="code_st_relate1"/> --