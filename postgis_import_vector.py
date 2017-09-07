# import psycopg2, urllib, zipfile, os
import os
# http://www.jmapping.com/getting-started-with-scripted-geo-data-processing-postgresql-postgis-python-and-a-little-ogr/
#DB connection properties
# conn = psycopg2.connect(dbname = 'postgres', host= 'localhost', port= 5432, user = 'postgres',password= 'xxxxhenry')
# cur = conn.cursor()  ## open a cursor

## Download the zipped shapefile

# urllib.urlretrieve("http://gis.drcog.org/datacatalog/download/685/county_2014.zip", "data/vector/county_data/county.zip")

# ## Unzip the shapefile
# fh = open('data/vector/county_data/county.zip', 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = "data/vector/county_data"
#     z.extract(name, outpath)
# fh.close()



## Download the zipped shapefile

# urllib.urlretrieve("http://gis.drcog.org/datacatalog/content/drcog-crash-data-points-2006", "data/vector/crash_data/crash.zip")

# ## Unzip the shapefile
# fh = open('data/vector/county_data/crash.zip', 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = "data/vector/crash_data"
#     z.extract(name, outpath)
# fh.close()
#


## Load the shapefile into the database
os.system("""ogr2ogr -overwrite -skipfailures -progress -f PostgreSQL PG:"dbname='postgres' host='localhost' port='5432' user='postgres' password='xxxxhenry'" data/vector/county_data/county/county_2014.shp -nln county""")

from osgeo import ogr

# ## Not the prettiest way to rename the geometry field
# fixCountyGeomName = 'ALTER TABLE county RENAME COLUMN wkb_geometry TO the_geom;'
# cur.execute(fixCountyGeomName)
#
# ## Download the zipped shapefile
# http://gis.drcog.org/datacatalog/content/drcog-crash-data-points-2006
# urllib.urlretrieve("http://gis.drcog.org/datacatalog/sites/default/files/shapefiles/drcog_crash_2006_shapefile_0.zip", "crash.zip")
#
# ## Unzip the shapefile
# fh = open('crash.zip', 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = "/YOUR/DESTINATION/PATH/"
#     z.extract(name, outpath)
# fh.close()
#
# ## Load the shapefile into the database
# os.system("""ogr2ogr -overwrite -skipfailures -progress -f PostgreSQL PG:"dbname='YOUR_DATABASE' host='YOUR_HOST' port='5432' user='YOUR_USER' password='YOUR_PASS'" PATH/TO/drcog_crash_2006.shp -nln crash_pts""")
#
# ## Not the prettiest way to rename the geometry field
# fixCrashGeomName = 'ALTER TABLE crash_pts RENAME COLUMN wkb_geometry TO the_geom;'
# cur.execute(fixCrashGeomName)
#
# conn.commit() ## commits pending transactions to the db (making them persistent). This is needed for sql that modifies data or creates objects.
#
# cur.close()
# conn.close()
#
# print "Data loaded into database!"
# Now that the data is loaded into the database we can connect with psycopg2 and do some processing or analysis of the imported data.  This technique gives you the ability to utilize the full power of the database through SQL queries while also being able to pull data into your Python environment if needed.  This also provides control over the sequence of processing steps.   You could gain similar control through PostgreSQL functions but I will save that topic for another post.
#
# Here we perform a PostGIS ST_Within() function to determine how many pedestrians where injured or killed within Denver in 2006 while also creating an additional database table of just the crashes where pedestrians where involved.
#
# #!/usr/bin/env python
#
# import psycopg2
#
# #DB connection properties
# conn = psycopg2.connect(dbname = 'YOUR_DB_NAME', host= 'YOUR_HOST', port= 5432, user = 'YOUR_USER',password= 'YOUR_PASS')
# cur = conn.cursor()
#
# getPedestrianCrashesWhithin = '''SELECT a.killed, a.injured FROM crash_pts a, county b WHERE (a.ped_act1 > 0 OR a.ped_act2 > 0 OR a.ped_act3 > 0) AND b.county = 'Denver' AND ST_Within(a.the_geom, b.the_geom);'''
#
# createSubsetOfPedestrianCrashes = '''DROP TABLE IF EXISTS ped_crash_pts;
#                                      CREATE TABLE ped_crash_pts AS
#                                      SELECT a.* FROM crash_pts a, county b WHERE a.ped_act1 > 0 OR a.ped_act2 > 0 OR a.ped_act3 > 0;'''
#
# cur.execute(createSubsetOfPedestrianCrashes)
# conn.commit()
#
# cur.execute(getPedestrianCrashesWhithin)  ## executes the sql command
# pedestrianCrashes = cur.fetchall()  ## returns the result
#
# totalKilled = 0
# totalInjured = 0
# for crash in pedestrianCrashes:
#     killed = crash[0]
#     injured = crash[1]
#
#     if killed > 0:
#         totalKilled += 1
#
#     if injured > 0:
#         totalInjured += 1
#
# print "Total killed in Denver = ", totalKilled
# print "Total injured in Denver = ", totalInjured
#
# cur.close()
# conn.close()