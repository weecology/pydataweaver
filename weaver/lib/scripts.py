from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
import csv
import imp
import io
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from os.path import join, isfile, getmtime, exists, abspath

from pkg_resources import parse_version

from weaver.lib.defaults import SCRIPT_SEARCH_PATHS, VERSION, ENCODING, SCRIPT_WRITE_PATH
# from weaver.lib.compile import compile_json
from retriever.lib.load_json import read_json



def MODULE_LIST(force_compile=False):
    """Load scripts from scripts directory and return list of modules."""
    modules = []

    return rt.datasets()


def SCRIPT_LIST(force_compile=False):
    import retriever as rt
    # return [module.SCRIPT for module in MODULE_LIST(force_compile)]
    return rt.datasets()


def get_script(dataset):
    """Return the script for a named dataset."""
    scripts = {script.name: script for script in SCRIPT_LIST()}
    if dataset in scripts:
        return scripts[dataset]
    else:
        raise KeyError("No dataset named: {}".format(dataset))


def open_fr(file_name, encoding=ENCODING, encode=True):
    """Open file for reading respecting Python version and OS differences.

    Sets newline to Linux line endings on Windows and Python 3
    When encode=False does not set encoding on nix and Python 3 to keep as bytes
    """
    if sys.version_info >= (3, 0, 0):
        if os.name == 'nt':
            file_obj = io.open(file_name, 'r', newline='', encoding=encoding)
        else:
            if encode:
                file_obj = io.open(file_name, "r", encoding=encoding)
            else:
                file_obj = io.open(file_name, "r")
    else:
        file_obj = io.open(file_name, "r", encoding=encoding)
    return file_obj


def open_fw(file_name, encoding=ENCODING, encode=True):
    """Open file for writing respecting Python version and OS differences.

    Sets newline to Linux line endings on Python 3
    When encode=False does not set encoding on nix and Python 3 to keep as bytes
    """
    if sys.version_info >= (3, 0, 0):
        if encode:
            file_obj = io.open(file_name, 'w', newline='', encoding=encoding)
        else:
            file_obj = io.open(file_name, 'w', newline='')
    else:
        file_obj = io.open(file_name, 'wb')
    return file_obj


def open_csvw(csv_file, encode=True):
    """Open a csv writer forcing the use of Linux line endings on Windows.

    Also sets dialect to 'excel' and escape characters to '\\'

    """
    if os.name == 'nt':
        csv_writer = csv.writer(csv_file, dialect='excel', escapechar='\\', lineterminator='\n')
    else:
        csv_writer = csv.writer(csv_file, dialect='excel', escapechar='\\')
    return csv_writer


def to_str(object, object_encoding=sys.stdout):
    if sys.version_info >= (3, 0, 0):
        enc = object_encoding.encoding
        return str(object).encode(enc, errors='backslashreplace').decode("latin-1")
    else:
        return object
