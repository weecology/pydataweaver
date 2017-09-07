
import os

from osgeo import gdal
from osgeo import osr
from gdalconst import GA_ReadOnly


class Raster:
    """ processes the spatial files from a given location
    """

    raster_extensions = ['.gif', '.img', '.bil', '.jpg', '.tif', '.tiff','.hdf','.l1b']
    multi_file = [".hdf"]

    def __init__(self):
        self.data_sets = list()
        self.firm = []

    def read_source(self, pathx):
        """read source folder or file and return list of Raster files
        """
        if os.path.isfile(os.path.normpath(pathx)):
            self.firm = [os.path.normpath(pathx)]
        else:
            self.firm = [os.path.normpath(os.path.join(root, name))
                         for root, dirs, files in os.walk(pathx, topdown=False) for name in files]

    def get_bands(self):
        """get all the bands from the source files"""
        for filenames in self.firm:
            if os.path.isfile(filenames) and os.path.splitext(os.path.normpath(filenames))[1] in self.raster_extensions:
                extension = os.path.splitext(os.path.normpath(filenames))[1]
                try:
                    if extension in self.multi_file:
                        files_sc = gdal.Open(filenames, GA_ReadOnly)
                        datasets = files_sc.GetSubDatasets()
                        for sub_dataset in datasets:
                            subdataset_name = sub_dataset[0]
                            src_ds = gdal.Open(subdataset_name, gdal.GA_ReadOnly)
                            self.data_sets.append((sub_dataset[0], extension))
                    else:
                        self.data_sets.append((filenames, extension))
                except RuntimeError as e:
                    print(('Unable to open file {0}.'.format(filenames)))
                    print(e)


def get_no_data_value(rasterfn, band_number):
    """get the no data value of the raster"""
    raster_src = gdal.Open(rasterfn)
    band = raster_src.GetRasterBand(band_number)
    return band.GetNoDataValue()


def get_color_table(rasterfn, band_number):
    """get the color table"""
    raster = gdal.Open(rasterfn)


def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
    """convert array to raster """
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()




