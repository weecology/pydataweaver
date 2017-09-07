<?php
    include_once("config.inc.php");
    $param_geom = $_REQUEST['geom'];
    $param_table = $_REQUEST['table'];
    $param_props = $_REQUEST['props'];
    $dbconn = pg_connect(DSN);

    $res = pg_query_params($dbconn, 
       'SELECT ch17.get_features($1,$2,$3) As result ', 
         array($param_geom, $param_table,$param_props));
    $val = pg_fetch_result($res,0,0);
    echo $val;

?>
