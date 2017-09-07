import psycopg2
import subprocess
import sys, os

# https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
input_path = "C:\\data\\shape_exe1"

for raster in os.listdir(input_path):
    if raster.endswith(".tif"):
       name = raster.split(".tif")[0]
       raster = os.path.join(input_path, raster)


    os.environ['PATH'] = r';C:\Program Files\PostgreSQL\9.4\bin'
    os.environ['PGHOST'] = 'localhost'
    os.environ['PGPORT'] = '5432'
    os.environ['PGUSER'] = 'postgres'
    os.environ['PGPASSWORD'] = 'postgres'
    os.environ['PGDATABASE'] = 'raster_database'

    rastername = str(name)
    rasterlayer = rastername.lower()

    conn = psycopg2.connect(database="raster_database", user="postgres", host="localhost", password="postgres")
    cursor = conn.cursor()

    cmds = 'raster2pgsql -s 32633 -t 2000x2000 "' + raster + '" |psql'
    subprocess.call(cmds, shell=True)

    sql = "UPDATE " + rasterlayer + " SET rast = ST_Rescale(rast, 250, 'Near'); \
                  UPDATE " + rasterlayer + " SET rast = ST_Transform(ST_SetSRID(rast,32633),4326);"
    cursor.execute(sql)
    conn.commit()

    rql = "COPY (SELECT encode(ST_AsTIFF(rast), 'hex') AS tif FROM " + rasterlayer + ") TO 'C:/Users/Data/" + rasterlayer + ".hex';"
    cursor.execute(rql)
    conn.commit()