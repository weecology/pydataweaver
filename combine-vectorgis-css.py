
# importing pyspatialite
from pyspatialite import dbapi2 as db

# creating/connecting the test_db
conn = db.connect('test_db.sqlite')

# creating a Cursor
cur = conn.cursor()

# testing library versions
rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
for row in rs:
    msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
    print msg



"""select * from surveyied_Data
JOIN ("Select name, X(Geometry), Y(Geometry), county  from towns") as gisdata
where gisdata.X = x(Geometry) and gisdata.Y = Y(Geometry)
"""

# AsText(Envelope(GeomFromText('POINT(10 20)')));

SELECT * from surveyied_Data as

JOIN("Select name, X(Geometry), Y(Geometry), county from towns") as gisdata
where

AsText(Envelope(GeomFromText('POINT(X Y)')));



# join


# SELECT plots.plot_type, AVG(surveys.weight)
# FROM surveys
# JOIN plots
# ON surveys.plot_id = plots.plot_id
# GROUP BY plots.plot_type;



