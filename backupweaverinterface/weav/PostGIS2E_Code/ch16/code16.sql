-- <start id="code_souce_target_add_topology" > --
ALTER TABLE ch16.twin_cities ADD COLUMN source integer; -- <co id="co_code_souce_target_add_topology_1"/>
ALTER TABLE ch16.twin_cities ADD COLUMN target integer; -- <co id="co_code_souce_target_add_topology_2"/>
SELECT pgr_CreateTopology(
	'ch16.twin_cities',
	0.000001,
	'geom',
	'gid',
	'source',
	'target'
); -- <co id="co_code_souce_target_add_topology_3"/> --
-- <end id="code_souce_target_add_topology" > --

-- <start id="code_costing_length" > --
ALTER TABLE ch16.twin_cities ADD COLUMN length float8; -- <co id="co_code_costing_length_1"/>
UPDATE ch16.twin_cities 
SET length = ST_Length(ST_Transform(geom,4326)::geography); -- <co id="co_code_costing_length_2"/>
-- <end id="code_costing_length" > --

-- <start id="code_dijkstra_twin_cities_join" > --
SELECT pd.seq, e.geom, pd.cost, pd.id1 As node
INTO ch16.dijkstra_result
FROM 
	pgr_Dijkstra(
		'SELECT gid AS id, source, target, length As cost 
		FROM ch16.twin_cities', -- <co id="co_code_dijkstra_twin_cities_join_1"/>
		134, -- <co id="co_code_dijkstra_twin_cities_join_2"/>
		33, -- <co id="co_code_dijkstra_twin_cities_join_3"/>
		false, -- <co id="co_code_dijkstra_twin_cities_join_4"/>
		false -- <co id="co_code_dijkstra_twin_cities_join_5"/>
    ) As pd -- <co id="co_code_dijkstra_twin_cities_join_6"/>
    LEFT JOIN 
	ch16.twin_cities As e 
	ON pd.id2 = e.gid
ORDER BY pd.seq;
-- <end id="code_dijkstra_twin_cities_join" > --
 
-- <start id="code_traveling_create_table"/> -- 
CREATE TABLE spain_nuclear_plants(
	id serial, 
	plant varchar(150), 
	lat double precision, 
	lon double precision
);
-- <end id="code_traveling_create_table"/> -- 
 
-- <start id="code_pgr_tsp_spain_nuclear_plants"/> -- 
SELECT seq, t.id1, p.id, p.plant
FROM 
	pgr_tsp(
		'SELECT id, lon AS x, lat AS y 
		FROM ch16.spain_nuclear_plants', -- <co id="co_code_pgr_tsp_spain_nuclear_plants_1"/>
		1, -- <co id="co_code_pgr_tsp_spain_nuclear_plants_2"/>
		7 -- <co id="co_code_pgr_tsp_spain_nuclear_plants_3"/>
	) As t 
    INNER JOIN 
	ch16.spain_nuclear_plants As p 
	ON t.id2 = p.id -- <co id="co_code_pgr_tsp_spain_nuclear_plants_4"/>
ORDER BY seq;
-- <end id="code_pgr_tsp_spain_nuclear_plants"/> -- 

-- <start id="code_save_pg_rdata"/> -- 
CREATE OR REPLACE FUNCTION ch16.save_places_rdata() RETURNS text AS
$$
places_mega <<- pg.spi.exec("
	SELECT name, latitude, longitude FROM ch16.places WHERE megacity = 1
")  -- <co id="co_code_save_pg_rdata_1"/>      
nb <<- pg.spi.exec("
	SELECT name, latitude, longitude 
	FROM ch16.places
	WHERE ST_DWithin(geog,ST_GeogFromText('POINT(7.5 9.0)'),1000000) 
") -- <co id="co_code_save_pg_rdata_1b"/>
save(places_mega, nb, file="C:/Temp/places.RData") -- <co id="co_code_save_pg_rdata_2"/>
return("done")
$$
LANGUAGE 'plr';
-- <end id="code_save_pg_rdata"/> -- 

-- start id="code_r_graph_income_house" --
CREATE OR REPLACE FUNCTION ch16.graph_income_house() RETURNS text AS
$$
randdata <<- pg.spi.exec("  
	SELECT x As income,AVG(x*(1+random()*y)) As avgprice
	FROM 
		generate_series(2000,100000,10000) As x 
		CROSS JOIN 
		generate_series(1,5) As y
	GROUP BY x 
	ORDER BY x
") -- <co id="co_code_r_graph_income_house_1"/>
png('C:/temp/housepercap.png',width=500,height=400) -- <co id="co_code_r_graph_income_house_2"/>
opar <- par(bg="white") -- <co id="co_code_r_graph_income_house_3"/>
plot(x=randdata$income,y=randdata$avgprice,ann=FALSE,type="n") -- <co id="co_code_r_graph_income_house_4"/> 
yrange = range(randdata$avgprice)
abline(
	h=seq(yrange[1],yrange[2],(yrange[2]-yrange[1])/10),
	lty=1,col="grey"
) -- <co id="co_code_r_graph_income_house_5"/> 
lines(x=randdata$income,y=randdata$avgprice,col="green4", -- <co id="co_code_r_graph_income_house_6"/> 
   lty="dotted") 
points(x=randdata$income,y=randdata$avgprice,bg="limegreen",pch=23) -- <co id="co_code_r_graph_income_house_7"/> 
title(
	main="Random plot of house price vs. per capita income",
	xlab="Per cap income",ylab="Average House Price",
	col.main="blue",col.lab="red1",font.main=4,font.lab=3
)
dev.off() -- <co id="co_code_r_graph_income_house_8"/> 
return("done")
$$
LANGUAGE 'plr';
--# end id="code_r_graph_income_house --

-- <start id="code_r_plot_linestrings"/> --
CREATE OR REPLACE FUNCTION ch16.plot_routing_results()
RETURNS text AS
$$
library(sp)
library(rgeos)
geodata <<- pg.spi.exec("
	SELECT gid, route, ST_AsText(geom) As geomwkt
	FROM ch16.twin_cities 
	ORDER BY gid
") -- <co id="co_code_r_plot_linestrings_1"/> 
ngeom <- length(geodata$gid)
row.names(geodata) = geodata$gid
for (i in 1:ngeom) { -- <co id="co_code_r_plot_linestrings_2"/>     
	if (i == 1) {
		geo.sp = readWKT(geodata$geomwkt[i],geodata$gid[i])
	}
	else {
		geo.sp = rbind(
			geo.sp,readWKT(geodata$geomwkt[i],geodata$gid[i])
		)    
	}
} -- <co id="co_code_r_plot_linestrings_2a"/>
sdf <- SpatialLinesDataFrame(geo.sp, geodata[-3]) -- <co id="co_code_r_plot_linestrings_3"/>
georesult <<- pg.spi.exec("
	SELECT ST_AsText(ST_LineMerge(ST_Collect(geom))) As geomwkt
	FROM ch16.dijkstra_result
") -- <co id="co_code_r_plot_linestrings_4"/>
  
sdf_result <- SpatialLinesDataFrame(
	readWKT(georesult$geomwkt[1],"result"),
	data = data.frame(c("result")),
	match.ID=FALSE
) -- <co id="co_code_r_plot_linestrings_5"/>
png('C:/temp/twin_bestpath.png',width=500,height=400) -- <co id="co_code_r_plot_linestrings_6"/>
plot(sdf,xlim=c(-94,-93),ylim=c(44.5,45.5),axes=TRUE); -- <co id="co_code_r_plot_linestrings_7"/>
lines(sdf_result,col="green4",lty="dashed",type="o") -- <co id="co_code_r_plot_linestrings_8"/>
title(
	main="Travel options to Twin Cities",font.main=4,col.main="red", 
	xlab="Longitude",ylab="Latitude"
) -- <co id="co_code_r_plot_linestrings_9"/>
dev.off()
return("done")
$$
LANGUAGE 'plr' VOLATILE;
-- <end id="code_r_plot_linestrings"/> --

-- <start id="code_plpython_write_bin_file"/> --
CREATE OR REPLACE FUNCTION ch16.write_bin_file(
	param_bytes bytea,
	param_filename text
)
RETURNS text AS 
$$
f = open('C:/temp/' + param_filename, 'wb+') -- <co id="co_code_plpython_write_bin_file_1"/>
f.write(param_bytes) -- <co id="co_code_plpython_write_bin_file_2"/>
f.close()
return param_filename -- <co id="co_code_plpython_write_bin_file_3"/>
$$ LANGUAGE plpython3u IMMUTABLE;
-- <end id="code_plpython_write_bin_file"/> --

-- <start id="code_plpython_write_bin_file"/> --
CREATE OR REPLACE FUNCTION ch16.read_bin_file(param_filename text)
RETURNS bytea AS 
$$
f = open('C:/temp/' + param_filename, 'rb') 
var_bytes = f.read(10000000000) -- <co id="co_code_plpython_read_bin_file_1"/>
f.close()
return var_bytes
$$ LANGUAGE plpython3u;
-- <end id="code_plpython_read_bin_file"/> --

-- <start id="code_plpython_write_bin_file_use"/> --
SELECT 
	ch16.write_bin_file(
		ST_AsPNG(ST_AsRaster(ST_Collect(geom),300,300,'8BUI')),
		'dijkstra_result.png'
	)
FROM ch16.dijkstra_result;
-- <end id="code_plpython_write_bin_file_use"/> --
  
-- <start id="code_plpython_fngetxlspts"/> --
CREATE OR REPLACE FUNCTION ch16.fngetxlspts(
	param_filename text,
	OUT place text, OUT lon float, OUT lat float
)
RETURNS SETOF RECORD AS
$$
import xlrd -- <co id="co_code_plpython_fngetxlspts_1"/>
book = xlrd.open_workbook(param_filename)
sh = book.sheet_by_index(0)  
for rx in range(1,sh.nrows): -- <co id="co_code_plpython_fngetxlspts_2"/>
yield(
	sh.cell_value(rowx=rx,colx=0), -- <co id="co_code_plpython_fngetxlspts_3_1"/>
	sh.cell_value(rowx=rx,colx=1), -- <co id="co_code_plpython_fngetxlspts_3_2"/>
	sh.cell_value(rowx=rx,colx=2) -- <co id="co_code_plpython_fngetxlspts_3_3"/>
)                                                        
$$
LANGUAGE 'plpython3u' VOLATILE;
-- <end id="code_plpython_fngetxlspts"/> --

-- <start id="code_plpython_fngetxlspts_use"/> --
SELECT place, ST_SetSRID(ST_Point(lon,lat),4326) As geom
FROM ch16.fngetxlspts('C:/Temp/Test.xls') AS foo;
-- <end id="code_plpython_fngetxlspts_use"/> --

-- <start id="code_plpython_list_files"/> 
CREATE FUNCTION ch16.list_files(param_filepath text) RETURNS SETOF text 
AS
$$
import os
return os.listdir(param_filepath)
$$
LANGUAGE 'plpython3u' VOLATILE;
-- <end id="code_plpython_list_files"/>

-- <start id="code_plpython_list_files_use"/>
SELECT file 
FROM ch16.list_files('C:/temp') As file 
WHERE file LIKE '%.xls';
-- <end id="code_plpython_list_files_use"/>

-- <start id="code_plpython_list_files_xls_use"/> --
SELECT DISTINCT pt.place, pt.lon, pt.lat
FROM 
	ch16.list_files('C:/temp') AS file, -- <co id="co_code_plpython_list_files_xls_use_1"/> 
    LATERAL
	ch16.fngetxlspts('C:/temp/' || file) As pt -- <co id="co_code_plpython_list_files_xls_use_2"/>
WHERE file LIKE '%.xls' -- <co id="co_code_plpython_list_files_xls_use_3"/>
-- <end id="code_plpython_list_files_xls_use"/> --

-- <start id="code_plpython_google_geocode"/> --
CREATE FUNCTION ch16.google_geocode(
	param_addr text,
	OUT address text, OUT lon numeric, OUT lat numeric
) -- <co id="co_code_plpython_google_geocode_1"/> --
RETURNS record
AS
$$
from geopy.geocoders import GoogleV3 -- <co id="co_code_plpython_google_geocode_2"/>
geoc = GoogleV3()
address, 
(latitude,longitude) = geoc.geocode(param_addr) -- <co id="co_code_plpython_google_geocode_3"/>
return (address, longitude, latitude) -- <co id="co_code_plpython_google_geocode_4"/>
$$
LANGUAGE 'plpython3u';
-- <end id="code_plpython_google_geocode"/> --

-- <start id="code_plpython_google_geocode_use"/>--
SELECT * 
FROM ch16.google_geocode(
	'1731 New Hampshire Avenue Northwest, Washington, DC 20010'
);
--<end id="code_plpython_google_geocode_use"/> --

-- <start id="code_plv8_parse_gps_usage"/> --
SELECT ch16.parse_gps('36°57''9" N 110°4''21" W');
-- outputs
{36.9525,-110.0725}
-- <end id="code_plv8_parse_gps_usage"/> --

-- <start id="code_plv8_st_max4ma"/> --
CREATE FUNCTION ch16.plv8_st_max4ma(
    value float8[][][],
    pos integer[][][],
    VARIADIC userargs text[] DEFAULT NULL::text[]
)
RETURNS double precision AS
$$
    return Math.max.apply(null,value);
$$
LANGUAGE plv8 IMMUTABLE;
-- <end id="code_plv8_st_max4ma"/> --

-- code_plv8_st_range4ma --
CREATE FUNCTION ch16.plv8_st_range4ma(
    value float8[][][], 
    pos integer[][][], 
    VARIADIC userargs text[] DEFAULT NULL::text[]
)
RETURNS double precision AS
$$
    return(Math.max.apply(null,value) - Math.min.apply(null,value);
$$
LANGUAGE plv8 IMMUTABLE;
-- code_plv8_st_range4ma --

-- <start id="code_sql_st_range4ma"/> --
CREATE FUNCTION ch16.sql_st_range4ma(
    value float8[][][],
    pos integer[][][], 
    VARIADIC userargs text[] DEFAULT NULL::text[]
)
RETURNS double precision AS
$$
    SELECT MAX(v) - MIN(v) FROM unnest($1) As v;
$$
LANGUAGE sql IMMUTABLE;
-- <end id="code_sql_st_range4ma"/> --
  
-- <start id="code_compare_speed_range4ma"/> --
SELECT 
    ch16.write_bin_file(
        ST_AsPNG(
            ST_MapAlgebra(
                ST_Clip(
					rast,
					ST_Expand(ST_Centroid(rast::geometry),300)
				),
                1,
                'ch16.plv8_st_range4ma(
                    double precision[][][],
                    integer[][],
                    text[]
                )'::regprocedure,
                '8BUI','FIRST',NULL,2,2
            )
        ),
        RID::TEXT || '_plv8_range2.png'
    )
FROM ch16.pics; -- <co id="co_code_compare_speed_range4ma_1"/>

SELECT 
    ch16.write_bin_file(
        ST_AsPNG(
            ST_MapAlgebra( 
                ST_Clip(
					rast,
					ST_Expand(ST_Centroid(rast::geometry),300)
				),
                1,
                'ch16.sql_st_range4ma(
                    double precision[][][],
                    integer[][],
                    text[]
                )'::regprocedure,
                '8BUI','FIRST',NULL,2,2 
            )
        ),
        RID::TEXT || '_sql_range2.png'
    )
FROM ch16.pics; -- <co id="co_code_compare_speed_range4ma_2"/>

SELECT 
    ch16.write_bin_file(
        ST_AsPNG(
            ST_MapAlgebra( 
                ST_Clip(
					rast,
					ST_Expand(ST_Centroid(rast::geometry),300)
				),   
                1,
                'st_range4ma(
                    double precision[][][],
                    integer[][],
                    text[]
                )'::regprocedure,
                '8BUI','FIRST',NULL,2,2
            )
        ),
        RID::TEXT || '_builtin_range2.png')
FROM ch16.pics;  -- <co id="co_code_compare_speed_range4ma_3"/>
-- <end id="code_compare_speed_range4ma"/> --

-- <start id="code_create_plv8_modules"/> --
CREATE TABLE ch16.plv8_modules(
    modname text PRIMARY KEY,
    load_on_start boolean,
    code text
);
-- <end id="code_create_plv8_modules"/> --

-- <start id="code_plv8_module_compiler"/> --
CREATE OR REPLACE FUNCTION ch16.plv8_startup()
RETURNS void AS
$$ -- <co id="co_code_plv8_module_compiler_1"/>
    var rows = plv8.execute(
        "SELECT modname, code " + 
        " FROM ch16.plv8_modules WHERE load_on_start"
    );
    for (var r = 0; r < rows.length; r++) {
        var code = rows[r].code;
        eval("(function() { " + code + "})")(); -- <co id="co_code_plv8_module_compiler_2"/>
    };
$$
LANGUAGE plv8;

SELECT ch16.plv8_startup(); -- <co id="co_code_plv8_module_compiler_3"/>
-- <end id="code_plv8_module_compiler"/> --

-- <start id="code_plv8_dummy_data_with_chance"/> --
CREATE TABLE ch16.people(
    id serial primary key, -- <co id="co_code_plv8_dummy_data_with_chance_1"/>
    first_name varchar(50), last_name varchar(50), 
    gender varchar(15), geog geography(POINT,4326)
);
DO LANGUAGE plv8
$$ -- <co id="co_code_plv8_dummy_data_with_chance_2"/>
    var sql = 
        "INSERT INTO ch16.people(first_name,last_name,gender,geog) 
        VALUES($1,$2,$3,ST_Point($4,$5)::geography)" -- <co id="co_code_plv8_dummy_data_with_chance_3"/>
    var iplan = plv8.prepare(
        sql,
        ['text','text','text','numeric','numeric']
    ); -- <co id="co_code_plv8_dummy_data_with_chance_4"/>
    for (var i=0; i < 10000; i++) {
        iplan.execute([
            chance.first(),
            chance.last(),
            chance.gender(),
            chance.longitude(),
            chance.latitude()
        ]);
    }
$$;
-- <end id="code_plv8_dummy_data_with_chance"/> --