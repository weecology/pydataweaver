import os

from osgeo import gdal
from osgeo import osr
from gdalconst import GA_ReadOnly


class Raster:
    """ processes the spatial files from a given location
    """

    raster_extensions = ['.gif', '.img', '.bil', '.jpg', '.tif', '.tiff','.hdf','.l1b']
    multi_file = ['.hdf','hd5']

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
    srcband = raster_src.GetRasterBand(band_number)
    return srcband.GetNoDataValue()


def get_color_table(rasterfn, band_number):
    """get the color table for a given band"""
    raster_src = gdal.Open(rasterfn)
    srcband = raster_src.GetRasterBand(band_number)
    return srcband.GetRasterColorTable()


def get_color_entries(color_table):
    if color_table is not None:
        return color_table.GetCount()
    else:
        return 0


