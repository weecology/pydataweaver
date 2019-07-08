from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
import csv
import io
import os
import sys
from os.path import join, exists

from pydataweaver.lib.defaults import SCRIPT_SEARCH_PATHS, ENCODING, SCRIPT_WRITE_PATH
from pydataweaver.lib.load_json import read_json

global_script_list = None


def reload_scripts():
    """Load scripts from scripts directory and return list of modules."""
    modules = []
    loaded_files = []
    loaded_scripts = []
    if not os.path.isdir(SCRIPT_WRITE_PATH):
        os.makedirs(SCRIPT_WRITE_PATH)

    for search_path in [
        search_path for search_path in SCRIPT_SEARCH_PATHS if exists(search_path)
    ]:
        data_packages = [
            file_i for file_i in os.listdir(search_path) if file_i.endswith(".json")
        ]

        for script in data_packages:
            script_name = ".".join(script.split(".")[:-1])
            if script_name not in loaded_files:
                read_script = read_json(join(search_path, script_name))

                if read_script and read_script.name.lower() not in loaded_scripts:
                    setattr(read_script, "_file", os.path.join(search_path, script))
                    setattr(read_script, "_name", script_name)
                    modules.append(read_script)
                    loaded_files.append(script_name)
                    loaded_scripts.append(read_script.name.lower())

    if global_script_list:
        global_script_list.set_scripts(modules)
    return modules


def SCRIPT_LIST():
    """Return Loaded scripts.

    Ensure that only one instance of SCRIPTS is created."""
    if global_script_list:
        return global_script_list.get_scripts()
    return reload_scripts()


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
        if os.name == "nt":
            file_obj = io.open(file_name, "r", newline="", encoding=encoding)
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
            file_obj = io.open(file_name, "w", newline="", encoding=encoding)
        else:
            file_obj = io.open(file_name, "w", newline="")
    else:
        file_obj = io.open(file_name, "wb")
    return file_obj


def open_csvw(csv_file, encode=True):
    """Open a csv writer forcing the use of Linux line endings on Windows.

    Also sets dialect to 'excel' and escape characters to '\\'
    """
    if os.name == "nt":
        csv_writer = csv.writer(
            csv_file, dialect="excel", escapechar="\\", lineterminator="\n"
        )
    else:
        csv_writer = csv.writer(csv_file, dialect="excel", escapechar="\\")
    return csv_writer


def to_str(object, object_encoding=sys.stdout):
    """Convert a Python3 object to a string as in Python2.

    Strings in Python3 are bytes.
    """
    if sys.version_info >= (3, 0, 0):
        enc = object_encoding.encoding
        return str(object).encode(enc, errors="backslashreplace").decode("latin-1")
    return object


class StoredScripts:
    def __init__(self):
        self._shared_scripts = SCRIPT_LIST()

    def get_scripts(self):
        return self._shared_scripts

    def set_scripts(self, script_list):
        self._shared_scripts = script_list


global_script_list = StoredScripts()
