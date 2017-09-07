-- <start id="code_output_geom"/> --
SELECT 
    ST_AsGML(geom,5) as GML,
    ST_AsKML(geom,5) As KML,
    ST_AsGeoJSON(geom,5) As GeoJSON,
    ST_AsSVG(geom,0,5) As SVG_Absolute,
    ST_AsSVG(geom,1,5) As SVG_Relative,
    ST_AsX3D(geom,6) As X3D
FROM 
    (SELECT 
        ST_GeomFromText('LINESTRING(2 48 1,0 51 1)',4326) As geom
    ) X;
-- <end id="code_output_geom"/> --

-- <start id="code_geohash"/> --
SELECT i As rad_meters, ST_GeoHash(geog::geometry) as ghash
FROM (
    SELECT i, ST_Buffer(ST_GeogFromText('POINT(2 48)'), i) As geog 
    FROM unnest(ARRAY[0.02,1,1000,10000,50000,150000]) AS i
) As X;
-- <end id="code_geohash"/> --

-- <start id="code_bag_geometries"/> --
SELECT * INTO unconstrained_geoms
FROM (
    VALUES 
        (ST_GeomFromText('POINT(-100 28 1)',4326)),
        (ST_GeomFromText('LINESTRING(-80 28 1,-90 29 1)',4326)),
        (ST_GeomFromText('POLYGONZ((10 28 1,9 29 1,7 30 1,10 28 1))')), 
        (ST_GeomFromText(
            'POLYHEDRALSURFACE(
                ((0 0 0,0 0 1,0 1 1,0 1 0,0 0 0)), 
                ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)),
                ((0 0 0,1 0 0,1 0 1,0 0 1,0 0 0)),
                ((1 1 0,1 1 1,1 0 1,1 0 0,1 1 0)), 
                ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)), 
                ((0 0 1,1 0 1,1 1 1,0 1 1,0 0 1)) 
            )'
        ))
) As z(geom);
-- <end id="code_bag_geometries"/> --

-- <start id="code_typed_geometries"/> --
SELECT geom::geometry(LineString,4326) INTO constrained_geoms
FROM (
    VALUES 
        (ST_GeomFromText('LINESTRING(-80 28, -90 29)', 4326)), 
        (ST_GeomFromText('LINESTRING(10 28, 9 29, 7 30)', 4326 ))
) As x(geom);
-- <end id="code_typed_geometries"/> --

ALTER TABLE constrained_geoms 
ALTER COLUMN geom TYPE geometry(LineString,4326);

-- <start id="code_transforming_kml"/> --
SELECT ST_GeomFromKML(
    '<LineString><coordinates>10,28 9,29 7,30</coordinates></LineString>'
);
-- <end id="code_transforming_kml"/> --

-- <start id="code_canonical_geom_form_short_cast"/> --
SELECT '0101000020E61000008048BF7D1D2059C017B7D100DEB23C40'::geometry;
-- <end id="code_canonical_geom_form_short_cast"/> --

-- <start id="code_autocast_2"/> --
SELECT (ST_Centroid('LINESTRING(1 2,3 4)'));
-- <end id="code_autocast_2"/> --

-- <start id="code_autocast_3"/> --
SELECT ST_Centroid(ST_GeomFromText('LINESTRING(1 2,3 4)'));
-- <end id="code_autocast_3"/> --

-- <start id="code_autocast_4"/> --
SELECT ST_Perimeter('POLYGON((
    145.007 13.581,144.765 13.21,
    144.602 13.2,144.589 13.494,
    144.845 13.705,145.007 13.581
))');
-- <end id="code_autocast_4"/> --

-- <start id="code_st_srid_geom"/> --
SELECT ST_SRID(ST_GeomFromText('POLYGON((1 1,2 2,2 0,1 1))',4326)); -- <co id="co_code_st_srid_geom_1"/> 

SELECT ST_SRID(geom) As srid, COUNT(*) As number_of_geoms -- <co id="co_code_st_srid_geom_2"/> 
FROM sometable 
GROUP BY ST_SRID(geom);

SELECT 
    ST_SRID(geom) As srid, 
    ST_SRID(ST_SetSRID(geom,4326)) as srid_new -- <co id="co_code_st_srid_geom_3"/> 
FROM ( 
    VALUES 
        (ST_GeomFromText('POLYGON((70 20,71 21,71 19,70 20))',4269)), 
        (ST_Point(1,2))
) As X (geom);
-- <end id="code_st_srid_geom"/> --

-- <start id="code_st_transform_geom"/> --
SELECT ST_AsEWKT(
    ST_Transform('SRID=4326;LINESTRING(-73 41,-72 42)'::geometry,32618)
 );
-- <end id="code_st_transform_geom"/> --

-- <start id="code_geog_transform"/> --
SELECT 
    ST_Transform(
        ST_ClosestPoint(
            ST_Transform(geog::geometry,32618),
            ST_Transform(
                'SRID=4326;LINESTRING(-73 41,-72 42)'::geometry,32618
            )
        ),
        4326
    )::geography;
-- <end id="code_geog_transform"/> --

-- <start id="code_geom_geometrytype"/> --
SELECT ST_GeometryType(geom) As new_name, GeometryType(geom) As old_name
FROM (VALUES 
    (ST_GeomFromText('POLYGON((0 0,1 1,0 1,0 0))')),
    (ST_Point(1,2)),
    (ST_MakeLine(ST_Point(1,2), ST_Point(1,2))),
    (ST_Collect(ST_Point(1,2), ST_Buffer(ST_Point(1,2),3))),
    (ST_LineToCurve(ST_Buffer(ST_Point(1,2),3))),
    (ST_LineToCurve(ST_Boundary(ST_Buffer(ST_Point(1,2),3)))),
    (ST_Multi(ST_LineToCurve(ST_Boundary(ST_Buffer(ST_Point(1,2),3)))))
) As x(geom);
-- <end id="code_geom_geometrytype"/> --

-- <start id="code_geom_conditional_type"/> --
SELECT 
    CASE 
        WHEN GeometryType(geom) = 'POLYGON' THEN ST_Area(geom) 
        WHEN GeometryType(geom) = 'LINESTRING' THEN ST_Length(geom) 
        ELSE NULL 
    END As measure 
FROM sometable;
-- <end id="code_geom_conditional_type"/> --

-- <start id="code_geom_coord_dims"/> --
SELECT 
    ST_GeometryType(geom) As type, 
    ST_Dimension(geom) As gdim, 
    ST_CoordDim(geom) as cdim
FROM unconstrained_geoms;
-- <end id="code_geom_coord_dims"/> -- 

-- <start id="code_npoints_numpoints"/> --
SELECT 
    type, 
    ST_NPoints(geom) As npoints, 
    ST_NumPoints(geom) As numpoints
FROM (VALUES 
    ('LinestringM',
        ST_GeomFromEWKT('LINESTRINGM(1 2 3,3 4 5,5 8 7,6 10 11)')
    ),
    ('Circularstring',
        ST_GeomFromText('CIRCULARSTRING(2.5 2.5,4.5 2.5,4.5 4.5)')
    ),
    ('Polygon (Triangle)',
        ST_GeomFromText('POLYGON((0 1,1 -1,-1 -1,0 1))')
    ),
    ('Multilinestring',
        ST_GeomFromText('MULTILINESTRING((1 2,3 4,5 6),(10 20,30 40))')
    ),
    ('Collection', 
        ST_Collect(
            ST_GeomFromText('POLYGON((0 1,1 -1,-1 -1,0 1))'),
            ST_Point(1,3)
        )
    )
) As x(type, geom);
-- <end id="code_npoints_numpoints"/> --

-- <start id="code_length_3dlength"/> --
SELECT ST_Length(geom) As length_2d, ST_3DLength(geom) As length_3d
FROM (
    VALUES 
        (ST_GeomFromText('LINESTRING(1 2 3,4 5 6)')), 
        (ST_GeomFromText('LINESTRING(1 2,4 5)'))) 
As x(geom);
-- <end id="code_length_3dlength"/> --

-- <start id="code_box2d_box3d"/> --
SELECT name, Box2D(geom) As box2d, Box3D(geom) As box3d
FROM (VALUES 
    ('2D Line', 
        ST_GeomFromText(
            'LINESTRING(121.63 25.03,3.03 6.58,-71.06 42.36)',4326
        )
    ),
    ('3D Line', ST_GeomFromText('LINESTRING(1 2 3,3 4 1000.34567)')),
    ('Vert 2D Line', ST_GeomFromText('LINESTRING(1 2,1 4)')),
    ('Point', ST_GeomFromText('POINT(1 2)')),
    ('Polygon', ST_GeomFromText('POLYGON((1 2,3 4,5 6,1 2))')),
    ('Cube',
        ST_GeomFromText(
            'POLYHEDRALSURFACE(
                ((0 0 0,0 0 1,0 1 1,0 1 0,0 0 0)),
                ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)),
                ((0 0 0,1 0 0,1 0 1,0 0 1,0 0 0)),
                ((1 1 0,1 1 1,1 0 1,1 0 0,1 1 0)),
                ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)),
                ((0 0 1,1 0 1,1 1 1,0 1 1,0 0 1)) 
            )'
        )
    )
 )
AS x(name,geom);
-- <end id="code_box2d_box3d"/> --

-- <start id="code_st_boundary"/> --
SELECT object_name,ST_AsText(ST_Boundary(geom)) As WKT
FROM (VALUES 
    ('Simple linestring',
        ST_GeomFromText('LINESTRING(-14 21,0 0,35 26)')
    ),
    ('Non-simple linestring',
        ST_GeomFromText('LINESTRING(2 0,0 0,1 1,1 -1)')
    ),
    ('Closed linestring',
        ST_GeomFromText('
            LINESTRING(
                52 218,139 82,262 207,245 261,207 267,153 207,
                125 235,90 270,55 244,51 219,52 218)'
        )
    ),
    ('Polygon',
        ST_GeomFromText('
            POLYGON((
                52 218,139 82,262 207,245 261,207 267,153 207,
                125 235,90 270,55 244,51 219,52 218))'
        )
    ),
    ('Polygon with holes',
        ST_GeomFromText('
            POLYGON(
                (-0.25 -1.25,-0.25 1.25,2.5 1.25,2.5 -1.25,-0.25 -1.25),
                (2.25 0,1.25 1,1.25 -1,2.25 0),
                (1 -1,1 1,0 0,1 -1))'
        )
    )
)
AS x(object_name,geom);
-- <end id="code_st_boundary"/> --

-- <start id="code_centroid_pointonsurface"/> --
SELECT 
    name, 
    ST_AsEWKT(ST_Centroid(geom)) As centroid, 
    ST_AsEWKT(ST_PointOnSurface(geom)) As point_on_surface
FROM (VALUES 
    ('Multipoint',ST_GeomFromText('MULTIPOINT(-1 1,0 0,2 3)')),
    ('Multipoint 3D',ST_GeomFromText('MULTIPOINT(-1 1 1,0 0 2,2 3 1)')),
    ('Multilinestring',
        ST_GeomFromText('MULTILINESTRING((0 0,0 1,1 1),(-1 1,-1 -1))')
    ),
    ('Polygon',ST_GeomFromEWKT('
        POLYGON(
            (-0.25 -1.25,-0.25 1.25,2.5 1.25,2.5 -1.25,-0.25 -1.25),
            (2.25 0,1.25 1,1.25 -1,2.25 0),
            (1 -1,1 1,0 0,1 -1)
        )')
    )
)
As x(name,geom);
-- <end id="code_centroid_pointonsurface"/> --

-- <start id="code_pointn"/> --
SELECT ST_AsText(
    ST_PointN(ST_GeomFromText('LINESTRING(1 2,3 4,5 8)'),2)
);
-- <end id="code_pointn"/> --

-- <start id="code_st_dump"/> --
WITH foo(gid,geom) As ( -- <co id="code_st_dump_1"/> --
    VALUES (
        1,
        ST_GeomFromText('
            POLYHEDRALSURFACE( 
                ((0 0 0,0 0 1,0 1 1,0 1 0,0 0 0)), 
                ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)),
                ((0 0 0,1 0 0,1 0 1,0 0 1,0 0 0)),
                ((1 1 0,1 1 1,1 0 1,1 0 0,1 1 0)), 
                ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)), 
                ((0 0 1,1 0 1,1 1 1,0 1 1,0 0 1)) 
            )'
        )
    ),
        (
        2,
        ST_GeomFromText('
            GEOMETRYCOLLECTION(
                MULTIPOLYGON(
                    ((2.25 0,1.25 1,1.25 -1,2.25 0)),
                    ((1 -1,1 1,0 0,1 -1))
                ),
                MULTIPOINT(1 2,3 4),
                LINESTRING(5 6,7 8),
                MULTICURVE(CIRCULARSTRING(1 2,0 4,2 8),(1 2,5 6)))'))
 )

SELECT 
    gid, 
    (gdump).path As pos, 
    ST_AsText((gdump).geom) As exploded_geometry  -- <co id="code_st_dump_3"/> --
FROM (SELECT gid, ST_Dump(geom) As gdump FROM foo) As foofoo; -- <co id="code_st_dump_2"/> ---
-- <end id="code_st_dump"/> --

-- <start id="code_whale_spots"/> -- 
SELECT whale, ST_AsEWKT(spot) As spot
FROM (VALUES 
    ('Mr. Whale', ST_SetSRID(ST_Point(-100.499, 28.7015), 4326)), 
    ('Mr. Whale with M as time', 
        ST_SetSRID(ST_MakePointM(-100.499,28.7015,5), 4326)
    ), -- <co id="code_whale_spots_1a"/> --
    ('Mr. Whale with Z as depth', 
        ST_SetSRID(ST_MakePoint(-100.499,28.7015,0.5), 4326)
    ), -- <co id="code_whale_spots_2a"/> --
    ('Mr. Whale with M and Z', 
        ST_SetSRID(ST_MakePoint(-100.499,28.7015,0.5,5), 4326)
    ) -- <co id="code_whale_spots_3a"/> --
) As x(whale, spot);
-- <end id="code_whale_spots"/> -- 

-- <start id="code_compare_simplify_preserve"/> -- 
SELECT 
    pow(2,n) as tolerance, 
    ST_AsText(ST_Simplify(geom, pow(2,n))) As simp1, 
    ST_AsText(ST_SimplifyPreserveTopology(geom, pow(2,n))) As simp2
FROM 
    (SELECT ST_GeomFromText(
        'POLYGON(
            (10 0,20 0,30 10,30 20,20 30,10 30,0 20,0 10,10 0)
        )') As geom) As x 
    CROSS JOIN 
    generate_series(2,4) As n;
-- <end id="code_compare_simplify_preserve"/> --