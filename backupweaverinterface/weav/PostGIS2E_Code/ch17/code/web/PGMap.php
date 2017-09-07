<?php
    include_once("config.inc.php");  // <co id="co_code_pgmap_1a" />
    $param_format = $_REQUEST['FORMAT']; //<co id="co_code_pgmap_2a" />
    $param_width = (int) $_REQUEST['WIDTH'];
    $param_height = (int) $_REQUEST['HEIGHT'];
    $param_bbox = $_REQUEST['BBOX'];
    $param_schema = $_REQUEST['SCHEMA'];
    $param_table = $_REQUEST['LAYERS'];
    if ( !empty($_REQUEST['VERSION'])  
    	  && $_REQUEST['VERSION'] == '1.1.1' ) { // <co id="co_code_pgmap_3a" /> 
        $param_srid = (int) str_replace('EPSG:', ''
        	 , $_REQUEST['SRS']);
    }
    else { /** assume 1.3.0 **/
        $param_srid = (int) str_replace('EPSG:', ''
        	 , $_REQUEST['CRS']);
    }

    $dbconn = pg_connect(DSN); // <co id="co_code_pgmap_4a" /> 
    pg_query('SET bytea_output = "escape";'); // <co id="co_code_pgmap_5a" /> 
    $res = pg_query_params($dbconn, 
       'SELECT ch17.get_rast_tile($1, $2, $3, $4,
         $5, $6, $7) As result', 
         array($param_format, $param_width, $param_height,
         	  $param_srid, $param_bbox, $param_schema, $param_table )); // <co id="co_code_pgmap_5a" /> 
    $val = pg_fetch_result($res,0,0); //<co id="co_code_pgmap_5a" /> /
    
    header('Content-type: ' . $param_format); // <co id="co_code_pgmap_8a" /> 
    echo pg_unescape_bytea($val);   // <co id="co_code_pgmap_9a" /> 
?>
