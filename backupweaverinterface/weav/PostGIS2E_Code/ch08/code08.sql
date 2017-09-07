-- code_install_postgis_tiger_geocoder --
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_tiger_geocoder;
-- code_install_postgis_tiger_geocoder --

-- <start id="code_postgis_tiger_geocoder_grant"> --
GRANT USAGE ON SCHEMA tiger TO PUBLIC; -- <co id="co_postgis_tiger_geocoder_grant_1"/> --
GRANT USAGE ON SCHEMA tiger_data TO PUBLIC;
GRANT SELECT, REFERENCES, TRIGGER 
    ON ALL TABLES IN SCHEMA tiger TO PUBLIC;
GRANT SELECT, REFERENCES, TRIGGER 
    ON ALL TABLES IN SCHEMA tiger_data TO PUBLIC;
GRANT EXECUTE 
    ON ALL FUNCTIONS IN SCHEMA tiger TO PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA tiger_data 
GRANT SELECT, REFERENCES 
    ON TABLES TO PUBLIC;-- <co id="co_postgis_tiger_geocoder_grant_2"/>
-- <end id="code_postgis_tiger_geocoder_grant"> --

-- [1] Grant read and execute rights to all users of db
-- [2] Future table permissions

-- <start id="code_geocode_norm"> --
SELECT normalize_address(a) As addy
FROM (
    VALUES 
        ('ONE E PIMA ST STE 999, TUCSON, AZ'),
        ('4758 Reno Road, DC 20017'),
        ('1021 New Hampshare Avenue, Washington, DC 20010'),
        ('1731 New Hampshire Ave Northwest, Washington, DC 20010'),
        ('1 Palisades, Denver, CO')
) X(a);
-- <end id="code_geocode_norm"> --

-- <start id="code_geocode_norm2"> --
WITH A AS (
    SELECT normalize_address(a) As addy
    FROM (
        VALUES 
            ('ONE E PIMA ST STE 999, TUCSON, AZ'),
            ('4758 Reno Road, DC 20017'),
            ('1021 New Hampshare Avenue, Washington, DC 20010'),
            ('1731 New Hampshire Ave Northwest, Washington, DC 20010'),
            ('1 Palisades, Denver, CO')
    ) X(a)
)
SELECT 
    (addy).address As num, 
    (addy).predirabbrev As pre, 
    (addy).streetname || ' ' || (addy).streettypeabbrev As street, 
    (addy).location As city, 
    (addy).stateabbrev As st
FROM A;
-- <end id="code_geocode_norm2"> --

-- <start id="code_geocode_norm3"> --
WITH A AS (
    SELECT pagc_normalize_address(a) As addy
    FROM (
        VALUES 
            ('ONE E PIMA ST STE 999, TUCSON, AZ'),
            ('4758 Reno Road, DC 20017'),
            ('1021 New Hampshare Avenue, Washington, DC 20010'),
            ('1731 New Hampshire Ave Northwest, Washington, DC 20010'),
            ('1 Palisades, Denver, CO')
    ) X(a)
)
SELECT 
    (addy).address As num, 
    (addy).predirabbrev As pre, 
    (addy).streetname || ' ' || (addy).streettypeabbrev As street, 
    (addy).location As city, 
    (addy).stateabbrev As st
FROM A;
-- <end id="code_geocode_norm3"> --

-- <start id="code_standardize_address"> --
WITH A(a) AS (
    VALUES 
        ('ONE E PIMA ST STE 999, TUCSON, AZ'),
        ('4758 Reno Road, DC 20017'),
        ('1021 New Hampshare Avenue, Washington, DC 20010'),
        ('1731 New Hampshire Ave Northwest, Washington, DC 20010'),
        ('1 Palisades, Denver, CO')
)
SELECT (s).house_num, (s).name, (s).predir, (s).suftype, (s).sufdir
FROM (
    SELECT standardize_address(
        'pagc_lex','pagc_gaz','pagc_rules', a
    ) As s FROM A
) AS X;
-- <end id="code_standardize_address"/> --


-- <start id="code_geocode_basic"> --
SELECT 
    g.rating As r, -- <co id="co_code_geocode_basic_1"/> --
    ST_X(geomout) As lon, 
    ST_Y(geomout) As lat, 
    pprint_addy(addy) As paddress -- <co id="co_code_geocode_basic_2"/>
FROM 
    geocode(
        '1731 New Hampshire Avenue Northwest, Washington, DC 20010'
    ) As g;
-- <end id="code_geocode_basic"> --


-- <start id="code_geocode_specific_addy"> --
SELECT 
    g.rating As r, 
    ST_X(g.geomout)::numeric(10,5) As lon,
    ST_Y(g.geomout)::numeric(10,5) As lat, -- <co id="co_code_geocode_specific_addy_1"/> --
    (g.addy).address As snum,
    (g.addy).streetname || ' ' 
        || (g.addy).streettypeabbrev As street,-- <co id="co_code_geocode_specific_addy_2"/>
    (g.addy).zip
FROM geocode('1021 New Hampshare Ave, Washington, DC 20009',1) As g;-- <co id="co_code_geocode_specific_addy_3"/> 
-- <end id="code_geocode_specific_addy"> --

-- <start id="code_geocode_pagc"> --
SELECT g.rating As r, ST_X(geomout) As lon, ST_Y(geomout) As lat 
FROM geocode(
    pagc_normalize_address(
       '1731 New Hampshire Avenue Northwest, Washington, DC 20010'
    )
) As g;
-- <end id="code_geocode_pagc"> --


-- <start id="code_batch_create"> --
DROP TABLE IF EXISTS addr_to_geocode;
CREATE TABLE addr_to_geocode (
    addid serial NOT NULL PRIMARY KEY, 
    rating integer, 
    address text, 
    norm_address text, 
    pt geometry
);
INSERT INTO addr_to_geocode(address)
VALUES 
    ('ONE E PIMA ST STE 999, TUCSON, AZ'),
    ('4758 Reno Road, DC 20017'),
    ('1021 New Hampshare Avenue, Washington, DC 20010'),
    ('1731 New Hampshire Avenue Northwest, Washington, DC 20010'),
    ('1 Palisades, Denver, CO');
-- <end id="code_batch_create"> --


-- <start id="code_standardize_pagc_normalize"/> --
SELECT address As hnum, streetname, streettypeabbrev, 
    postdirabbrev AS postdir, internal As num, stateabbrev As st 
FROM pagc_normalize_address(
    '1731 New Hampshire Avenue Northwest, Washington, DC 20010'
    ) As addy;
-- <end id="code_standardize_pagc_normalize"/> --


-- <start id="code_standardize_normalize"/> --
SELECT address As hnum, streetname, streettypeabbrev, 
    postdirabbrev AS postdir, internal As num, stateabbrev As st 
FROM normalize_address(
    '1731 New Hampshire Avenue Northwest, Washington, DC 20010'
    ) As addy;
-- <end id="code_standardize_normalize"/> --


-- <start id="code_geocode_batch_basic_pre93"> --
UPDATE addr_to_geocode 
SET 
    (rating, norm_address, pt) = -- <co id="co_code_geocode_batch_basic_pre93_1"/> --
    (COALESCE((g).rating,-1 ), pprint_addy( (g).addy), (g).geomout) -- <co id="co_code_geocode_batch_basic_pre93_2"/>
FROM 
    (SELECT * FROM addr_to_geocode 
        WHERE rating IS NULL LIMIT 100) As a -- <co id="co_code_geocode_batch_basic_pre93_3"/> -- 
    LEFT JOIN 
    (SELECT addid,  geocode(address, 1) As g
FROM addr_to_geocode As ag 
    WHERE rating IS NULL) As g1 ON a.addid = g1.addid
WHERE a.addid = addr_to_geocode.addid;
-- <end id="code_geocode_batch_basic_pre93"> --

-- [1] multi-column update
-- [2] select output from geocoder result
-- [3] batches of 100

-- <start id="code_geocode_batch_basic_93"> --
UPDATE addr_to_geocode
SET 
    (rating, norm_address, pt) = 
    (COALESCE((g).rating,-1 ), pprint_addy( (g).addy ), (g).geomout)
FROM 
    (SELECT * FROM addr_to_geocode WHERE rating IS NULL LIMIT 100) As a
    LEFT JOIN LATERAL 
    geocode(a.address, 1) As g  -- <co id="co_code_geocode_batch_basic_93"/> --
    ON ((g).rating < 22)
WHERE a.addid = addr_to_geocode.addid;
-- <end id="code_geocode_batch_basic_93"> --

-- <start id="code_reverse_geocode_batch"> --
SELECT 
    address::varchar(20) as address, 
    pprint_addy((rc).addy[1])::varchar(20) As padd_1,  -- <co id="co_code_reverse_geocode_batch_1"/> --
    (rc).street[1]::varchar(12) As cstreet_1 -- <co id="co_code_reverse_geocode_batch_2"/> --
FROM (
    SELECT address, reverse_geocode(pt) AS rc 
    FROM addr_to_geocode
    WHERE rating between 0 and 20
) AS x;
-- <end id="code_reverse_geocode_batch"> --