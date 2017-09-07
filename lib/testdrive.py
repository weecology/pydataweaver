import gdal
from gdalconst import *
import osr
import os
import csvengine


from .gisengine import Spacial
from osgeo import gdal
import os, sys, time

startTime = time.time()
c= Spacial()
# c.read_source("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/hdffiles")

# c.read_source("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/testalldataformats")   #gdaltest/data/testalldataformats  hdffiles
c.read_source("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/Bioclim/")
c.get_bands()

# for (rectangle, choice) in c.data_sets:
#     print(rectangle, choice)
# print type(c.data_sets[0])
# print type(c.data_sets)
# exit()

# this reads the main file and creates out merge
# exampleFile = open('C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/testalldataformats/routes_new.csv')
exampleFile = open('C:/Users/Henry/.retriever/raw_data/BBS/routes_new.csv')
# exampleFile = open('C:/Users/Henry/.retriever/raw_data/BBS/100routes_new.csv')
output =open('result13.csv', 'wb')
csvWriter = csvengine.writer(output, dialect='excel')
exampleReader = csvengine.reader(exampleFile,delimiter=',')
header = next(exampleReader)
latitude = header.index("Lati")
longitude = header.index("Longi")
# print(latitude,longitude)
# print ";;;;;;;;;;;;;;;",header
header_set = False
header_written = False
new_header = ','.join(header)

kill_memory = list()

for mysubdataset_name, formatx  in c.data_sets:
    src_ds = gdal.Open(mysubdataset_name, gdal.GA_ReadOnly)
    kill_memory.append((mysubdataset_name,formatx,src_ds))


for row in exampleReader:
    # print type(row)
    new_line = ','.join(row )
    x, y = float(row[longitude]), float(row[latitude])

    for mysubdataset_name,formatx,src_ds in kill_memory:

        rows = src_ds.RasterYSize
        cols = src_ds.RasterXSize
        geoMatrix = src_ds.GetGeoTransform()
        # get georeference info
        transform = src_ds.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = transform[5]
        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)
        for band_num in range(1, src_ds.RasterCount+1):
            if not header_set:
                if formatx  not in c.multi_file:
                    if band_num == 1:
                        new_header += ","+str(os.path.splitext(os.path.basename(os.path.normpath(mysubdataset_name)))[0])
                    else:
                        new_header += ","+str(os.path.splitext(os.path.basename(os.path.normpath(mysubdataset_name)))[0])+"_band_"+str(band_num)
                else:
                    description_hdf = str(src_ds.GetDescription()).split(":")
                    if len(description_hdf) > 4:
                        new_header += ","+str(description_hdf[5])
                    else:
                        if band_num == 1:
                            new_header += ","+str(description_hdf[4])
                        else:
                            new_header += ","+str(description_hdf[4])+"_band_"+str(band_num)

            srcband = src_ds.GetRasterBand(band_num)

            # print "[ NO DATA VALUE ] = ", srcband.GetNoDataValue()

            # data = srcband.ReadAsArray(0, 0, cols, rows)
            # feature = data[yOffset, xOffset]
            data = srcband.ReadAsArray(xOffset, yOffset, 1, 1)
            feature = data[0, 0]

            #
            # pixel = int((x - ulX) / xDist)
            # line = int((ulY - y) / yDist)
            # array = srcband.ReadAsArray()
            #
            # feature = str(array[pixel][line])
            # # print("EXTENT")
            # maxx = ulX +xDist*src_ds.RasterXSize
            # miny = ulY +yDist*src_ds.RasterYSize
            # # print "((x_min, pixel_size, 0, y_max, 0, -pixel_size))"
            # # print geoMatrix
            # # print (ulX, miny,maxx,ulY)
            new_line += str(","+ str(feature))
    header_set = True

    if header_set and not header_written:
        csvWriter.writerow(new_header.split(","))
        header_written=True
    elif header_set and header_written:
        csvWriter.writerow(new_line.split(","))


        # print(new_line)
# print(new_header)
output.close()
exampleFile.close()
endTime = time.time()
print(('The script took ' + str(endTime - startTime) + ' seconds'))
exit()





c= Spacial()
# c.read_source("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/hdffiles")

# c.read_source("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/testalldataformats")   #gdaltest/data/testalldataformats  hdffiles
c.read_source("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/Bioclim/")
c.get_bands()

# for (rectangle, choice) in c.data_sets:
#     print(rectangle, choice)
# print type(c.data_sets[0])
# print type(c.data_sets)
# exit()

# this reads the main file and creates out merge
# exampleFile = open('C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/testalldataformats/routes_new.csv')
exampleFile = open('C:/Users/Henry/.retriever/raw_data/BBS/routes_new.csv')
# exampleFile = open('C:/Users/Henry/.retriever/raw_data/BBS/100routes_new.csv')
output =open('result10.csv', 'wb')
csvWriter = csvengine.writer(output, dialect='excel')
exampleReader = csvengine.reader(exampleFile,delimiter=',')
header = next(exampleReader)
latitude = header.index("Lati")
longitude = header.index("Longi")
# print(latitude,longitude)
# print ";;;;;;;;;;;;;;;",header
header_set = False
header_written = False
new_header = ','.join(header)

kill_memory = list()

for mysubdataset_name, formatx  in c.data_sets:
    src_ds = gdal.Open(mysubdataset_name, gdal.GA_ReadOnly)
    kill_memory.append((mysubdataset_name,formatx,src_ds))
    rows = src_ds.RasterYSize
    cols = src_ds.RasterXSize
    geoMatrix = src_ds.GetGeoTransform()
    # get georeference info
    transform = src_ds.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
for row in exampleReader:
    # print type(row)
    new_line = ','.join(row )
    x, y = float(row[longitude]), float(row[latitude])
    for mysubdataset_name,formatx,src_ds in kill_memory:
        for band_num in range(1, src_ds.RasterCount+1):
            if not header_set:
                if formatx  not in c.multi_file:
                    if band_num == 1:
                        new_header += ","+str(os.path.splitext(os.path.basename(os.path.normpath(mysubdataset_name)))[0])
                    else:
                        new_header += ","+str(os.path.splitext(os.path.basename(os.path.normpath(mysubdataset_name)))[0])+"_band_"+str(band_num)
                else:
                    description_hdf = str(src_ds.GetDescription()).split(":")
                    if len(description_hdf) > 4:
                        new_header += ","+str(description_hdf[5])
                    else:
                        if band_num == 1:
                            new_header += ","+str(description_hdf[4])
                        else:
                            new_header += ","+str(description_hdf[4])+"_band_"+str(band_num)

            srcband = src_ds.GetRasterBand(band_num)

            # print "[ NO DATA VALUE ] = ", srcband.GetNoDataValue()

            data = srcband.ReadAsArray(0, 0, cols, rows)
            xOffset = int((x - xOrigin) / pixelWidth)
            yOffset = int((y - yOrigin) / pixelHeight)
            feature = data[yOffset, xOffset]
            # pixel = int((x - ulX) / xDist)
            # line = int((ulY - y) / yDist)
            # array = srcband.ReadAsArray()
            #
            # feature = str(array[pixel][line])
            # # print("EXTENT")
            # maxx = ulX +xDist*src_ds.RasterXSize
            # miny = ulY +yDist*src_ds.RasterYSize
            # # print "((x_min, pixel_size, 0, y_max, 0, -pixel_size))"
            # # print geoMatrix
            # # print (ulX, miny,maxx,ulY)
            new_line += str(","+ str(feature))
    header_set = True

    if header_set and not header_written:
        csvWriter.writerow(new_header.split(","))
        header_written=True
    elif header_set and header_written:
        csvWriter.writerow(new_line.split(","))


    # print(new_line)
# print(new_header)
output.close()
exampleFile.close()
exit()








for row in exampleReader:
    print((type(row)))
    new_line = ','.join(row )
    x, y = float(row[longitude]), float(row[latitude])

    for mysubdataset_name, formatx  in c.data_sets:
        src_ds = gdal.Open(mysubdataset_name, gdal.GA_ReadOnly)

        geoMatrix = src_ds.GetGeoTransform()

        for band_num in range(1, src_ds.RasterCount+1):
            if not header_set:
                if formatx  not in c.multi_file:
                    if band_num == 1:
                        new_header += ","+str(os.path.splitext(os.path.basename(os.path.normpath(mysubdataset_name)))[0])
                    else:
                        new_header += ","+str(os.path.splitext(os.path.basename(os.path.normpath(mysubdataset_name)))[0])+"_band_"+str(band_num)
                else:
                    description_hdf = str(src_ds.GetDescription()).split(":")
                    if len(description_hdf) > 4:
                        new_header += ","+str(description_hdf[5])
                    else:
                        if band_num == 1:
                            new_header += ","+str(description_hdf[4])
                        else:
                            new_header += ","+str(description_hdf[4])+"_band_"+str(band_num)

            srcband = src_ds.GetRasterBand(band_num)

            # print "[ NO DATA VALUE ] = ", srcband.GetNoDataValue()

           # refactor
            ulX = geoMatrix[0]
            ulY = geoMatrix[3]
            xDist = geoMatrix[1]
            yDist = geoMatrix[5]
            rtnX = geoMatrix[2]
            pixel = int((x - ulX) / xDist)
            line = int((ulY - y) / xDist)
            array = srcband.ReadAsArray()

            # feature = str(array[pixel][line])
            feature = str(34)
            # print("EXTENT")
            maxx = ulX +xDist*src_ds.RasterXSize
            miny = ulY +yDist*src_ds.RasterYSize
            # print "((x_min, pixel_size, 0, y_max, 0, -pixel_size))"
            # print geoMatrix
            # print (ulX, miny,maxx,ulY)
            new_line += str(","+ feature)
    header_set = True
    print(new_line)

    print("-----------------------------------------------")
print(new_header)








exit()
gtif = gdal.Open("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/bio/bio1.bil")

# assumed values

print(x)
print(y)


geoMatrix= gtif.GetGeoTransform()
ulX = geoMatrix[0]
ulY = geoMatrix[3]
xDist = geoMatrix[1]
yDist = geoMatrix[5]
rtnX = geoMatrix[2]
pixel = int((x - ulX) / xDist)
line = int((ulY - y) / xDist)
srcband = gtif.GetRasterBand(1)

print("((x_min, pixel_size, 0, y_max, 0, -pixel_size))")
print((gtif.GetGeoTransform()))
print((srcband.GetMinimum(), srcband.GetMaximum()))

array = srcband.ReadAsArray()
print((pixel, line))
print((array[pixel][line]))





exit()
# Open tif file
ds = gdal.Open("C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/bio/bio1.bil")
# GDAL affine transform parameters, According to gdal documentation xoff/yoff are image left corner, a/e are pixel wight/height and b/d is rotation and is zero if image is north up.
xoff, a, b, yoff, d, e = ds.GetGeoTransform()

def pixel2coord(x, y):
    """Returns global coordinates from pixel x, y coords"""
    xp = a * x + b * y + xoff
    yp = d * x + e * y + yoff
    return(xp, yp)

# get columns and rows of your image from gdalinfo
rows = 36+1
colms = 34+1

if __name__ == "__main__":
 for row in  range(0,rows):
  for col in  range(0,colms):
    print((pixel2coord(col,row)))



# pixel = 120
# line = 20
#
# infile = "C:/Users/Henry/PycharmProjects/gdalandgis/gdaltest/data/bio/bio1.bil"
#
#
#
# indataset = gdal.Open( infile, GA_ReadOnly )
#
# geomatrix = indataset.GetGeoTransform()
# X = geomatrix[0] + geomatrix[1] * pixel + geomatrix[2] * line
# Y = geomatrix[3] + geomatrix[4] * pixel + geomatrix[5] * line
#
# print geomatrix
# srs = osr.SpatialReference()
# srs.ImportFromWkt(indataset.GetProjection())
#
# srsLatLong = srs.CloneGeogCS()
# ct = osr.CoordinateTransformation(srs, srsLatLong)
# (long, lat, height) = ct.TransformPoint(X, Y)
#
# print 'pixel: %g, line: %g' % (pixel, line)
# print 'latitude: %g, longitude: %g (in degrees)' % (long, lat)

# # A grid
# x = np.linspace(-sp.pi,sp.pi,100)
# X, Y = np.meshgrid(x,x)
#
# # Some values
# U = sp.sin(X)
# V = sp.cos(X)
#
#
# # Save the data into a hdf5 file
# filename = "data.hdf5"
#
# # Create and open the file with the given name
# outfile = hdf.File(filename)
#
# # Store some data under /axisgrid with direct assignment of the data x
# outfile.create_dataset("axisgridx", data=x)
#
# # Create a group for storing further data under /grid/*
# grp_grid = outfile.create_group("grid")
#
# # Store some data under /grid/grid* with direct assignment of the data X and Y
# grp_grid.create_dataset("gridx", data=X)
# grp_grid.create_dataset("gridy", data=Y)
#
# # Store the vector field values under another group called /values
# grp_vals = outfile.create_group("values")
#
# # Prepare space for storing the values but do not assign values yet
# grp_vals.create_dataset("valsx", U.shape, np.floating)
# grp_vals.create_dataset("valsy", V.shape, np.floating)
#
# # Now assign the data for U and V and show slicing via ":" and ellipsis "..."
# outfile["/values/valsx"][:] = U
# outfile["/values/valsy"][...] = V
#
# # And close the file
# outfile.close()
#
#
# # Open the file again, now in read only mode (we don't want to write data anymore!)
# infile = hdf.File(filename, "r")
#
# # Get the data, but omit every second value, just to show off some slicing
# a = infile["/grid/gridx"][::2,::2]
# b = infile["/grid/gridy"][::2,::2]
# c = infile["/values/valsx"][::2,::2]
# d = infile["/values/valsy"][::2,::2]
#
# # Plot the data as usual
# pl.figure()
# pl.quiver(a,b, c,d)
# pl.savefig("hdf_example.png")




# def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
#     """convert array to raster """
#     cols = array.shape[1]
#     rows = array.shape[0]
#     originX = rasterOrigin[0]
#     originY = rasterOrigin[1]
#
#     driver = gdal.GetDriverByName('GTiff')
#     outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
#     outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
#     outband = outRaster.GetRasterBand(1)
#     outband.WriteArray(array)
#     outRasterSRS = osr.SpatialReference()
#     outRasterSRS.ImportFromEPSG(4326)
#     outRaster.SetProjection(outRasterSRS.ExportToWkt())
#     outband.FlushCache()