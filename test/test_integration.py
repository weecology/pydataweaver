# -*- coding: latin-1  -*-
# """Integrations tests for Data Weaver"""
from __future__ import print_function

import json
import os
import shlex
import shutil
import subprocess
import sys
from imp import reload

from retriever.lib.defaults import ENCODING

encoding = ENCODING.lower()

reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding(encoding)
import pytest
from weaver.lib.load_json import read_json
from weaver.lib.defaults import HOME_DIR
from weaver.engines import engine_list
from weaver.lib.engine_tools import file_2list
from weaver.lib.engine_tools import create_file

# Set postgres password, Appveyor service needs the password given
# The Travis service obtains the password from the config file.
if os.name == "nt":
    os_password = "Password12!"
else:
    os_password = ""

mysql_engine, postgres_engine, sqlite_engine, msaccess_engine, \
csv_engine, download_engine, json_engine, xml_engine = engine_list

table_one = {
    'name': 'table_one',
    'raw_data': ['a,b,c',
                 '1,2,3',
                 '4,5,6'],
    'script': {"name": "table_one",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_one",
                    "schema": {},
                    "url": "http://example.com/table_one.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_one": "http://example.com/table_one.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}

#t1.c==t2.c
table_two = {
    'name': 'table_two',
    'raw_data': ['d,c,f',
                 '1,5,8',
                 '2,6,9',
                 '3,5,7'],
    'script': {"name": "table_two",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_two",
                    "schema": {},
                    "url": "http://example.com/table_two.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_two": "http://example.com/table_two.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}

# t1.b==t3.e and t1.c==t3.f
table_three = {
    'name': 'table_three',
    'raw_data': ['d,e,f,g',
                 '1,2,4,4',
                 '1,2,3,4',
                 '4,5,6,4',
                 '1,5,6,4'],
    'script': {"name": "table_three",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_three",
                    "schema": {},
                    "url": "http://example.com/table_three.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_three": "http://example.com/table_three.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}

# t1.c==t2.c and t2.f== t4.f(intermediate table)
table_four = {
    'name': 'table_four',
    'raw_data': ['e,f,g',
                 '1,2,3',
                 '4,5,6'],
    'script': {"name": "table_four",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_four",
                    "schema": {},
                    "url": "http://example.com/table_four.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_four": "http://example.com/table_four.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}

table_five = {
    'name': 'table_five',
    'raw_data': ['a,b,c',
                 '1,2,3',
                 '4,5,6'],
    'script': {"name": "table_five",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_five",
                    "schema": {},
                    "url": "http://example.com/table_five.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_five": "http://example.com/table_five.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}

table_six = {
    'name': 'table_six',
    'raw_data': ['a,b,c',
                 '1,2,3',
                 '4,5,6'],
    'script': {"name": "table_six",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_six",
                    "schema": {},
                    "url": "http://example.com/table_six.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_six": "http://example.com/table_six.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}


table_seven = {
    'name': 'table_seven',
    'raw_data': ['a,b,c',
                 '1,2,3',
                 '4,5,6'],
    'script': {"name": "table_seven",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_seven",
                    "schema": {},
                    "url": "http://example.com/table_seven.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_seven": "http://example.com/table_seven.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}

table_eight = {
    'name': 'table_eight',
    'raw_data': ['a,b,c',
                 '1,2,3',
                 '4,5,6'],
    'script': {"name": "table_eight",
               "resources": [
                   {"dialect": {"do_not_bulk_insert": "True"},
                    "name": "table_eight",
                    "schema": {},
                    "url": "http://example.com/table_eight.txt"}
               ],
               "retriever": "True",
               "version": "1.0.0",
               "urls":
                   {"table_eight": "http://example.com/table_eight.txt"}
               },
    'expect_out': ['a,b,c', '1,2,3', '4,5,6']
}
tests = [
    table_one,
    table_two,
    table_three,
    table_four,
    table_five,
    table_six,
    table_seven,
    table_eight
]

# Create a tuple of all test scripts with their expected values
test_parameters = [(test, test['expect_out']) for test in tests]

file_location = os.path.dirname(os.path.realpath(__file__))
weaver_root_dir = os.path.abspath(os.path.join(file_location, os.pardir))
for test in tests:
    if not os.path.exists(os.path.join(HOME_DIR, "raw_data", test['name'])):
        os.makedirs(os.path.join(HOME_DIR, "raw_data", test['name']))
    rd_path = os.path.join(HOME_DIR,
                           "raw_data", test['name'], test['name'] + '.txt')
    create_file(test['raw_data'], rd_path)

    path_js = os.path.join(HOME_DIR, "scripts", test['name'] + '.json')
    with open(path_js, 'w') as js:
        json.dump(test['script'], js, indent=2)
    read_json(os.path.join(HOME_DIR, "scripts", test['name']))