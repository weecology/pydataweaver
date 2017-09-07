Data is downloaded from
-- http://www.worldclim.org/tiles.php -
-- http://biogeo.ucdavis.edu/data/climate/worldclim/1_4/tiles/cur/prec_25.zip (precipitation)
-- http://biogeo.ucdavis.edu/data/climate/worldclim/1_4/tiles/cur/bio_25.zip
-- http://biogeo.ucdavis.edu/data/climate/worldclim/1_4/tiles/cur/tmean_26.zip

and loaded using (instructions detailed in chapter 5)
raster2pgsql -s 4326 -I -C -M bio/*.bil -F -t 256x256 ch12.bioclim | psql
raster2pgsql -s 4326 -I -C -M prec/*.bil -F -t 256x256 ch12.prec | psql
raster2pgsql -s 4326 -I -C -M alt/*.bil -F -t 256x256 ch12.prec | psql