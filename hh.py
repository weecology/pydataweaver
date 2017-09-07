
# # Create a PostGIS table from WKT
import ogr, osr


database = 'testdb'
usr = 'postgres'
pw = 'xxxxhenry'
table = 'testll'

wkt = "POINT (1120351.5712494177 741921.4223245403)"
point = ogr.CreateGeometryFromWkt(wkt)

connectionString = "PG:dbname='%s' user='%s' password='%s'" % (database,usr,pw)
ogrds = ogr.Open(connectionString)

srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

layer = ogrds.CreateLayer(table, srs, ogr.wkbPoint, ['OVERWRITE=YES'] )
ogrds.CreateLayer()

layerDefn = layer.GetLayerDefn()

feature = ogr.Feature(layerDefn)
feature.SetGeometry(point)

layer.StartTransaction()
layer.CreateFeature(feature)
feature = None
layer.CommitTransaction()