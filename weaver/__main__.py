import os
import sys
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from sqlalchemy.orm import mapper, create_session
from weaver.lib.get_opts import parser
import imp


# sys removes the setdefaultencoding method at startup; reload to get it back

imp.reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    # set default encoding to latin-1 to avoid ascii encoding issues
    sys.setdefaultencoding('latin-1')


def main():
    """
    main function the weaver module
    """
    if len(sys.argv) == 1:
        # if no command line args are passed, show the help options
        parser.parse_args(['-h'])
    else:
        args = parser.parse_args()

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
            print((args.command + " data set to trim "+args.source_file+" result data set "+args.dest_file ))
            print("attributes:")
            print(args.attr)
            return

        # basing on the database system used (engine)
        # delete comment : We assume that a person either uses mysql or postgres

        if args.command == 'dbjoin':

            from weaver.lib.tools import choose_engine
            engine = choose_engine(args.__dict__)

            # give the main Engine or its children a connection and session value
            engine_sqlarchemy = engine.db_connect()  # this returns create_engine of sqlarchemy

            # use the engine to create the sql statement from the config file.

            cconnection = engine_sqlarchemy.connect()

            query = engine.create_query(args.__dict__["config"])

            # todos check if query fields contain keywords
            result = cconnection.execute(query)

            print(query)
            for row in result:

                print(row)

            cconnection.close()




            pass


if __name__ == "__main__":
    main()