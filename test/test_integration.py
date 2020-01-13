# -*- coding: latin-1  -*-
"""Integrations tests for Data Weaver"""
from __future__ import print_function

import json
import os
import shlex
import shutil
import subprocess
from collections import OrderedDict

import pandas
import pytest
from retriever import dataset_names
from retriever import install_postgres
from retriever import install_sqlite
from retriever import reload_scripts as retriever_reload_scripts

from pydataweaver import reload_scripts as weaver_reload_scripts
from pydataweaver.engines import engine_list
from pydataweaver.lib.defaults import ENCODING
from pydataweaver.lib.engine_tools import create_file
from pydataweaver.lib.load_json import read_json

encoding = ENCODING.lower()

FILE_LOCATION = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))
RETRIEVER_HOME_DIR = os.path.normpath(os.path.expanduser("~/.retriever/"))
RETRIEVER_DATA_DIR = os.path.normpath(os.path.expanduser("~/.retriever/raw_data/"))
RETRIEVER_SCRIPT_DIR = os.path.normpath(os.path.expanduser("~/.retriever/scripts/"))
WEAVER_HOME_DIR = os.path.normpath(os.path.expanduser("~/.pydataweaver/"))
WEAVER_SCRIPT_DIR = os.path.normpath(os.path.expanduser("~/.pydataweaver/scripts/"))
WEAVER_TEST_DATA_PACKAEGES_DIR = os.path.normpath(
    os.path.join(FILE_LOCATION, "test_data_packages"))

# Set postgres password, Appveyor service needs the password given
# The Travis service obtains the password from the config file.
os_password = ""
pgdb_host = "localhost"
mysqldb_host = "localhost"
testdb = "testdb_weaver"
testschema = "testschema_weaver"

if os.name == "nt":
    os_password = "Password12!"

docker_or_travis = os.environ.get("IN_DOCKER")
if docker_or_travis == "true":
    os_password = "Password12!"
    pgdb_host = "pgdb_weaver"
    mysqldb_host = "mysqldb_weaver"

table_one = {
    "name": "table-one",
    "raw_data": ["a,b,c", "1,3,5", "2,4,6"],
    "script": {
        "name": "table-one",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "table_one",
            "schema": {
                "fields": [
                    {
                        "name": "a",
                        "type": "int"
                    },
                    {
                        "name": "b",
                        "type": "int"
                    },
                    {
                        "name": "c",
                        "type": "int"
                    },
                ]
            },
            "url": "http://example.com/table_one.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

table_two = {
    "name": "table-two",
    "raw_data": ["a,d,e", "1,r,UV", "2,s,WX", "3,t,YZ"],
    "script": {
        "name": "table-two",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "table_two",
            "schema": {
                "fields": [
                    {
                        "name": "a",
                        "type": "int"
                    },
                    {
                        "name": "d",
                        "size": "4",
                        "type": "char"
                    },
                    {
                        "name": "e",
                        "size": "4",
                        "type": "char"
                    },
                ]
            },
            "url": "http://example.com/table_two.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

table_three = {
    "name": "table-three",
    "raw_data": ["a,b,e", "1,2,UV", "1,3,WX", "1,0,YZ", "2,4,OP", "2,5,QR"],
    "script": {
        "name": "table-three",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "table_three",
            "schema": {
                "fields": [
                    {
                        "name": "a",
                        "type": "int"
                    },
                    {
                        "name": "b",
                        "type": "int"
                    },
                    {
                        "name": "e",
                        "size": "4",
                        "type": "char"
                    },
                ]
            },
            "url": "http://example.com/table_three.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

table_four = {
    "name": "table-four",
    "raw_data": ["a,f,g", "4,1,4", "2,2,5", "1,3,6"],
    "script": {
        "name": "table-four",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "table_four",
            "schema": {
                "fields": [
                    {
                        "name": "a",
                        "type": "int"
                    },
                    {
                        "name": "f",
                        "size": "4",
                        "type": "char"
                    },
                    {
                        "name": "g",
                        "size": "4",
                        "type": "char"
                    },
                ]
            },
            "url": "http://example.com/table_four.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

table_five = {
    "name": "table-five",
    "raw_data": ["id,a,b,f", "1,1,3,PL", "2,2,4,PT", "3,2,4,PX"],
    "script": {
        "name": "table-five",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "table_five",
            "schema": {
                "fields": [
                    {
                        "name": "id",
                        "type": "int"
                    },
                    {
                        "name": "a",
                        "type": "int"
                    },
                    {
                        "name": "b",
                        "type": "int"
                    },
                    {
                        "name": "f",
                        "size": "4",
                        "type": "char"
                    },
                ]
            },
            "url": "http://example.com/table_five.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

# Retriever script and data
RETRIEVER_TESTS_DATA = [table_one, table_two, table_three, table_four, table_five]

# Retriever script names
TESTS_SCRIPTS = [data_dict["name"] for data_dict in RETRIEVER_TESTS_DATA]

# Weaver defaults
# Engines
postgres_engine, sqlite_engine = engine_list

# Weaver test data(Tuple)
# (Script file name with no extension, script name, result table, expected)

WEAVER_TEST_DATA = [
    # TODO: un-comment and ensure test passes
    (
        "multi_columns_multi_tables_caps",
        "tables-a-c-e-columns-a-b-caps",
        "tables-a-c-e-columns-a-b-caps.a_b_e.csv",
        {
            "t1_a": [1, 2, 2],
            "t1_b": [3, 4, 4],
            "t1_c": [5, 6, 6],
            "as_0_e": ["WX", "OP", "OP"],
            "as_1_id": [1, 2, 3],
            "as_1_f": ["PL", "PT", "PX"],
        },
    ),
    (
        "multi_columns_multi_tables",
        "tables-a-c-e-columns-a-b",
        "tables-a-c-e-columns-a-b.a_b_e.csv",
        {
            "t1_a": [1, 2, 2],
            "t1_b": [3, 4, 4],
            "t1_c": [5, 6, 6],
            "as_0_e": ["WX", "OP", "OP"],
            "as_1_id": [1, 2, 3],
            "as_1_f": ["PL", "PT", "PX"],
        },
    ),
    (
        "one_column_multi_tables",
        "tables-a-b-d-columns-a",
        "tables-a-b-d-columns-a.a_b_d.csv",
        {
            "t1_a": [1, 2],
            "t1_b": [3, 4],
            "t1_c": [5, 6],
            "as_0_e": ["UV", "WX"],
            "as_0_d": ["r", "s"],
            "as_1_g": [6, 5],
            "as_1_f": [3, 2],
        },
    ),
    (
        "simple_join_one_column_custom",
        "tables-a-b-columns-a-custom",
        "tables-a-b-columns-a-custom.a_b_custom.csv",
        {
            "t1_a": [1, 2],
            "t1_b": [3, 4],
            "t1_c": [5, 6],
            "as_0_e": ["UV", "WX"]
        },
    ),
    (
        "simple_join_two_column",
        "tables-a-c-columns-a-b",
        "tables-a-c-columns-a-b.a_b.csv",
        {
            "t1_a": [1, 2],
            "t1_b": [3, 4],
            "t1_c": [5, 6],
            "as_0_e": ["WX", "OP"]
        },
    ),
    (
        "simple_join_one_column",
        "tables-a-b-columns-a",
        "tables-a-b-columns-a.a_b.csv",
        {
            "t1_a": [1, 2],
            "t1_b": [3, 4],
            "t1_c": [5, 6],
            "as_0_e": ["UV", "WX"],
            "as_0_d": ["r", "s"],
        },
    ),
]

# File names without `.json` extension
WEAVER_TEST_DATA_PACKAGE_FILES = [
    file_base_names[0] for file_base_names in WEAVER_TEST_DATA
]
weaver_test_parameters = [(test[1], test[2], test[3]) for test in WEAVER_TEST_DATA]


def set_retriever_resources(resource_up=True):
    """Create or tear down retriever data and scripts

    if resource_up =True, set up retriever else tear down
    Data directory uses "-", data file names uses "_"
    script file names uses "_"
    """
    for file_names in RETRIEVER_TESTS_DATA:
        data_dir_path = os.path.join(RETRIEVER_DATA_DIR, file_names["name"])
        data_dir_path = os.path.normpath(data_dir_path)
        data_file_name = file_names["name"].replace("-", "_") + ".txt"
        data_file_path = os.path.normpath(os.path.join(data_dir_path, data_file_name))
        script_name = file_names["script"]["name"] + ".json"
        script_file_path = os.path.normpath(
            os.path.join(RETRIEVER_SCRIPT_DIR, script_name.replace("-", "_")))

        # Set or tear down raw data files
        # in '~/.retriever/raw_data/data_dir_path/data_file_name'
        if resource_up:
            if not os.path.exists(data_dir_path):
                os.makedirs(data_dir_path)
                create_file(file_names["raw_data"], data_file_path)
            if not os.path.exists(RETRIEVER_SCRIPT_DIR):
                os.makedirs(RETRIEVER_SCRIPT_DIR)
            with open(script_file_path, "w") as js:
                json.dump(file_names["script"], js, indent=2)
            retriever_reload_scripts()
        else:
            shutil.rmtree(data_dir_path)
            os.remove(script_file_path)


def file_exists(path):
    """Return true if a file exists and its size is greater than 0."""
    return os.path.isfile(path) and os.path.getsize(path) > 0


# WEAVER


def set_weaver_data_packages(resources_up=True):
    """Setup or tear down pydataweaver test scripts

    Copy or delete pydataweaver test scripts from test_data directory,
    WEAVER_TEST_DATA_PACKAEGES_DIR
    to ~/.pydataweaver script directory WEAVER_SCRIPT_DIR
    """
    if resources_up:
        if not WEAVER_SCRIPT_DIR:
            os.makedirs(WEAVER_SCRIPT_DIR)
    for file_name in WEAVER_TEST_DATA_PACKAGE_FILES:
        if resources_up:
            scr_pack_path = os.path.join(WEAVER_TEST_DATA_PACKAEGES_DIR,
                                         file_name + ".json")
            pack_path = os.path.normpath(scr_pack_path)
            shutil.copy(pack_path, WEAVER_SCRIPT_DIR)
            weaver_reload_scripts()
        else:
            dest_pack_path = os.path.join(WEAVER_SCRIPT_DIR, file_name + ".json")
            dest_path = os.path.normpath(dest_pack_path)
            if os.path.exists(dest_path):
                os.remove(dest_path)


def install_to_database(dataset, install_function, config):
    install_function(dataset, **config)
    return


def install_sqlite_regression(dataset):
    """Install test dataset into sqlite."""
    dbfile = os.path.normpath(os.path.join(os.getcwd(), testdb + ".sqlite"))
    sqlite_engine.opts = {
        "engine": "sqlite",
        "file": dbfile,
        "table_name": "{db}_{table}",
    }
    interface_opts = {"file": dbfile}
    install_to_database(dataset, install_sqlite, interface_opts)


def setup_sqlite_retriever_db():
    teardown_sqlite_db()
    for test_data in RETRIEVER_TESTS_DATA:
        install_sqlite_regression(test_data["script"]["name"])


def teardown_sqlite_db():
    dbfile = os.path.normpath(os.path.join(os.getcwd(), testdb + ".sqlite"))
    subprocess.call(["rm", "-r", dbfile])


def teardown_weaver_scripts():
    set_weaver_data_packages(resources_up=False)


def teardown_retriever_scripts():
    set_retriever_resources(resource_up=False)


def install_dataset_postgres(dataset):
    postgres_engine.opts = {
        "engine": "postgres",
        "user": "postgres",
        "password": os_password,
        "host": pgdb_host,
        "port": 5432,
        "database": testdb,
        "database_name": testschema,
        "table_name": "{db}.{table}",
    }
    interface_opts = {
        "user": "postgres",
        "password": postgres_engine.opts["password"],
        "host": postgres_engine.opts["host"],
        "database": postgres_engine.opts["database"],
        "database_name": postgres_engine.opts["database_name"],
        "table_name": postgres_engine.opts["table_name"],
    }
    install_to_database(dataset, install_postgres, interface_opts)


def setup_postgres_retriever_db():
    for test_data in RETRIEVER_TESTS_DATA:
        install_dataset_postgres(test_data["script"]["name"])


def teardown_postgres_db():
    # Retriever database
    cmd = ("psql -U postgres -d " + testdb + "-h " + pgdb_host +
           ' -w -c "DROP SCHEMA IF EXISTS ' + testschema + 'CASCADE"')
    try:
        subprocess.call(shlex.split(cmd))
    except:
        pass

    # Weaver database
    for file_base_names in WEAVER_TEST_DATA:
        dataset = file_base_names[1]
        sql_stm = "DROP SCHEMA IF EXISTS " + dataset.replace("-", "_") + " CASCADE"
        cmd = ("psql -U postgres -d " + testdb + " -h " + pgdb_host +
               ' -w -c "{sql_stm}"')
        dfd = cmd.format(sql_stm=sql_stm)
        try:
            subprocess.call(shlex.split(dfd))
        except:
            pass


# Test Retriever resources
def test_retriever_test_resources():
    """Test retriever resource files"""
    scrpts_and_raw_data = True
    # ToDOs: Change tests the db_md5 and make it Global
    for items in TESTS_SCRIPTS:
        retriever_raw_data_path = os.path.normpath(
            os.path.join(RETRIEVER_HOME_DIR, "raw_data", items,
                         items.replace("-", "_") + ".txt"))
        if not file_exists(retriever_raw_data_path):
            scrpts_and_raw_data = False
        retriever_script_path = os.path.normpath(
            os.path.join(RETRIEVER_HOME_DIR, "scripts",
                         items.replace("-", "_") + ".json"))
        if not file_exists(retriever_script_path):
            scrpts_and_raw_data = False
    assert scrpts_and_raw_data is True


def test_restiever_test_scripts():
    """Test Retriever test scripts"""
    datasets_list = dataset_names()
    assert set(TESTS_SCRIPTS).issubset(
        set(datasets_list['online'] + datasets_list['offline']))


def test_weaver_test_data_packages():
    """Test available Pydataweaver test scripts"""
    data_packages_exists = True
    for weaver_script in WEAVER_TEST_DATA_PACKAGE_FILES:
        file_paths = os.path.join(WEAVER_SCRIPT_DIR, weaver_script + ".json")
        if not file_exists(os.path.normpath(file_paths)):
            data_packages_exists = False
    assert data_packages_exists is True


def get_script_module(script_name):
    """Load script modules."""
    print(os.path.join(WEAVER_HOME_DIR, "scripts", script_name))
    return read_json(os.path.join(WEAVER_HOME_DIR, "scripts", script_name))


def get_output_as_csv(dataset, engines, db):
    """Integrate datasets and return the output as a csv."""
    import pydataweaver

    weaver_reload_scripts()
    eng = pydataweaver.join_postgres(dataset,
                                     database=testdb,
                                     host=pgdb_host,
                                     password=os_password)
    csv_file = eng.to_csv()
    return csv_file


def teardown_module():
    teardown_postgres_db()
    teardown_sqlite_db()
    teardown_weaver_scripts()
    teardown_retriever_scripts()


def setup_module():
    """Set up resources used for testing."""
    set_retriever_resources(resource_up=True)
    set_weaver_data_packages(resources_up=True)

    # set up postgres database
    setup_postgres_retriever_db()
    setup_sqlite_retriever_db()


@pytest.mark.parametrize("dataset, csv_file, expected", weaver_test_parameters)
def test_postgres(dataset, csv_file, expected):
    tmpdir = None
    postgres_engine.opts = {
        "engine": "postgres",
        "user": "postgres",
        "password": os_password,
        "host": pgdb_host,
        "port": 5432,
        "database": testdb,
        "database_name": testschema,
        "table_name": "{db}.{table}",
    }
    interface_opts = {
        "user": "postgres",
        "password": postgres_engine.opts["password"],
        "host": postgres_engine.opts["host"],
        "database": postgres_engine.opts["database"],
        "database_name": postgres_engine.opts["database_name"],
        "table_name": postgres_engine.opts["table_name"],
    }
    res_csv = get_output_as_csv(dataset,
                                postgres_engine,
                                db=postgres_engine.opts["database_name"])
    df = pandas.DataFrame.from_dict(OrderedDict(expected))
    data = pandas.read_csv(res_csv)
    os.remove(res_csv)

    # The SQL results returned always change in order.
    # tests the equality of column names and then tests the sorted data frames
    assert sorted(list(data.columns)) == sorted(list(df.columns))
    data = data[sorted(sorted(list(data.columns)))]
    df = df[sorted(sorted(list(df.columns)))]
    assert df.equals(data)
