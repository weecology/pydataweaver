import sqlite3
# SELECT load_extension('libspatialite.dylib')
conn = sqlite3.connect("test.db")


from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst

# # Create a PostGIS table from WKT
import ogr, osr


# database = 'test'
# usr = 'postgres'
# pw = 'xxxxhenry'
# table = 'test'
#
# wkt = "POINT (1120351.5712494177 741921.4223245403)"
# point = ogr.CreateGeometryFromWkt(wkt)
#
# connectionString = "PG:dbname='%s' user='%s' password='%s'" % (database,usr,pw)
# ogrds = ogr.Open(connectionString)
#
# srs = osr.SpatialReference()
# srs.ImportFromEPSG(4326)
#
# layer = ogrds.CreateLayer(table, srs, ogr.wkbPoint, ['OVERWRITE=YES'] )
#
# layerDefn = layer.GetLayerDefn()
#
# feature = ogr.Feature(layerDefn)
# feature.SetGeometry(point)
#
# layer.StartTransaction()
# layer.CreateFeature(feature)
# feature = None
# layer.CommitTransaction()




# Import vector data into postgis