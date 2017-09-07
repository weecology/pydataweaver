-- start: code_create_ch13_staging --
CREATE SCHEMA ch13_staging;
CREATE SCHEMA ch13;
-- end: code_create_ch13_staging --

-- <start id="code_create_topology_4326"/> --
SELECT CreateTopology('ch13a_topology',4326); 
-- <end id="code_create_topology_4326"/> --

--<start id="code_load_colorado"/> -- 
SELECT TopoGeo_AddLineString(
    'ch13a_topology', 
	ST_GeomFromText(
		'LINESTRING(
			-109.05304 39.195013,
			-109.05304 41.000889,
			-104.897461 40.996484
		)',
		4326
    )
);

SELECT TopoGeo_AddLineString(
	'ch13a_topology',
	ST_GeomFromText(
		'LINESTRING(
		    -104.897461 40.996484,
		    -102.051744 40.996484, 
		    -102.051744 40.003029
		)',
		4326
    )
);

SELECT TopoGeo_AddLineString(
	'ch13a_topology',
	ST_GeomFromText(
		'LINESTRING(
		    -102.051744 40.003029,
		    -102.04874 36.992682,
		    -104.48204 36.992682
		)',
		4326
    )
);
     
SELECT TopoGeo_AddLineString(
	'ch13a_topology',
	ST_GeomFromText(
		'LINESTRING(
		    -104.48204 36.992682,
		    -109.045226 36.999077, 
		    -109.05304 39.195013
		)',
		4326
    )
 );
--<end id="code_load_colorado"/> --	
	
--<start id="code_load_colorado_highway_I-70"/> --
SELECT TopoGeo_AddLineString(
	'ch13a_topology',
	ST_GeomFromText(
		'LINESTRING(
			-109.05304 39.195013, 
			-108.555908 39.108751, 
			-105.021057 39.717751, 
			-102.051744 40.003029
		)',
		4326
    )
 );
--<end id="code_load_colorado_highway_I-70"/> --

--<start id="code_load_colorado_highway_I-25"/> --
SELECT TopoGeo_AddLineString(
	'ch13a_topology',
	ST_GeomFromText(
		'LINESTRING(
			-104.897461 40.996484,
			-105.021057 39.717751,
			-104.798584 38.814031,
			-104.48204 36.992682
		)',
		4326
    )
);
--<end id="code_load_colorado_highway_I-25"/> --

-- <start id="query_list_topologies"/> --
SELECT id, name, srid, precision, hasz FROM topology.topology;
-- <end id="query_list_topologies"/> --

-- <start id="code_highways_topogeom"/> --
CREATE TABLE ch13.highways_topo (highway varchar(20) PRIMARY KEY); 
SELECT AddTopoGeometryColumn(
    'ch13a_topology',
    'ch13',
    'highways_topo',
    'topo',
    'LINESTRING'
);
-- <end id="code_highways_topogeom"/> --

-- <start id="code_highways_createtopogeom"/> --
INSERT INTO ch13.highways_topo (highway, topo) 
VALUES (
    'I70', 
    CreateTopoGeom( -- <co id="co_code_highways_createtopogeom_1"/>
        'ch13a_topology',
        2, -- <co id="co_code_highways_createtopogeom_2"/>
        1, -- <co id="co_code_highways_createtopogeom_3"/>
        '{{5,2},{6,2}}'::topoelementarray -- <co id="co_code_highways_createtopogeom_4"/>
    )
);
-- <end id="code_highways_createtopogeom"/> --
  
-- <start id="code_highways_totopogeom"/> --
INSERT INTO ch13.highways_topo (highway, topo) 
SELECT 
    'I25', 
	toTopoGeom( -- <co id="co_code_highways_totopogeom_1"/>
		ST_GeomFromText(
			'LINESTRING(
                -104.897461 40.996484,
                -105.021057 39.717751,
                -104.798584 38.814031,
                -104.48204 36.992682
            )',
			4326
		), -- <co id="co_code_highways_totopogeom_2"/>
	'ch13a_topology', -- <co id="co_code_highways_totopogeom_3"/>
	1 -- <co id="co_code_highways_totopogeom_4"/>
  );
-- <end id="code_highways_totopogeom"/> --

-- <start id="query_topology_co_topo_elements"/> --
SELECT highway, (topo).*, GetTopoGeomElements(topo) As el
FROM ch13.highways_topo
ORDER BY highway;
-- <end id="query_topology_co_topo_elements"/> --

-- <start id="output_topology_co_topo_elements"/> --
 highway | topology_id | layer_id | id | type |  el
---------+-------------+----------+----+------+-------
 I25     |           1 |        1 |  2 |    2 | {7,2}
 I25     |           1 |        1 |  2 |    2 | {8,2}
 I70     |           1 |        1 |  1 |    2 | {5,2}
 I70     |           1 |        1 |  1 |    2 | {6,2}
-- <end id="output_topology_co_topo_elements"/> --

-- <start id="code_create_ch13_topology"/> --
SELECT CreateTopology('ch13_topology', 32610, 0.05);
-- <end id="code_create_ch13_topology"/> --

-- <start id="code_create_ch13_admin_boundaries_line"/> --
SELECT 
    gid, 
    TopoGeo_AddLineString(
        'ch13_topology', ST_Transform(geom, 32610)
    ) As edge_id -- <co id="co_code_create_ch13_admin_boundaries_line_1"/>
FROM (
    SELECT gid, (ST_Dump(geom)).geom FROM ch13_staging.cityboundary
) As f; -- <co id="co_code_create_ch13_admin_boundaries_line_2"/>
-- <end id="code_create_ch13_admin_boundaries_line"/> --

-- <start id="code_count_faces_edges_nodes_relations"/> --
SELECT 'faces' As type, COUNT(*) As num FROM ch13_topology.face
UNION ALL
SELECT 'edges' As type, COUNT(*) As num FROM ch13_topology.edge
UNION ALL
SELECT 'nodes' As type, COUNT(*) As num FROM ch13_topology.node
UNION ALL
SELECT 'relations' As type, COUNT(*) As num FROM ch13_topology.relation;
-- <end id="code_count_faces_edges_nodes_relations"/> --

-- <start id="code_create_topogeo_addpolygon_municipal"/> --
SELECT 
    gid, 
    TopoGeo_AddPolygon(
        'ch13_topology', ST_Transform(geom, 32610), 0.05
    ) As face_id
FROM (
    SELECT 
        gid, 
        (ST_Dump(geom)).geom 
    FROM ch13_staging.neighbourhoods
) As f;
-- <end id="code_create_topogeo_addpolygon_municipal"/> --

-- <start id="code_build_topogeometry_columns_prim_child"/> --
CREATE TABLE ch13.neighbourhoods (feat_name varchar(50) primary key);
SELECT AddTopoGeometryColumn(
    'ch13_topology',
    'ch13',    
    'neighbourhoods',
    'topo',
    'MULTIPOLYGON'
); -- <co id="co_code_build_topogeometry_columns_prim_child_1"/>
  
CREATE TABLE ch13.cities (feat_name varchar(150) primary key);
SELECT AddTopoGeometryColumn(
    'ch13_topology', 
    'ch13',   
    'cities',
    'topo',
    'MULTIPOLYGON',
    1
);  -- <co id="co_code_build_topogeometry_columns_prim_child_2"/>
-- <end id="code_build_topogeometry_columns_prim_child"/> --

-- <start id="code_totopogeom_nei"/> --
INSERT INTO ch13.neighbourhoods (feat_name, topo)
SELECT  
    neighbourh,  
    toTopoGeom(
        ST_Transform(geom, 32610), 'ch13_topology', 1, 0.05
    )
FROM ch13_staging.neighbourhoods;
-- <end id="code_totopogeom_nei"/> --

-- <start id="code_createtopogeom_city"/> --
INSERT INTO ch13.cities (feat_name, topo)
SELECT 
    'Victoria',    
    CreateTopoGeom(
        'ch13_topology',
        3, -- <co id="co_code_createtopogeom_city_1"/>
        2, -- <co id="co_code_createtopogeom_city_2"/>
        (
            SELECT TopoElementArray_Agg(
				ARRAY[(topo).id,(topo).layer_id]
			) -- <co id="co_code_createtopogeom_city_3"/>
            FROM ch13.neighbourhoods
        )
);
-- <end id="code_createtopogeom_city"/> --

-- <start id="code_city_asgeom"/> --
SELECT topo::geometry FROM ch13.cities WHERE feat_name = 'Victoria';
-- <end id="code_city_asgeom"/> --

-- <start id="code_getfacegeom_city"/> --
SELECT face_id, ST_GetFaceGeometry('ch13_topology', face_id)
FROM (
    SELECT (GetTopoGeomElements(topo))[1] As face_id 
    FROM ch13.cities 
    WHERE feat_name = 'Victoria'
) As x;
-- <end id="code_getfacegeom_city"/> --

--<start id="code_count_faces_neighbourhood"/> --
SELECT feat_name, COUNT(face_id) As num_faces, 
    MIN(
        ST_Area(ST_GetFaceGeometry('ch13_topology',face_id))
    )::numeric(10,2) As min_area,
    MAX(
        ST_Area(ST_GetFaceGeometry('ch13_topology',face_id))
    )::numeric(10,2) As max_area
FROM (
    SELECT feat_name, (GetTopoGeomElements(topo))[1] As face_id 
	FROM ch13.neighbourhoods
) As x
GROUP BY feat_name 
HAVING COUNT(face_id) > 1
ORDER BY COUNT(face_id) DESC;
-- <end id="code_count_faces_neighbourhood"/> --

-- <start id="code_remove_small_pockets"/> --
DO 
LANGUAGE plpgsql 
$$
DECLARE r record; var_face integer;
BEGIN
    FOR r IN ( 
    SELECT DISTINCT abs(
        (ST_GetFaceEdges(
            'ch13_topology',face_id)
        ).edge
    ) As edge 
    FROM (
        SELECT feat_name, (GetTopoGeomElements(topo))[1] As face_id 
        FROM ch13.neighbourhoods
    ) As x
    WHERE ST_Area(ST_GetFaceGeometry('ch13_topology',face_id)) < 55000
     ) 
    LOOP
        BEGIN
            var_face := ST_RemEdgeNewFace('ch13_topology',r.edge);
            EXCEPTION
                WHEN OTHERS THEN
            RAISE WARNING 'Failed remove edge: %, %', r.edge, SQLERRM;
        END;
    END LOOP;
END
$$;
-- <end id="code_remove_small_pockets"/> -

-- <start id="code_determine_faces_shared"/> --
SELECT (GetTopoGeomElements(topo))[1] As face_id -- <co id="co_code_determine_faces_shared_1"/>
FROM ch13.neighbourhoods
WHERE feat_name = 'North Park' 
INTERSECT
SELECT (GetTopoGeomElements(topo))[1] As face_id  -- <co id="co_code_determine_faces_shared_3"/>
FROM ch13.neighbourhoods
WHERE feat_name = 'Burnside';
-- <end id="code_determine_faces_shared"/> --

-- <start id="code_removing_faces_topogeom"/> --
DELETE FROM ch13_topology.relation AS r -- <co id="co_code_removing_faces_topogeom_1"/>
WHERE EXISTS (
	SELECT topo -- <co id="co_code_removing_faces_topogeom_2"/>
	FROM ch13.neighbourhoods As n 
	WHERE 
		feat_name = 'North Park' AND 
		(topo).id = r.topogeo_id AND 
		r.element_id = 23 AND 
		r.element_type = 3
);

DELETE FROM ch13_topology.relation AS r -- <co id="co_code_removing_faces_topogeom_3"/>
WHERE EXISTS (
	SELECT topo 
	FROM ch13.neighbourhoods As n 
	WHERE 
		feat_name = 'Burnside' AND 
		(topo).id = r.topogeo_id AND 
		r.element_id = 31 AND 
		r.element_type = 3
);
-- <end id="code_removing_faces_topogeom"/> --

-- <start id="code_addtopogeomcolumn_streets"/> --
CREATE TABLE ch13.streets (
	gid integer primary key, 
	feat_name varchar(50), 
	access varchar(20), 
	rd_class varchar(20), 
	max_speed numeric(10,2)
); -- <co id="co_code_addtopogeomcolumn_streets_1"/>
  
SELECT AddTopoGeometryColumn(
	'ch13_topology',
	'ch13',
	'streets',
	'topo',
	'MULTILINESTRING'
); -- <co id="co_code_addtopogeomcolumn_streets_2"/>
  
CREATE TABLE ch13.log_street_failures (
	gid integer primary key,
	error text
); -- <co id="co_code_addtopogeomcolumn_streets_3"/> 
-- <end id="code_addtopogeomcolumn_streets"/> --  

-- <start id="code_totopogeom_streets"/> --
CREATE FUNCTION ch13.load_streets() RETURNS void AS
$$
DECLARE r record;
BEGIN
    FOR r IN 
		SELECT * 
		FROM ch13_staging.streetcentrelines -- <co id="co_code_totopogeom_streets_1"/>
        ORDER BY gid 
		LIMIT 500 OFFSET (SELECT MAX(gid) from ch13.streets)
	LOOP  
		BEGIN
			INSERT INTO ch13.streets (
				gid,feat_name,access,rd_class,max_speed,topo) -- <co id="co_code_totopogeom_streets_2"/>
			SELECT 
				r.gid,r.streetname,r.access,r.rd_class,
				r.max_speed::numeric,
				toTopoGeom(ST_Transform(ST_Force2D(r.geom),32610),-- <co id="co_code_totopogeom_streets_3"/>
      'ch13_topology',3,0.05); -- <co id="co_code_totopogeom_streets_4"/>
			EXCEPTION WHEN OTHERS THEN
				INSERT INTO ch13.log_street_failures (gid,error) -- <co id="co_code_totopogeom_streets_5"/>
				VALUES (r.gid,SQLERRM);
				RAISE WARNING 
					'Loading of record % failed: %',
					r.gid,
					SQLERRM;
		END;
    END LOOP;
END
$$
LANGUAGE plpgsql;
-- <end id="code_totopogeom_streets"/> --

-- <start id="code_pgscript_loop_street_insert"/> --
DECLARE @I; -- <co id="co_pgscript_loop_street_insert_1"/>
SET @I = 0;
WHILE @I < 10 -- <co id="co_pgscript_loop_street_insert_2"/>
BEGIN
	SELECT ch13.load_streets(); -- <co id="co_pgscript_loop_street_insert_3"/>
	SET @I = @I + 1; -- <co id="co_pgscript_loop_street_insert_4"/>
	PRINT @I;
END
-- <end id="code_pgscript_loop_street_insert"/> --

-- <start id="code_geom_simplification"/> --
SELECT feat_name, ST_Simplify(topo::geometry,150) As geom_simp 
FROM ch13.neighbourhoods;
-- <end id="code_geom_simplification"/> -- 

-- <start id="code_topo_simplification"/> --
SELECT feat_name, ST_Simplify(topo,150) As topo_simp 
FROM ch13.neighbourhoods;
-- <end id="code_topo_simplification"/> -- 

-- <start id="code_validatetopology_victoria"/> --
SELECT ValidateTopology('ch13_topology');
-- <end id="code_validatetopology_victoria"/> --

-- <start id="code_topologysummary_victoria"/> --
SELECT TopologySummary('ch13_topology');
-- <end id="code_topologysummary_victoria"/> --