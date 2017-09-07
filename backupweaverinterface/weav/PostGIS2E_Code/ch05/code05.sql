-- <start id="code_sql_art" /> --
SELECT art.n, art.geom
FROM (
    SELECT 
        n, 
        ST_Translate( -- <co id="co_code_sql_art_1" /> --
            ST_Buffer(
                ST_MakeLine(pt), mod(n,6) + 2, -- <co id="co_code_sql_art_3" /> --
                'endcap=' || endcaps[mod(n,3) + 1] || ' join=' || 
                joins[mod(n,array_upper(joins,1)) + 1] || 
                ' quad_segs=' || n
            ), -- <co id="co_code_sql_art_2" /> --
        n*10,n*random()*pi() 
    ) As geom
FROM (
    SELECT ceiling(random()*100)::integer As n, 
        ARRAY['square', 'round', 'flat'] As endcaps, 
        ARRAY['round','mitre','bevel'] As joins, 
        ST_Point(x*random(),y*random()) As pt 
    FROM generate_series(1,200, 7) As x 
        CROSS JOIN generate_series(1,500,20) As y
) As foo
GROUP BY foo.n, foo.endcaps, foo.joins
HAVING count(foo.n) > 10) As art;
-- <end id="code_sql_art" /> --