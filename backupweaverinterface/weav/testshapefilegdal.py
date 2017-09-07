from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst


# # Create a PostGIS table from WKT
import ogr, osr


try:
  from osgeo import ogr
  print ('Import of ogr from osgeo worked.  Hurray!\n')
except:
  print ('Import of ogr from osgeo failed\n\n')