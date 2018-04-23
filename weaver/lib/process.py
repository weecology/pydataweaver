from __future__ import print_function

import shutil

# from weaver.lib.models import *
from weaver.lib.models import myTables
from weaver.engines import choose_engine
from weaver.lib.defaults import DATA_DIR

from retriever import dataset_names
from weaver.lib.templates import TEMPLATES


class Processor(object):
    def __init__(self, name=None, dataobj =None):
        name = name
        config = dataobj
        scripts = []

        scripts_needed = []
        x = myTables

        main_table = config["main_file"]
        result_table = config["result"]
        first_table = myTables[main_table["table_type"]](name=main_table["table_name"], **main_table)
        print (first_table)


        for i in config["tables"]:
            xx = i["table_type"]

            vv = myTables[xx](name=i["table_name"], **i)

            print (i)



        # for i in config["tables"]:
        #     scripts_needed.append(i["dataset"])
        # print (set(scripts_needed))

        set()


