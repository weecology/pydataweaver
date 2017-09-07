-- <start id="code_partition_roads_states"/> --
CREATE TABLE ch14.roads(
    gid serial PRIMARY KEY,
    road_name character varying(100),
    geom geometry(LINESTRING,4269), state varchar(2)
);

CREATE TABLE ch14.roads_NE (CONSTRAINT pk PRIMARY KEY (gid)) -- <co id="co_code_partition_roads_states_1"/>
INHERITS (ch14.roads); 

ALTER TABLE ch14.roads_NE 
ADD CONSTRAINT chk CHECK (state IN ('MA','ME','NH','VT','CT','RI')); -- <co id="co_code_partition_roads_states_2"/>

CREATE TABLE ch14.roads_SW (CONSTRAINT pk_roads PRIMARY KEY (gid))
INHERITS (ch14.roads);

ALTER TABLE ch14.roads_SW
ADD CONSTRAINT chk CHECK (state IN ('AZ','NM','NV'));

SELECT gid, road_name, geom FROM ch14.roads WHERE state = 'MA'; -- <co id="co_code_partition_roads_states_3"/>
-- <end id="code_partition_roads_states"/> --

-- <start id="code_paris_arrondissements_alter"/> --
ALTER TABLE ch14.arrondissements 
ALTER COLUMN geom TYPE geometry(MultiPolygon,32631)
USING ST_Transform(geom,32631);

ALTER TABLE ch14.arrondissements 
ADD COLUMN ar_num integer;

UPDATE ch14.arrondissements 
SET ar_num = (regexp_matches(name, E'[0-9]+'))[1]::integer;
-- <end id="code_paris_arrondissements_alter"/> --

-- <start id="code_paris_arrondissements_hetero"/> --
CREATE TABLE ch14.paris_hetero (
    gid serial NOT NULL, 
    osm_id bigint, 
    geom geometry(Geometry,32631),
    ar_num integer,
    tags hstore,
    CONSTRAINT paris_hetero_pk 
    PRIMARY KEY (gid)
);
-- <end id="code_paris_arrondissements_hetero"/> --

-- <start id="code_region_tagging_arrondissement"/> --
INSERT INTO ch14.paris_hetero (osm_id, geom, ar_num, tags) -- <co id="co_code_region_tagging_arrondissement_1"/>
SELECT o.osm_id, ST_Intersection(o.geom,a.geom) As geom, 
    a.ar_num, o.tags
FROM                                   
    (
        SELECT osm_id, ST_Transform(way,32631) As geom, tags 
        FROM ch14_staging.planet_osm_line
    ) AS o
    INNER JOIN 
    ch14.arrondissements AS A
    ON (ST_Intersects(o.geom, a.geom));
CREATE INDEX idx_paris_hetero_geom 
ON ch14.paris_hetero USING gist(geom); -- <co id="co_code_region_tagging_arrondissement_2"/>
CREATE INDEX idx_paris_hetero_tags 
ON ch14.paris_hetero USING gist(tags);
VACUUM ANALYZE ch14.paris_hetero;                          
-- <end id="code_region_tagging_arrondissement"/> --

-- <start id="code_compte"/> --
SELECT ar_num, COUNT(DISTINCT osm_id) As compte
FROM ch14.paris_hetero
GROUP BY ar_num;
-- <end id="code_compte"/> --

-- <start id="code_vw_paris_points"/> --
CREATE OR REPLACE VIEW ch14.vw_paris_points AS 
SELECT 
    gid, osm_id, ar_num, geom,
    tags->'name' As place_name,
    tags->'tourism' As tourist_attraction
FROM ch14.paris_hetero
WHERE ST_GeometryType(geom) = 'ST_Point';
-- <end id="code_vw_paris_points"/> --

-- <start id="code_vw_paris_points_tmod"/> --
CREATE OR REPLACE VIEW ch14.vw_paris_points_tmod 
    WITH (security_barrier=true) AS -- <co id="co_code_vw_paris_points_tmod_1"/>
    SELECT 
        gid, osm_id, ar_num, 
        CAST(geom As geometry(POINT,32631)) As geom, -- <co id="co_code_vw_paris_points_tmod_2"/>
        tags->'name' As place_name,
        tags->'tourism' As tourist_attraction
    FROM ch14.paris_hetero
    WHERE ST_GeometryType(geom) = 'ST_Point';

CREATE INDEX idx_paris_hetero_geom_pt ON ch14.paris_hetero -- <co id="co_code_vw_paris_points_tmod_3"/>
USING gist ( (geom::geometry(POINT,32631)) )
WHERE ST_GeometryType(geom) = 'ST_Point';
-- <end id="code_vw_paris_points_tmod"/> --

-- <start id="code_paris_tmod"/> --
SELECT * 
FROM ch14.vw_paris_points_tmod 
WHERE ST_DWithin(geom,ST_SetSRID(ST_Point(453121,5413887),32631),4000);
-- <end id="code_paris_tmod"/> --

-- <start id="code_paris_points_homo"/> --
CREATE TABLE ch14.paris_points(
    gid SERIAL PRIMARY KEY, 
    osm_id bigint,
    ar_num integer, 
    feature_name varchar(200),
    feature_type varchar(50), 
    geom geometry(Point, 32631)
); -- <co id="co_code_paris_points_homo_1a"/> --

INSERT INTO ch14.paris_points (
	osm_id,	ar_num,	geom,
	feature_name, feature_type
) -- <co id="co_code_paris_points_homo_2a"/>
SELECT 
    osm_id, ar_num, geom, 
    tags->'name' As feature_name, 
    COALESCE(
        tags->'tourism',
        tags->'railway',
        tags->'station',
        'other'
    )::varchar(50) As feature_type
FROM ch14.paris_hetero
WHERE ST_GeometryType(geom) = 'ST_Point';
-- <end id="code_paris_points_homo"/> --

-- <start id="code_14_alpha"/> --
SELECT ar_num, COUNT(DISTINCT osm_id) As compte 
FROM (
    SELECT ar_num, osm_id FROM paris_points
    UNION ALL 
    SELECT ar_num, osm_id FROM paris_polygons
    UNION ALL
    SELECT ar_num, osm_id FROM paris_linestrings
) As X
GROUP BY ar_num;
-- <end id="code_14_alpha"/> --

-- <start id="code_paris_parent"/> --
CREATE TABLE ch14.paris (
    gid SERIAL PRIMARY KEY, 
    osm_id bigint, 
    ar_num integer, 
    feature_name varchar(200), 
    feature_type varchar(50), 
    geom geometry(geometry, 32631)
);
-- <end id="code_paris_parent"/> --

-- <start id="code_paris_polygons_child"/> --
CREATE TABLE ch14.paris_polygons (
    tags hstore, -- <co id="co_code_paris_polygons_child_1"/>
    CONSTRAINT paris_polygons_pk 
    PRIMARY KEY (gid)
)
INHERITS (ch14.paris);

ALTER TABLE ch14.paris_polygons NO INHERIT ch14.paris; -- <co id="co_code_paris_polygons_child_2"/>

INSERT INTO ch14.paris_polygons (
    osm_id,ar_num,geom,tags,
    feature_name,feature_type
)   -- <co id="co_code_paris_polygons_child_3"/>
SELECT 
    osm_id, ar_num, ST_Multi(geom) As geom, tags, 
    tags->'name',
    COALESCE(
        tags->'tourism',
        tags->'railway', 
        'other'
    )::varchar(50) As feature_type
FROM ch14.paris_hetero
WHERE ST_GeometryType(geom) LIKE '%Polygon';

SELECT populate_geometry_columns(
	'ch14.paris_polygons'::regclass,
	false
); -- <co id="co_code_paris_polygons_child_4"/>
ALTER TABLE ch14.paris_polygons INHERIT ch14.paris; -- <co id="co_code_paris_polygons_child_5"/> --
-- <end id="code_paris_polygons_child"/> --

-- <start id="code_paris_lines_child"/> --
CREATE TABLE ch14.paris_linestrings ( -- <co id="co_code_paris_lines_child_1"/>
    CONSTRAINT paris_linestrings_pk 
    PRIMARY KEY (gid)    
) INHERITS (ch14.paris);                               

ALTER TABLE ch14.paris_linestrings -- <co id="co_code_paris_lines_child_2"/>
ADD CONSTRAINT enforce_geotype_geom 
    CHECK (geometrytype(geom) = 'LINESTRING'::text);              
-- <end id="code_paris_lines_child"/> --

-- <start id="code_14_bravo"/> --
SELECT ar_num, COUNT(DISTINCT osm_id) As compte 
FROM ch14.paris 
GROUP BY ar_num;
-- <end id="code_14_bravo"/> --

-- <start id="code_14_charlie"/> --
SELECT ar_num, COUNT(DISTINCT osm_id) As compte
FROM ch14.paris_polygons
GROUP BY ar_num;
-- <end id="code_14_charlie"/> --

-- <start id="code_paris_point_child_adopt"/> --
ALTER TABLE ch14.paris_points DROP COLUMN gid; -- <co id="co_code_paris_point_child_adopt_1"/>
ALTER TABLE ch14.paris_points 
    ADD COLUMN gid integer -- <co id="co_code_paris_point_child_adopt_2"/>
        PRIMARY KEY NOT NULL DEFAULT nextval('ch14.paris_gid_seq');  
ALTER TABLE ch14.paris_points 
ALTER COLUMN geom TYPE geometry(geometry,32621);
  
SELECT populate_geometry_columns('ch14.paris_points', false);

ALTER TABLE ch14.paris_points INHERIT ch14.paris;  -- <co id="co_code_paris_point_child_adopt_3"/>
CREATE INDEX idx_paris_points_geom 
ON ch14.paris_points USING gist (geom); -- <co id="co_code_paris_point_child_adopt_4"/>
-- <end id="code_paris_point_child_adopt"/> --

-- <start id="code_14_delta"/> --
CREATE OR REPLACE VIEW ch14.subways AS
SELECT gid, osm_id, ar_num, feature_name, geom 
FROM ch14.paris_points                              
WHERE feature_type = 'subway';
-- <end id="code_14_delta"/> --

-- <start id="code_14_echo"/> --
UPDATE ch14.subways 
SET feature_name = 'subway 1' 
WHERE osm_id = 243496729;
-- <end id="code_14_echo"/> --

-- <start id="code_14_foxtrot"/> --
DELETE FROM ch14.subways WHERE feature_name = 'subway 1';
-- <end id="code_14_foxtrot"/> --

-- <start id="code_14_gulf"/> --
ALTER VIEW ch14.subways ALTER COLUMN feature_name SET DEFAULT 'subway';
-- <end id="code_14_gulf"/> --



-- <start id="code_rule_subway_insert"/> --
CREATE OR REPLACE RULE rule_subway_insert AS                  
ON INSERT TO ch14.subways
DO INSTEAD 
    INSERT INTO ch14.paris_points (
        gid, osm_id, ar_num, feature_name, feature_type, geom
    )
    VALUES (
        DEFAULT, 
        NEW.osm_id, 
        NEW.ar_num, 
        NEW.feature_name,
        'subway', 
        NEW.geom
    );                  
-- <end id="code_rule_subway_insert"/> --

-- <start id="code_reinsert_subway"/> --
INSERT INTO ch14.subways(osm_id, geom)
SELECT osm_id, geom
FROM ch14.paris_hetero WHERE osm_id = 243496729;
-- <end id="code_reinsert_subway"/> --

-- <start id="code_paris_rejects_table"/> --
CREATE TABLE ch14.paris_rejects (
    gid integer NOT NULL PRIMARY KEY,
    osm_id integer,
    ar_num integer,
    feature_name varchar(200),
    feature_type varchar(50),
    geom geometry, tags hstore
);
-- <end id="code_paris_rejects_table"/> --

-- <start id="code_trigger_paris_insert"/> --
CREATE OR REPLACE FUNCTION ch14.trigger_paris_insert() 
RETURNS trigger AS
$$
DECLARE 
    var_geomtype text;
BEGIN
    var_geomtype := geometrytype(NEW.geom); -- <co id="co_code_trigger_paris_insert_1"/>
    IF var_geomtype IN ('MULTIPOLYGON', 'POLYGON') THEN
        NEW.geom := ST_Multi(NEW.geom);
        INSERT INTO ch14.paris_polygons(
            gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        )
        SELECT gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        FROM (SELECT NEW.*) As foo; -- <co id="co_code_trigger_paris_insert_2"/>
    ELSIF var_geomtype = 'POINT' THEN
        INSERT INTO ch14.paris_points (
            gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        )
        SELECT gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        FROM (SELECT NEW.*) As foo;
    ELSIF var_geomtype = 'LINESTRING' THEN
        INSERT INTO ch14.paris_linestrings (
            gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        )
        SELECT gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        FROM (SELECT NEW.*) As foo;
    ELSE
        INSERT INTO ch14.paris_rejects (
            gid,osm_id,ar_num,feature_name,feature_type,geom,tags
        )
        SELECT gid,osm_id,ar_num,feature_name,feature_type,geom,tags 
        FROM (SELECT NEW.*) As foo; -- <co id="co_code_trigger_paris_insert_3"/>                             
    END IF;
    RETURN NULL; -- <co id="co_code_trigger_paris_insert_4"/>
END;
$$
LANGUAGE 'plpgsql' VOLATILE;
-- <end id="code_trigger_paris_insert"/> --

-- <start id="code_trigger_paris_insert_bind_before"/> --
CREATE TRIGGER trigger1_paris_insert BEFORE INSERT
ON ch14.paris FOR EACH ROW
EXECUTE PROCEDURE ch14.trigger_paris_insert();
-- <end id="code_trigger_paris_insert_bind_before"/> --

-- <start id="code_ch_14_india"/> --
INSERT INTO ch03.paris (osm_id, geom, tags)
SELECT osm_id, geom, tags FROM ch03.paris_hetero;
-- <end id="code_ch_14_india"/> --

-- <start id="code_trigger_dynamic_tables"/> --
CREATE OR REPLACE FUNCTION ch14.trigger_paris_child_insert() 
RETURNS TRIGGER AS 
$$
DECLARE
    var_sql text;
    var_tbl text;
BEGIN
    var_tbl :=  
		TG_TABLE_NAME || '_ar' || lpad(NEW.ar_num::text,2,'0'); -- <co id="co_code_trigger_dynamic_tables_1b"/>
    IF NOT EXISTS (
        SELECT * 
        FROM information_schema.tables -- <co id="co_code_trigger_dynamic_tables_2a"/>
        WHERE table_schema = TG_TABLE_SCHEMA AND table_name = var_tbl) 
    THEN        
        var_sql := 
            'CREATE TABLE ' || TG_TABLE_SCHEMA || '.' || var_tbl || 
            '(CONSTRAINT pk_' || var_tbl || 
            ' PRIMARY KEY(gid)) INHERITS (' || TG_TABLE_SCHEMA || 
            '.' || TG_TABLE_NAME  || '); CREATE INDEX idx_' || 
			var_tbl || '_geom ON ' || TG_TABLE_SCHEMA || '.' || 
			var_tbl || ' USING gist(geom); ALTER TABLE ' || 
			TG_TABLE_SCHEMA || '.' || var_tbl || 
            ' ADD CONSTRAINT chk_ar_num CHECK (ar_num = ' || 
            NEW.ar_num::text || ');';
        EXECUTE var_sql; -- <co id="co_code_trigger_dynamic_tables_3a"/>
    END IF;
    var_sql := 
        'INSERT INTO ' || TG_TABLE_SCHEMA || '.' || var_tbl || 
        '(gid,osm_id,ar_num,feature_name,feature_type,geom,tags) ' || 
        'VALUES($1,$2,$3,$4,$5,$6,$7)'; -- <co id="co_code_trigger_dynamic_tables_4a"/>
    EXECUTE var_sql 
    USING 
        NEW.gid,NEW.osm_id,NEW.ar_num,NEW.feature_name,
        NEW.feature_type,NEW.geom,NEW.tags;                       
    RETURN NULL; -- <co id="co_code_trigger_dynamic_tables_5a"/>
END;
$$ language plpgsql;
-- <end id="code_trigger_dynamic_tables"/> --

-- <start id="code_binding_trig_several_tables"/> --
CREATE TRIGGER trig01_paris_child_insert BEFORE INSERT
ON ch14.paris_polygons FOR EACH ROW
EXECUTE PROCEDURE ch14.trigger_paris_child_insert();

CREATE TRIGGER trig01_paris_child_insert BEFORE INSERT
ON ch14.paris_points FOR EACH ROW
EXECUTE PROCEDURE ch14.trigger_paris_child_insert();

CREATE TRIGGER trig01_paris_child_insert BEFORE INSERT
ON ch14.paris_linestrings FOR EACH ROW
EXECUTE PROCEDURE ch14.trigger_paris_child_insert();
-- <end id="code_binding_trig_several_tables"/> --
   
-- <start id="code_testing_truncate_before_test"/> --
TRUNCATE TABLE ch14.paris;
TRUNCATE TABLE ch14.paris_rejects;
-- <end id="code_testing_truncate_before_test"/> --

-- <start id="code_testing_create_table_triggers"/> --
INSERT INTO ch14.paris(osm_id, geom, tags, ar_num)
SELECT osm_id, geom, tags, ar_num
FROM ch14.paris_hetero;
-- <end id="code_testing_create_table_triggers"/> --

-- <start id="code_ch_14_juliet"/> --
SELECT * FROM ch14.paris WHERE ar_num = 17;
-- <end id="code_ch_14_juliet"/> --