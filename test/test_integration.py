# -*- coding: latin-1  -*-
# """Integrations tests for Data Weaver"""
from __future__ import print_function

import json
import os
import shutil
import subprocess
import sys
from collections import OrderedDict
from imp import reload

import pandas
import pytest

from retriever import dataset_names
from retriever import install_postgres
from retriever import install_sqlite
from retriever import reload_scripts as retriever_reload_scripts
from weaver import reload_scripts as weaver_reload_scripts
from weaver.engines import engine_list
from weaver.lib.defaults import ENCODING
from weaver.lib.engine_tools import create_file
from weaver.lib.load_json import read_json

encoding = ENCODING.lower()

reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding(encoding)

FILE_LOCATION = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))
RETRIEVER_HOME_DIR = os.path.normpath(os.path.expanduser('~/.retriever/'))
RETRIEVER_DATA_DIR = os.path.normpath(
    os.path.expanduser('~/.retriever/raw_data/'))
RETRIEVER_SCRIPT_DIR = os.path.normpath(
    os.path.expanduser('~/.retriever/scripts/'))
WEAVER_HOME_DIR = os.path.normpath(os.path.expanduser('~/.weaver/'))
WEAVER_SCRIPT_DIR = os.path.normpath(os.path.expanduser('~/.weaver/scripts/'))

# Set postgres password, Appveyor service needs the password given
# The Travis service obtains the password from the config file.
os_password = ""
pgdbs = "localhost"
docker_or_travis = os.environ.get("IN_DOCKER")

# Check if the environment variable "IN_DOCKER" is set to "true"
if docker_or_travis == "true":
    os_password = 'Password12!'
    pgdbs = "pgdbs"

table_one = {
    'name': 'table-one',
    'raw_data': ['a,b,c',
                 '1,3,5',
                 '2,4,6'],
    'script': {"name": "table-one",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
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
                            }
                        ]
                    },
                    "url": "http://example.com/table_one.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0"
               }
}

table_two = {
    'name': 'table-two',
    'raw_data': ['a,d,e',
                 '1,r,UV',
                 '2,s,WX',
                 '3,t,YZ'],
    'script': {"name": "table-two",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
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
                            }
                        ]
                    },
                    "url": "http://example.com/table_two.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0"
               }
}

table_three = {
    'name': 'table-three',
    'raw_data': ['a,b,e',
                 '1,2,UV',
                 '1,3,WX',
                 '1,0,YZ',
                 '2,4,OP',
                 '2,5,QR'],
    'script': {"name": "table-three",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
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
                            }
                        ]
                    },
                    "url": "http://example.com/table_three.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0"
               }
}

table_four = {
    'name': 'table-four',
    'raw_data': ['a,f,g',
                 '4,1,4',
                 '2,2,5',
                 '1,3,6'],
    'script': {"name": "table-four",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
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
                            }
                        ]
                    },
                    "url": "http://example.com/table_four.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0"
               }
}

table_five = {
    'name': 'table-five',
    'raw_data': ['id,a,b,f',
                 '1,1,3,PL',
                 '2,2,4,PT',
                 '3,2,4,PX'],
    'script': {"name": "table-five",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
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
                            }
                        ]
                    },
                    "url": "http://example.com/table_five.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0"
               },
}

# Retriever script and data
RETRIEVER_TESTS_DATA = [table_one,
                        table_two,
                        table_three,
                        table_four,
                        table_five
                        ]

# Weaver defaults
# Engines
postgres_engine, sqlite_engine = engine_list
WEAVER_TEST_DATA_PACKAEGES_DIR = os.path.normpath(
    os.path.join(FILE_LOCATION, "test_data_packages"))

# Weaver test data(Tuple)
# (Script file name with no extensio, script name, result table, expected)

WEAVER_TEST_DATA_PACKAGE_FILES2 = [
    # TODO: un-comment and ensure test passes
    # ('multi_columns_multi_tables',
    #  'tables-a-c-e-columns-a-b',
    #  'tables-a-c-e-columns-a-b.a_b_e.csv',
    #  {'a': [1, 2, 2],
    #   'b': [3, 4, 4],
    #   'c': [5, 6, 6],
    #   'e': ['WX', 'OP', 'OP'],
    #   'id': [1, 2, 3],
    #   'f': ['PL', 'PT', 'PX']
    #   }),
    ('one_column_multi_tables',
     'tables-a-b-d-columns-a',
     'tables-a-b-d-columns-a.a_b_d.csv',
     {'a': [1, 2],
      'b': [3, 4],
      'c': [5, 6],
      'e': ['UV', 'WX'],
      'd': ['r', 's'],
      'g': [6, 5],
      'f': [3, 2],

      }),
    ('simple_join_one_column_custom',
     'tables-a-b-columns-a-custom',
     'tables-a-b-columns-a-custom.a_b_custom.csv',
     {'a': [1, 2],
      'b': [3, 4],
      'c': [5, 6],
      'e': ['UV', 'WX']
      }),
    ('simple_join_two_column',
     'tables-a-c-columns-a-b',
     'tables-a-c-columns-a-b.a_b.csv',
     {'a': [1, 2],
      'b': [3, 4],
      'c': [5, 6],
      'e': ['WX', 'OP']
      }),
    ('simple_join_one_column',
     'tables-a-b-columns-a',
     'tables-a-b-columns-a.a_b.csv',
     {'a': [1, 2],
      'b': [3, 4],
      'c': [5, 6],
      'e': ['UV', 'WX'],
      'd': ['r', 's']
      })
]

# File names without `.json` extension
WEAVER_TEST_DATA_PACKAGE_FILES = [file_base_names[0]
                                  for file_base_names in WEAVER_TEST_DATA_PACKAGE_FILES2]


def set_retriever_resources(resource_up=True):
    """Create or tear down retriever data and scripts

    if resource_up =True, set up retriever else tear down
    Data directory uses "-", data file names uses "_"
    script file names uses "_"
    """
    for file_names in RETRIEVER_TESTS_DATA:
        data_dir_path = (os.path.join(RETRIEVER_DATA_DIR, file_names['name']))
        data_dir_path = os.path.normpath(data_dir_path)
        data_file_name = file_names['name'].replace("-", "_") + '.txt'
        data_file_path = os.path.normpath(os.path.join(data_dir_path, data_file_name))
        script_name = file_names['script']["name"] + '.json'
        script_file_path = os.path.normpath(os.path.join(RETRIEVER_SCRIPT_DIR, script_name.replace("-", "_")))

        # Set or tear down raw data files
        # in '~/.retriever/raw_data/data_dir_path/data_file_name'
        if resource_up:
            if not os.path.exists(data_dir_path):
                os.makedirs(data_dir_path)
                create_file(file_names['raw_data'], data_file_path)
            if not os.path.exists(RETRIEVER_SCRIPT_DIR):
                os.makedirs(RETRIEVER_SCRIPT_DIR)
            with open(script_file_path, 'w') as js:
                json.dump(file_names['script'], js, indent=2)
            retriever_reload_scripts()
        else:
            shutil.rmtree(data_dir_path)
            os.remove(script_file_path)


def file_exists(path):
    """Return true if a file exists and its size is greater than 0."""
    return os.path.isfile(path) and os.path.getsize(path) > 0


# WEAVER

def set_weaver_data_packages(resources_up=True):
    """Setup or tear down weaver test scripts

    Copy or delete weaver test scripts from test_data directory,
    WEAVER_TEST_DATA_PACKAEGES_DIR
    to ~/.weaver script directory WEAVER_SCRIPT_DIR
    """
    if resources_up:
        if not WEAVER_SCRIPT_DIR:
            os.makedirs(WEAVER_SCRIPT_DIR)
    for file_name in WEAVER_TEST_DATA_PACKAGE_FILES:
        if resources_up:
            scr_pack_path = os.path.join(WEAVER_TEST_DATA_PACKAEGES_DIR, file_name + ".json")
            pack_path = os.path.normpath(scr_pack_path)
            shutil.copy(pack_path, WEAVER_SCRIPT_DIR)
            weaver_reload_scripts()
        else:
            dest_pack_path = os.path.join(WEAVER_SCRIPT_DIR, file_name + ".json")
            dest_path = os.path.normpath(dest_pack_path)
            if os.path.exists(dest_path):
                os.remove(dest_path)


# weaver_reload_scripts()
def install_to_database(dataset, install_function, config):
    # install_function(dataset.replace('_', '-'), **config)
    install_function(dataset, **config)
    return


def install_sqlite_regression(dataset):
    """Install test dataset into sqlite."""
    dbfile = os.path.normpath(os.path.join(os.getcwd(), 'testdb.sqlite'))
    sqlite_engine.opts = {
        'engine': 'sqlite',
        'file': dbfile,
        'table_name': '{db}_{table}'}
    interface_opts = {'file': dbfile}
    install_to_database(dataset, install_sqlite, interface_opts)


def setup_sqlite_retriever_db():
    teardown_sqlite_db()
    for test_data in RETRIEVER_TESTS_DATA:
        install_sqlite_regression(test_data["script"]["name"])


def teardown_sqlite_db():
    dbfile = os.path.normpath(os.path.join(os.getcwd(), 'testdb.sqlite'))
    subprocess.call(['rm', '-r', dbfile])


def install_dataset_postgres(dataset):
    """Install test dataset into postgres ."""
    # cmd = 'psql -U postgres -d testdb -h localhost -c ' \
    #       '"DROP SCHEMA IF EXISTS testschema CASCADE"'
    # subprocess.call(shlex.split(cmd))
    postgres_engine.opts = {'engine': 'postgres',
                            'user': 'postgres',
                            'password': os_password,
                            'host': pgdbs,
                            'port': 5432,
                            'database': 'testdb',
                            'database_name': 'testschema',
                            'table_name': '{db}.{table}'}
    interface_opts = {"user": 'postgres',
                      "password": postgres_engine.opts['password'],
                      "host": postgres_engine.opts['host'],
                      "database": postgres_engine.opts['database'],
                      "database_name": postgres_engine.opts['database_name'],
                      "table_name": postgres_engine.opts['table_name']}
    install_to_database(dataset, install_postgres, interface_opts)


def setup_postgres_retriever_db():
    teardown_postgres_db()
    for test_data in RETRIEVER_TESTS_DATA:
        print(test_data["script"]["name"])
        install_dataset_postgres(test_data["script"]["name"])


def teardown_postgres_db():
    # cmd = 'psql -U postgres -d testdb -h ' + pgdbs + ' -w -c \"DROP SCHEMA IF EXISTS testschema CASCADE\"'
    # subprocess.call(shlex.split(cmd))
    pass


def setup_module():
    # Clean up any old files
    teardown_sqlite_db()

    # Set up test data and scripts
    set_retriever_resources(resource_up=True)
    set_weaver_data_packages(resources_up=True)

    # set up postgres database
    setup_postgres_retriever_db()
    setup_sqlite_retriever_db()


# Test Retriever resources
def test_retriever_test_resources():
    """Test retriever resource files"""
    scrpts_and_raw_data = True
    # ToDOs: Change tests the db_md5 and make it Global
    tests_scripts = [
        "table-one",
        "table-two",
        "table-three",
        "table-four",
        "table-five"]

    for items in tests_scripts:
        retriever_raw_data_path = os.path.normpath(
            os.path.join(RETRIEVER_HOME_DIR, 'raw_data', items, items .replace("-", "_")+ '.txt'))
        if not file_exists(retriever_raw_data_path):
            scrpts_and_raw_data = False
        retriever_script_path = os.path.normpath(
            os.path.join(RETRIEVER_HOME_DIR, 'scripts', items.replace("-", "_") + '.json'))
        if not file_exists(retriever_script_path):
            scrpts_and_raw_data = False
    assert scrpts_and_raw_data is True


def test_restiever_test_scripts():
    """Test retriever test scripts"""
    TESTS_SCRIPTS = [
        "table-one",
        "table-two",
        "table-three",
        "table-four",
        "table-five"]
    assert set(TESTS_SCRIPTS).issubset(set(dataset_names()))


def test_weaver_test_data_packages():
    """Test available weaver test scripts"""
    data_packages_exists = True
    for weaver_script in WEAVER_TEST_DATA_PACKAGE_FILES:
        file_paths = os.path.join(WEAVER_SCRIPT_DIR, weaver_script + '.json')
        if not file_exists(os.path.normpath(file_paths)):
            data_packages_exists = False
    assert data_packages_exists is True


    # Weaver integration


test_parameters = [(test[1], test[2], test[3])
                   for test in WEAVER_TEST_DATA_PACKAGE_FILES2]


def get_script_module(script_name):
    """Load a script module."""
    print(os.path.join(WEAVER_HOME_DIR, "scripts", script_name))
    return read_json(os.path.join(WEAVER_HOME_DIR, "scripts", script_name))


def get_output_as_csv(f, dataset, engines, tmpdir, db):
    """integrate datasets and return the output as a csv."""
    import weaver
    weaver_reload_scripts()
    eng = weaver.join_postgres(dataset, database='testdb', host=pgdbs, password=os_password)
    csv_file = eng.to_csv()
    return csv_file


@pytest.mark.parametrize(
    "f, dataset, csv_file, expected",
    WEAVER_TEST_DATA_PACKAGE_FILES2)
def test_postgres(f, dataset, csv_file, expected):
    tmpdir = None
    postgres_engine.opts = {'engine': 'postgres',
                            'user': 'postgres',
                            'password': os_password,
                            'host': pgdbs,
                            'port': 5432,
                            'database': 'testdb',
                            'database_name': 'testschema',
                            'table_name': '{db}.{table}'}
    interface_opts = {"user": 'postgres',
                      "password": postgres_engine.opts['password'],
                      "host": postgres_engine.opts['host'],
                      "database": postgres_engine.opts['database'],
                      "database_name": postgres_engine.opts['database_name'],
                      "table_name": postgres_engine.opts['table_name']}
    res_csv = get_output_as_csv(
        f,
        dataset,
        postgres_engine,
        tmpdir,
        db=postgres_engine.opts['database_name'])

    # df = pandas.DataFrame.from_items(expected)
    df = pandas.DataFrame.from_dict(OrderedDict(expected))

    data = pandas.read_csv(res_csv)
    os.remove(res_csv)

    assert sorted(list(data.columns)) == sorted(list(df.columns))
    data = data[sorted(sorted(list(data.columns)))]
    df = df[sorted(sorted(list(df.columns)))]

    assert df.equals(data)
