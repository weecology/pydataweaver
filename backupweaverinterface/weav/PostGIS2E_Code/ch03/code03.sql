-- Listing Determing WGS 84 UTM SRID of a geometry
CREATE OR REPLACE FUNCTION upgis_utmzone_wgs84(geometry) RETURNS integer AS
$$ 
DECLARE 
    geomgeog geometry; 
    zone int; 
    pref int; 
BEGIN 
geomgeog:=ST_Transform(ST_Centroid($1),4326);                            --#1

IF (y(geomgeog))>0 THEN                                                  --#2
    pref:=32600;                                                         --#2
ELSE                                                                     --#2
    pref:=32700;                                                         --#2
END IF;                                                                  --#2
zone:=floor((ST_X(geomgeog)+180)/6)+1;                                   --#2

RETURN zone+pref;
END; 
$$ LANGUAGE 'plpgsql' immutable; 
--#1 Convert to a long lat point
--#2 Determine UTM start and zone

-- Listing 6.2 Using functional indexes
CREATE INDEX feature_data_the_geom_utm
 ON feature_data
 USING gist
 (st_transform(the_geom, 32611));

CREATE VIEW vwfeature_data AS
    SELECT gid, f_name, the_geom, 
        ST_Tranform(the_geom,32611) As the_geom_utm
    FROM feature_data;

    
--Section Guessing at spatial reference system
-- Exercise 1: The US States data Guessing at SRID GRS 80 NAD 83 long lat
-- http://edcftp.cr.usgs.gov/pub/data/nationalatlas/statesp020.tar.gz
SELECT srid, srtext, proj4text
FROM spatial_ref_sys
WHERE srtext ILIKE '%nad83%' 
    AND proj4text ILIKE '%grs80%' AND proj4text ILIKE '%longlat%';

    
-- Exercise 2: SAN FRANCISCO DATA (READING FROM .PRJ FILES)
-- http://gispub02.sfgov.org/website/sfshare/catalog/bayarea_bridges.zip
SELECT srid, srtext,proj4text
FROM spatial_ref_sys
WHERE srtext ILIKE '%california%' AND proj4text ILIKE '%nad83%' 
    AND proj4text ILIKE '%ft%';

    
-- Exercise 3: If you guess wrong
SELECT UpdateGeometrySRID('sf', 'bridges', 'the_geom', 2227);