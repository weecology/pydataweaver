"""Data Weaver Wizard

Main entry for CLI

"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
from builtins import input
from imp import reload

from weaver.engines import engine_list, choose_engine
from weaver.lib.datapackage import create_json, edit_json, delete_json, get_script_filename
from weaver.lib.datasets import datasets, license
from weaver.lib.defaults import sample_script, CITATION, ENCODING
from weaver.lib.get_opts import parser
from weaver.lib.repository import check_for_updates
from weaver.lib.scripts import SCRIPT_LIST
from weaver.lib.engine_tools import name_matches, reset_retriever

from weaver.lib.process import Processor


def main():
    """This function launches the weaver."""
    if len(sys.argv) == 1:
        # if no command line args are passed, show the help options
        parser.parse_args(['-h'])

    else:

        args = parser.parse_args()

        if args.quiet:
            sys.stdout = open(os.devnull, 'w')

        if args.command == 'help':
            parser.parse_args(['-h'])

        # Citations and Ls are going to import from retriever

        if args.command == 'citation':
            if args.dataset is None:
                # get the citation of weaver
                print("ToDos::citation of weaver")
                return
            else:
                print("ToDos::the citation for dataset "+args.dataset )

        # list the data sets available
        if args.command == 'ls':
            print("ToDos:: list of all available data sets.\n "
                  "Either we search the default retriever data folder")
            return

        if args.command == 'join':
            # open the conf file
            print(args.config[0])
            from collections import OrderedDict
            import json
            json_object = OrderedDict()
            json_file = args.config[0]

            try:
                json_object = json.load(open(json_file, "r"))
            except ValueError:
                pass

        # get tables from scripts
        tables_items = json_object["tables"]
        Processor(name="henry", dataobj=json_object)

if __name__ == "__main__":
    main()
