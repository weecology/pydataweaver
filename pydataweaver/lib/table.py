from future import standard_library

standard_library.install_aliases()

import csv
import io
import sys
from functools import reduce

from pydataweaver.lib.cleanup import *


class Dataset(object):
    """Refactor table moddule since raster, vector and tabular data

    all have some common table features
    """

    def __init__(self, name=None):
        self.name = name


class TabularDataset(Dataset):
    """Information about a database table."""

    def __init__(
        self, name=None, fields=[], table_type="tabular", database_name=None, **kwargs
    ):

        self.name = name
        self.fields = fields
        self.table_type = table_type
        self.database_name = database_name

        for key in kwargs:
            if hasattr(self, key) and not self.__getattribute__(key):
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, kwargs[key])

        Dataset.__init__(self, self.name)


class RasterDataset(Dataset):
    """Raster table implementation"""

    def __init__(
        self, name=None, fields=[], table_type="raster", database_name=None, **kwargs
    ):
        self.name = None
        self.table_type = table_type
        self.group = None
        self.relative_path = 0
        self.resolution = None
        self.resolution_units = None
        self.dimensions = None
        self.noDataValue = None
        self.geoTransform = None
        self.parameter = None
        self.fields = fields
        self.database_name = database_name
        self.extent = None

        for key in kwargs:
            if hasattr(self, key) and not self.__getattribute__(key):
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, kwargs[key])
        Dataset.__init__(self, self.name)


class VectorDataset(Dataset):
    """Vector table implementation"""

    def __init__(
        self, name=None, fields=[], table_type="vector", database_name=None, **kwargs
    ):
        self.name = name
        self.table_type = table_type
        self.feature_count = None
        self.fields = fields
        self.database_name = database_name
        self.extent = {}
        self.saptialref = None

        for key in kwargs:
            if hasattr(self, key) and not self.__getattribute__(key):
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, kwargs[key])

        Dataset.__init__(self, self.name)


myTables = {"vector": VectorDataset, "raster": RasterDataset, "tabular": TabularDataset}
