import difflib
import os
import sys
import warnings
import unittest
import shutil


from decimal import Decimal
from hashlib import md5

from weaver import HOME_DIR
from weaver.lib.models import *


config_path = os.path.join(HOME_DIR, 'connections.config')



def get_saved_connection(engine_name):
    """Given the name of an engine, returns the stored connection for that engine
    from connections.config."""
    parameters = {}
    if os.path.isfile(config_path):
        config = open(config_path, "rb")
        for line in config:
            values = line.rstrip('\n').split(',')
            if values[0] == engine_name:
                try:
                    parameters = eval(','.join(values[1:]))
                except:
                    pass
    return parameters


def save_connection(engine_name, values_dict):
    """Saves connection information for an engine in connections.config."""
    lines = []
    if os.path.isfile(config_path):
        config = open(config_path, "rb")
        for line in config:
            if line.split(',')[0] != engine_name:
                lines.append('\n' + line.rstrip('\n'))
        config.close()
        os.remove(config_path)
        config = open(config_path, "wb")
    else:
        config = open(config_path, "wb")
    if "file" in values_dict:
        values_dict["file"] = os.path.abspath(values_dict["file"])
    config.write(engine_name + "," + str(values_dict))
    for line in lines:
        config.write(line)
    config.close()


def get_default_connection():
    """Gets the first (most recently used) stored connection from
    connections.config."""
    if os.path.isfile(config_path):
        config = open(config_path, "rb")
        default_connection = config.readline().split(",")[0]
        config.close()
        return default_connection
    else:
        return None


def choose_engine(opts, choice=True):
    """Prompts the user to select a database engine"""
    from weaver.engines import engine_list

    if "engine" in opts.keys():
        enginename = opts["engine"]
    elif opts["command"] == "download":
        enginename = "download"
    else:
        if not choice: return None
        print "Choose a database engine:"
        for engine in engine_list:
            if engine.abbreviation:
                abbreviation = "(" + engine.abbreviation + ") "
            else:
                abbreviation = ""
            print "    " + abbreviation + engine.name
        enginename = raw_input(": ")
    enginename = enginename.lower()

    engine = Engine()
    if not enginename:
        engine = engine_list[0]
    else:
        for thisengine in engine_list:
            if (enginename == thisengine.name.lower()
                              or thisengine.abbreviation
                              and enginename == thisengine.abbreviation):
                engine = thisengine

    engine.opts = opts
    return engine
print ("Henry classeeeee manager")  