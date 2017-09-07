-- verifying PostGIS / PostgreSQL version
SELECT postgis_full_version();
SELECT version();

CREATE SCHEMA ch01;

-- <start id="code_create_lu_franchises"/> --
CREATE TABLE ch01.lu_franchises (id char(3) PRIMARY KEY
 , franchise varchar(30)); -- <co id="co_code_create_lu_franchises_1" />

INSERT INTO ch01.lu_franchises(id, franchise) -- <co id="co_code_create_lu_franchises_2" />
VALUES 
  ('BKG', 'Burger King'), ('CJR', 'Carl''s Jr'),
  ('HDE', 'Hardee'), ('INO', 'In-N-Out'), 
  ('JIB', 'Jack in the Box'), ('KFC', 'Kentucky Fried Chicken'),
  ('MCD', 'McDonald'), ('PZH', 'Pizza Hut'),
  ('TCB', 'Taco Bell'), ('WDY', 'Wendys');
-- <end id="code_create_lu_franchises"/> --
-- #1 create table
-- #2 populate table

-- <start id="code_create_restaurants"/> --
CREATE TABLE ch01.restaurants
(
  id serial primary key   -- <co id="co_code_create_restaurants_1"/> --
  , franchise char(3) NOT NULL
  , geom geometry(point,2163) -- <co id="co_code_create_restaurants_2"/> --
);
-- <end id="code_create_restaurants"/> --


-- <start id="code_restaurants_fk"/> --
ALTER TABLE ch01.restaurants 
  ADD CONSTRAINT fk_restaurants_lu_franchises
  FOREIGN KEY (franchise) 
  REFERENCES ch01.lu_franchises (id)
  ON UPDATE CASCADE ON DELETE RESTRICT;
-- <end id="code_restaurants_fk"/> --

-- <start id="code_restaurants_fki"/> --
CREATE INDEX fki_restaurants_franchises 
 ON ch01.restaurants (franchise);
-- <end id="code_restaurants_fki"/> --

-- <start id="code_create_highways"/> --
CREATE TABLE ch01.highways -- <co id="co_code_create_highways_1"/>
(
  gid integer NOT NULL,
  feature character varying(80),
  name character varying(120),
  state character varying(2),
  geom geometry(multilinestring,2163), -- <co id="co_code_create_highways_2"/>
  CONSTRAINT pk_highways PRIMARY KEY (gid)
);

CREATE INDEX idx_highways 
 ON ch01.highways USING gist(geom); -- <co id="co_code_create_highways_3"/>
-- <end id="code_create_highways"/> --
--#1 create highway
--#3 multilinestring equal area
--#2 add spatial index

-- <start id="code_create_restaurants_staging"/> --
CREATE TABLE ch01.restaurants_staging (
  franchise text, lat double precision, lon double precision);
-- <end id="code_create_restaurants_staging"/> --

-- <start id="code_insert_restaurants"/> --
INSERT INTO ch01.restaurants (franchise, geom)
SELECT franchise
 , ST_Transform(
   ST_SetSRID(ST_Point(lon , lat), 4326)
   , 2163) As geom
FROM ch01.restaurants_staging;
-- <end id="code_insert_restaurants"/> --

-- <start id="code_restaurants_geom_idx"/> --
CREATE INDEX idx_code_restaurants_geom 
  ON ch01.restaurants USING gist(geom); 
-- <end id="code_restaurants_geom_idx"/> --

-- <start id="code_insert_highways"/> --
INSERT INTO ch01.highways (gid, feature, name, state, geom)
SELECT gid, feature, name, state, ST_Transform(geom, 2163)
FROM ch01.highways_staging
WHERE feature LIKE 'Principal Highway%';
-- <end id="code_insert_highways"/> --

-- <start id="code_one_mile_count"/> --
SELECT f.franchise
 , COUNT(DISTINCT r.id) As total -- <co id="co_code_one_mile_count_1"/>
FROM ch01.restaurants As r 
  INNER JOIN ch01.lu_franchises As f ON r.franchise = f.id
    INNER JOIN ch01.highways As h 
      ON ST_DWithin(r.geom, h.geom, 1609) -- <co id="co_code_one_mile_count_2"/>
GROUP BY f.franchise
ORDER BY total DESC;
-- <end id="code_one_mile_count"/> --

-- <start id="code_hardee_md"/> --
SELECT COUNT(DISTINCT r.id) As total
FROM ch01.restaurants As r 
     INNER JOIN ch01.highways As h 
     ON ST_DWithin(r.geom, h.geom, 1609*20)
WHERE r.franchise = 'HDE' 
 AND h.name  = 'US Route 1' AND h.state = 'MD';
-- <end id="code_hardee_md"/>

-- <start id="code_route1"/> --
SELECT gid, name, geom 
FROM ch01.highways
WHERE name = 'US Route 1' AND state = 'MD';
-- <end id="code_route1"/> --

-- <start id="code_route1_buffer"/> --
SELECT ST_Union(ST_Buffer(geom, 1609*20))
FROM ch01.highways
WHERE name = 'US Route 1' AND state = 'MD';
-- <end id="code_route1_buffer"/> --

-- <start id="code_route1_hardee"/> --
SELECT r.geom
FROM ch01.restaurants r
WHERE EXISTS 
 (SELECT gid FROM ch01.highways 
  WHERE ST_DWithin(r.geom, geom, 1609*20) AND 
  name = 'US Route 1' 
   AND state = 'MD' AND r.franchise = 'HDE');
-- <end id="code_route1_hardee"/> --

--Unused Below


-- loading data server side --
-- Using SQL
COPY ch01.restaurants 
 FROM '/data/restaurants.csv' DELIMITER ',';
