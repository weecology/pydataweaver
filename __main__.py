# Welcome to the WEAVER. This module......
#
#
# Copyright (C) 2015 Weecology
#
# This module is part of weaver and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from weaver.engines import engine_list
from weaver.lib.engine import Engine
from weaver import VERSION
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import os
import platform
import sys
import mysql.connector
import psycopg2
from weaver.lib.get_opts import parser
import json
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from sqlalchemy.orm import mapper, create_session
import csv
import time


import os
import platform
import sys

# sys removes the setdefaultencoding method at startup; reload to get it back

reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    # set default encoding to latin-1 to avoid ascii encoding issues
    sys.setdefaultencoding('latin-1')


def main():
    """
    main function the weaver module
    """

    # if no command line args are passed, launch GUI
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == 'gui'):
        # if no command line args are passed, launch GUI
        from weaver.app.main import launch_app
        launch_app()
    else:
        args = parser.parse_args()
        print(args)
        if args.quiet:
            sys.stdout = open(os.devnull, 'w')

        if args.command == 'help':
            parser.parse_args(['-h'])
            return

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

        # process single file to trim attributes
        if args.command == 'trim':
            print("ToDos:: project only the selected attributes")
            print(args.command + " data set to trim "+args.source_file+" result data set "+args.dest_file )
            print("attributes:")
            print (args.attr)
            return

        # basing on the database system used (engine)
        # delete comment : We assume that a person either uses mysql or postgres

        if args.command == 'dbjoin':

            from weaver.lib.tools import choose_engine
            engine = choose_engine(args.__dict__)
            engine_connection=engine.db_connect()
            pass


if __name__ == "__main__":
    main()