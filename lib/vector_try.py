try:
    from osgeo import ogr

    print('Import of ogr from osgeo worked.  Hurray!\n')
except:
    print('Import of ogr from osgeo failed\n\n')

cnt = ogr.GetDriverCount()
formatsList = []  # empty List

for i in range(cnt):
    driver = ogr.GetDriver(i)
    driverName = driver.GetName()
    if not driverName in formatsList:
        formatsList.append(driverName)
formatsList.sort()  # sorting the messsy list of ogr drivers

# for i in formatsList:
#     print i


import sys, sqlite3

if len(sys.argv) != 2:
  print("expected database file name")
  sys.exit()
file = sys.argv[1]

conn = sqlite3.connect(file)
c = conn.cursor()

c.execute('select * from sqlite_master')
for table in c:
  print((table[0]))

conn.close()