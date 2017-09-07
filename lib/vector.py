en_de = {"red" : "rot", "green" : "grn", "blue" : "blau", "yellow":"gelb"}
de_fr = {"rot" : "rouge", "grn" : "vert", "blau" : "bleu", "gelb":"jaune"}
ke = "red"
print((en_de[ke]))
exit()
dictionaries = {"en_de" : en_de, "de_fr" : de_fr }
print((dictionaries["de_fr"]["blau"]))

exit()
# Get List of Ogr Drivers Alphabetically (A- Z)
import ogr
cnt = ogr.GetDriverCount()
formatsList = []  # Empty List

for i in range(cnt):
    driver = ogr.GetDriver(i)
    # print dir(driver)
    print((driver.name))
    # exit()
    driverName = driver.GetName()

    if not driverName in formatsList:
        formatsList.append(driverName)

formatsList.sort() # Sorting the messy list of ogr drivers

for i in formatsList:
    print(i)

# Is Ogr Driver Available by Driver Name
## Shapefile available?
driverName = "ESRI Shapefile"
drv = ogr.GetDriverByName( driverName )
dataformats= {"ESRI Shapefile":".shp"}
layerList = []


# To take care of the CSV special case (see comments) without changing the input filename format:
# http://gis.stackexchange.com/questions/141905/force-ogr-to-use-specific-driver-for-input-format

import os


class Vectors(object):

    def __init__(self):
        self.layerList = []
        self.paths = [] # just all files

        self.extension_drivers = {".shp":"ESRI Shapefile"}     # extension , driver_name
        self.data_sets =[]  # filename drivername       (only vector data sources  and extension)

    # move read source to manager
    def read_source(self, pathx):
        """read source folder or file and return list of files
        """
        if os.path.isfile(os.path.normpath(pathx)):
            self.paths = [os.path.normpath(pathx)]
        else:
            self.paths = [os.path.normpath(os.path.join(root, name))
                         for root, dirs, files in os.walk(pathx, topdown=False) for name in files]


    def data_sources(self):
        """get all the bands from the source files"""
        for filenames in self.paths:
            if os.path.isfile(filenames) and os.path.splitext(os.path.normpath(filenames))[1] in self.extension_drivers:
                extension = os.path.splitext(os.path.normpath(filenames))[1]
                self.data_sets.append((filenames, extension,self.extension_drivers[extension] )) #infact we dont need extension

    def get_layers(self):
        for filename, extension, driver_name in self.data_sets:
            driver = ogr.GetDriverByName(driver_name)
            data_source = driver.Open(filename, 0) # 0 means read-only. 1 means writeable

            if data_source is None:
                print(('Could not open {}'.format(filename)))
            else:
                layer = data_source.GetLayer()
                featureCount = layer.GetFeatureCount()

def get_driver(driver_name):
    return ogr.GetDriverByName(driver_name)


# given a file name and the driver
# make sure the dataset is not getting dereferenced   :: ref rasters memory dereferenced
# ref:http://gis.stackexchange.com/questions/157521/python-crashes-with-returned-gdal-band-object-from-a-function
#else  remove from get_layers
def read_dataSource(filename,driver_name):
    driver = ogr.GetDriverByName(driver_name)
    data_source = driver.Open(filename, 0) # 0 means read-only. 1 means writeable.
    return data_source


