# -*- coding: latin-1  -*-
# Integrations tests for Data Weaver.
# The tests use the Data Retriever platform to install
# all the required datasets and the Pydataweaver integrates
# the datasets.
from __future__ import print_function

import json
import os
import shlex
import shutil
import subprocess
import time
from urllib.request import urlretrieve

import pytest
import retriever as rt

import pydataweaver as wt
from pydataweaver.engines import engine_list
from pydataweaver.lib.defaults import ENCODING
from pydataweaver.lib.engine_tools import create_file

encoding = ENCODING.lower()
FILE_LOCATION = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))
RETRIEVER_HOME_DIR = os.path.normpath(os.path.expanduser("~/.retriever/"))
RETRIEVER_DATA_DIR = os.path.normpath(os.path.expanduser("~/.retriever/raw_data/"))
RETRIEVER_SCRIPT_DIR = os.path.normpath(os.path.expanduser("~/.retriever/scripts/"))
WEAVER_HOME_DIR = os.path.normpath(os.path.expanduser("~/.pydataweaver/"))
WEAVER_SCRIPT_DIR = os.path.normpath(os.path.expanduser("~/.pydataweaver/scripts/"))
WEAVER_TEST_DATA_PACKAEGES_DIR = os.path.normpath(
    os.path.join(FILE_LOCATION, "test_data_packages"))

RETRIEVER_GIS_REPO = ("https://raw.githubusercontent.com/weecology"
                      "/retriever/master/test/raw_data_gis/scripts/{script_names}.json")

postgres_engine, _ = engine_list

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

test_sample_wgs84 = {
    "name": "testsurveryone",
    "raw_data": [
        "site_id, state, longitude, latitude, habitat_code",
        "1,QP,-117.20,40.04, H1",
        "2,QR,-112.10,41.00, H2",
        "3,QS,-115.58,34.50, HA",
        "4,QT,-114.62,36.78, H3",
        "5,QU,-111.70,32.97, H4",
        "6,Qv,-120.09,35.62, H5",
        "7,QX,-120.68,38.84, H6",
    ],
    "script": {
        "name": "testsurveryone",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "sites",
            "schema": {
                "fields": [
                    {
                        "name": "site_id",
                        "type": "int"
                    },
                    {
                        "name": "state",
                        "size": "4",
                        "type": "char"
                    },
                    {
                        "name": "longitude",
                        "type": "double"
                    },
                    {
                        "name": "latitude",
                        "type": "double"
                    },
                    {
                        "name": "habitat_code",
                        "size": "4",
                        "type": "char"
                    },
                ]
            },
            "url": "http://example.com/testsurveryone.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

test_sample_nad83 = {
    "name": "testsurverytwo",
    "raw_data": [
        "site_id, state, longitude, latitude, habitat_code",
        "1,QP,-2152956,2033827, HA",
        "2,QR,-2001329,1867986, HA",
        "3,QS,-1598571,1221204, HA",
        "4,QT,-1735983,2180715, HA",
        "5,QU,-1240827,2064625, HA",
    ],
    "script": {
        "name": "testsurverytwo",
        "resources": [{
            "dialect": {
                "do_not_bulk_insert": "True"
            },
            "name": "sites",
            "schema": {
                "fields": [
                    {
                        "name": "site_id",
                        "type": "int"
                    },
                    {
                        "name": "state",
                        "size": "4",
                        "type": "char"
                    },
                    {
                        "name": "longitude",
                        "type": "double"
                    },
                    {
                        "name": "latitude",
                        "type": "double"
                    },
                    {
                        "name": "habitat_code",
                        "size": "4",
                        "type": "char"
                    },
                ]
            },
            "url": "http://example.com/testsurverytwo.txt",
        }],
        "retriever": "True",
        "version": "1.0.0",
    },
}

RETRIEVER_TESTS_DATA = [test_sample_wgs84, test_sample_nad83]
RETRIEVER_SPATIAL_DATA = [
    "test-eco-level-four",
    "test-raster-bio1",
    "test-raster-bio2",
    "test-us-eco",
]
survey_scripts = [test_scr["script"]["name"] for test_scr in RETRIEVER_TESTS_DATA]
all_script_names = survey_scripts + RETRIEVER_SPATIAL_DATA

WEAVER_TEST_SCRIPTS = [
    # ("test-vector-multi-raster", "csvfile_name", "dd"),
    ("test-multi-vector", "csvfile_name", "dd"),
    ("test-raster", "csvfile_name", "dd"),
    ("test-vector", "csvfile_name", "dd"),
    ("test-multi-raster", "csvfile_name", "dd"),
]
WEAVER_TEST_DATA_PACKAGE_FILES = [
    file_base_names[0].replace("-", "_") for file_base_names in WEAVER_TEST_SCRIPTS
]


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
        else:
            dest_pack_path = os.path.join(WEAVER_SCRIPT_DIR, file_name + ".json")
            dest_path = os.path.normpath(dest_pack_path)
            if os.path.exists(dest_path):
                os.remove(dest_path)
    wt.reload_scripts()


def set_retriever_res(resource_up=True):
    """Create or tear down retriever data and scripts

    If resource_up, set up retriever else tear down.
    Data directory names use "-",
    Data file names use "_"
    Script file names use "_"
    """
    if not os.path.exists(RETRIEVER_SCRIPT_DIR):
        os.makedirs(RETRIEVER_SCRIPT_DIR)
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
            with open(script_file_path, "w") as js:
                json.dump(file_names["script"], js, indent=2)
        else:
            shutil.rmtree(data_dir_path)
            os.remove(script_file_path)
    for script_name in RETRIEVER_SPATIAL_DATA:
        file_name = script_name.replace("-", "_")
        script_file_path = os.path.normpath(
            os.path.join(RETRIEVER_SCRIPT_DIR,
                         script_name.replace("-", "_") + ".json"))
        if resource_up:
            url = RETRIEVER_GIS_REPO.format(script_names=file_name)
            urlretrieve(url, script_file_path)
        else:
            os.remove(script_file_path)
    rt.reload_scripts()


def file_exists(path):
    """Return true if a file exists and its size is greater than 0."""
    return os.path.isfile(path) and os.path.getsize(path) > 0


def install_to_database(dataset, install_function, config):
    """Install RETRIEVER_SPATIAL_DATA using default db and schema names"""
    install_function(dataset, **config)
    return


def install_dataset_postgres(dataset):
    """Retriever install test datasets

    Datasets are installed into Postgres
    with the names as the database_name
    """
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
        "table_name": postgres_engine.opts["table_name"],
    }
    install_to_database(dataset, rt.install_postgres, interface_opts)


def setup_postgres_retriever_db():
    """Install the required retriever datasets"""
    for test_data in all_script_names:
        install_dataset_postgres(test_data)


def teardown_postgres_db():
    # Retriever database
    cmd = ("psql -U postgres -d " + testdb + " -h " + pgdb_host +
           ' -w -c "DROP SCHEMA IF EXISTS ' + testschema + ' CASCADE"')
    subprocess.call(shlex.split(cmd))

    # Pydataweaver database
    for dataset in all_script_names:
        sql_stm = "DROP SCHEMA IF EXISTS " + dataset.replace("-", "_") + " CASCADE"
        cmd = ("psql -U postgres -d " + testdb + " -h " + pgdb_host +
               " -w -c '{sql_stm}'")
        dfd = cmd.format(sql_stm=sql_stm)
        subprocess.call(shlex.split(dfd))


# Weaver integration
def get_output_as_csv(dataset, engines, db):
    """Integrate datasets and return the output as a csv."""
    wt.reload_scripts()
    eng = wt.join_postgres(
        dataset,
        database=testdb,
        database_name=testschema,
        host=pgdb_host,
        password=os_password,
    )
    # Wait for 5 seconds
    time.sleep(5)
    csv_file = eng.to_csv()
    return csv_file


def setup_module():
    # Set up postgres database
    teardown_postgres_db()
    set_weaver_data_packages(resources_up=True)
    set_retriever_res(resource_up=True)
    setup_postgres_retriever_db()


def teardown_module():
    """Tear down databases, and delete data package test scripts"""
    teardown_postgres_db()
    set_weaver_data_packages(resources_up=False)
    set_retriever_res(resource_up=False)


@pytest.mark.parametrize("dataset, csv_file, expected", WEAVER_TEST_SCRIPTS)
def test_postgres(dataset, csv_file, expected):
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
        "port": postgres_engine.opts["port"],
        "database": postgres_engine.opts["database"],
        "database_name": postgres_engine.opts["database_name"],
        "table_name": postgres_engine.opts["table_name"],
    }
    res_csv = get_output_as_csv(dataset,
                                postgres_engine,
                                db=postgres_engine.opts["database_name"])
    assert file_exists(res_csv)
    os.remove(res_csv)
