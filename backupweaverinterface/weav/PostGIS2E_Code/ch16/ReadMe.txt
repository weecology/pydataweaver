To create ch16 schema and load reference data:
psql -d postgis_in_action -f data/ch16_data.sql

To create the pics table
raster2pgsql -F -Y data/*.JPG ch16.pics | psql -U postgres -d postgis_in_action

Data Sources
1) Packaged picture is a snapshot view of Boston from our office.
2) twin_cities are roads subset from roads data in chapter 1.
3) spain_nuclear_plants consists of spain nuclear power lon lat locations.
4) chance.js is original chance script from http://chancejs.com/  (chance_modified.js is our slightly modified version we loaded into plv8_modules to run under PL/V8)