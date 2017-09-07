-- Listing Code filter by table schema
-- <start id="code_information_schema_columns_table_filter" /> --
SELECT c.column_name, c.data_type, c.udt_name,
        c.ordinal_position AS ord_pos,
        c.column_default AS cdefault
    FROM information_schema.columns AS c
    WHERE table_schema = 'ch01' and table_name = 'restaurants'
    ORDER BY c.column_name;
-- <end id="code_information_schema_columns_table_filter" /> --

-- Listing Subselects used in a table alias
-- <start id="code_subselects_in_table_alias" /> --
SELECT s.state, r.cnt_residents, c.land_area
    FROM states As s LEFT JOIN
        (SELECT state, COUNT(res_id) As cnt_residents
            FROM residents
            GROUP BY state) AS r ON s.state = r.state
    LEFT JOIN (SELECT state, SUM(ST_Area(the_geom)) As land_area
            FROM counties
            GROUP BY state) As c
        ON s.state = c.state;
-- <end id="code_subselects_in_table_alias" /> --

-- Listing Same statement written using a correlated subquery
-- <start id="code_using_correlated_subquery" /> --
SELECT s.state,
        (SELECT COUNT(res_id)
            FROM residents
            WHERE residents.state = s.state) AS cnt_residents
    , (SELECT SUM(ST_Area(the_geom))
        FROM counties
         WHERE counties.state = s.state) AS land_area
    FROM states As s ;
-- <end id="code_using_correlated_subquery" /> --