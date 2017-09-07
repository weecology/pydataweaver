# pip install gdal
# error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": http://landinghub.visualstudio.com/visual-cpp-build-tools
# install The Visual C++ Build Tools http://landinghub.visualstudio.com/visual-cpp-build-tools
# pip install gdal wont work do install with pre compiled libraries
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal

from osgeo import gdal
# from osgeo import ogr
# from osgeo import osr
# from osgeo import gdal_array
# from osgeo import gdalconst
from osgeo.gdalconst import *

#read file
# ADW100o100N012d0150.HDF 43
#  GLAH13_633_2103_001_1317_0_01_0001.h5        5
#   MOD29.A2013196.1250.005.2013196195940.hdf
raster_file = 'C:/Users/Henry/Downloads/data-20170502T144908Z-001/data/MOD29.A2013196.1250.005.2013196195940.hdf'
dataset = gdal.Open(raster_file, GA_ReadOnly)

# print(dataset.GetSubDatasets())
for i in dataset.GetSubDatasets():
    print((i[0]))
    dat = gdal.Open(i[0], GA_ReadOnly)
    # print (dataset.GetProjection)
    print((dir(dat)))
    # band1 = dat.GetRasterBand(1)
    # rows = dat.RasterYSize
    # cols = dat.RasterXSize
    print((dataset.GetGeoTransform))

    # cropData = band1.ReadAsArray(0,0,cols,rows)
    # print (cropData)

    print("\n")
    exit()


# print (dataset.RasterCount)
# print(dir(dataset))
#
# print(dataset.GetMetadata())

class Hdf(object):
    """Hdf4 files
    Hierarchical Data Format (HDF) is a set of file formats (HDF4, HDF5) designed to store and organize large amounts of data. Originally developed at the National Center for Supercomputing Applications, it is supported
    """


    pass


class Hdf4(Hdf):
    """Hdf4 files"""


    pass


class Hdf5(Hdf):
    """Hdf4 files"""


    pass
