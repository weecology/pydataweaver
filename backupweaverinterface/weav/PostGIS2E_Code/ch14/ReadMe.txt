You don't need these files to complete the core of chapter 14 exercises.  These are provided for reference or if you would like to go thru the whole preparation yourself and be able to run all the code listings.

1) We downloaded that portion of data in (osm format) using the openstreetmap api and loaded in using osm2pgsql as discussed in Chapter 4.
Arc De Triump - lon:2.2952675,lat:48.8752933 (http://api.openstreetmap.org/api/0.6/bbox=2.28568,48.87957,2.30371,48.8676)

This is all included in the ch14_staging_data.sql and can be loaded without going thru the trouble.  The raw osm file is in raw_files folder.

osm2pgsql arctriump.osm -U postgres -P 5432 -d postgis_in_action -S default.style --hstore

2) The paris_-_arrondissements.zip is the shapefile of the arrondissements polygons we downloaded from geocommons.
The arrondisement boundaries were downloaded from:  http://finder.geocommons.com/overlays/18335
Data is in WGS 84 long lat (SRID: 4326).  This is also in the raw_files folder and also included in sql format in ch14_data.sql already transformed;

#
3) The code14.sql contains code used in book