Data for this chapter was downloaded from MassGIS website

Vector:
OpenSpace - http://www.mass.gov/anf/research-and-tech/it-serv-and-support/application-serv/office-of-geographic-information-massgis/datalayers/osp.html
Hospitals - http://www.mass.gov/anf/research-and-tech/it-serv-and-support/application-serv/office-of-geographic-information-massgis/datalayers/hospitals.html
Roads - http://www.mass.gov/anf/research-and-tech/it-serv-and-support/application-serv/office-of-geographic-information-massgis/datalayers/ftpeotroads.html


Raster:
http://www.mass.gov/anf/research-and-tech/it-serv-and-support/application-serv/office-of-geographic-information-massgis/datalayers/noaacharts.html#download
used noaa_13270_1.zip (MrSid) converted to jpeg with: 
gdal_translate -of JPEG noaa_13270_1.sid noaa_13270_1.jpg 

then loaded in with raster2pgsql using
raster2pgsql -I -e -F -C -Y -s 26986 -t 500x500  noaa/*.jpg ch17.noaa | psql -U postgres -d postgis_in_action

In a PostGIS 2+ enabled database

Get into psql (TIP: You can launch psql from PgAdmin Plugins menu - make sure to select the database first before you launch)
run
\i /path/to/data/ch17_vector.sql

--- alternatively --
"C:\Program Files\PostgresQL\9.3\bin\psql" -h localhost -d postgis_in_action -U postgres -f ch17_data.sql

-- All the code for the web applications described in the chapter can be found in the webapp folder