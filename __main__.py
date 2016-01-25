# Welcome to the WEAVER. This module......
#
#
# Copyright (C) 2015 the Data Weaver contributors and the University of Florida
#
# This module is part of weaver and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import os
import sys
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from sqlalchemy.orm import mapper, create_session
from weaver.lib.get_opts import parser


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
    if len(sys.argv) == 1 :
        print "arguments required, use weaver -h for help"
        sys.exit(1)
   
    else:
        args = parser.parse_args()

        if args.quiet:
            sys.stdout = open(os.devnull, 'w')

        if args.command == 'help':
            parser.parse_args(['-h'])
            return
        if args.command == "weaver-gui":
            # launch GUI
            from weaver.app.main import launch_app
            launch_app()
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
            # read config file.
            # if engines are present
            #
            # check if config and check the engines in the config file
            # query = read_config()
            # query = use_on_clause()

            from weaver.lib.tools import choose_engine
            engine = choose_engine(args.__dict__)

            # give the main Engine or its children a connection and session value
            engine_sqlarchemy = engine.db_connect()  # this returns create_engine of sqlarchemy

            # use the engine to create the sql statement from the config file.

            cconnection = engine_sqlarchemy.connect()

            query = engine.create_query(args.__dict__["config"])

            # todos check if query fields contain keywords
            result = cconnection.execute(query)
            print query
            for row in result:

                print row

            cconnection.close()




            pass


if __name__ == "__main__":
    main()