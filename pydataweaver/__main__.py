"""Data Weaver Wizard

Main entry for CLI

"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys

from pydataweaver.engines import choose_engine
from pydataweaver.lib.datasets import datasets, dataset_names, license
from pydataweaver.lib.defaults import CITATION, SCRIPT_SEARCH_PATHS
from pydataweaver.lib.engine_tools import name_matches, reset_weaver
from pydataweaver.lib.get_opts import parser
from pydataweaver.lib.repository import check_for_updates
from pydataweaver.lib.scripts import SCRIPT_LIST, reload_scripts, get_script


def main():
    """This function launches the pydataweaver."""
    if len(sys.argv) == 1:
        # If no command line Args are passed, show the help options
        parser.parse_args(["-h"])
    else:
        args = parser.parse_args()

        if (args.command not in ["reset", "update"] and
                not os.path.isdir(SCRIPT_SEARCH_PATHS[1]) and not [
                    f for f in os.listdir(SCRIPT_SEARCH_PATHS[-1])
                    if os.path.exists(SCRIPT_SEARCH_PATHS[-1])
                ]):
            check_for_updates()
            reload_scripts()
        script_list = SCRIPT_LIST()

        if args.command == "join" and not args.engine:
            parser.parse_args(["join", "-h"])

        if args.quiet:
            sys.stdout = open(os.devnull, "w")

        if args.command == "help":
            parser.parse_args(["-h"])

        if args.command == "update":
            check_for_updates()
            reload_scripts()
            return

        if args.command == "reset":
            reset_weaver(args.scope)
            return
        if args.command == "citation":
            if args.dataset is None:
                # get the citation of pydataweaver
                print(CITATION)
                return
            else:
                scripts = name_matches(script_list, args.dataset)
                for data_set in scripts:
                    print("\nDataset:  {}".format(data_set.name))
                    print("Description:   {}".format(data_set.description))
                    print("Citations:")
                    for cite in data_set.citation:
                        for key, value in cite.items():
                            print("{k}:    {v}".format(k=key, v=value))
            return
        if args.command == "license":
            data_set_license = license(args.dataset)
            if data_set_license:
                print(data_set_license)
            else:
                print("There is no license information for {}".format(args.dataset))
            return

        # list the data sets available
        if args.command == "ls":
            if not (args.l or args.k or isinstance(args.v, list)):
                all_scripts = dataset_names()
                print("Available datasets : {}\n".format(len(all_scripts)))
                from pydataweaver import lscolumns

                lscolumns.printls(all_scripts)

            # If pydataweaver ls  -v  has a list of scripts, i.e item1, item2,
            # print the items' information, else consider all scripts"
            elif isinstance(args.v, list):
                if args.v:
                    try:
                        all_scripts = [get_script(dataset) for dataset in args.v]
                    except KeyError:
                        all_scripts = []
                        print("Dataset(s) is not found.")
                else:
                    all_scripts = datasets()
                print_info(all_scripts)

            else:
                param_licenses = args.l if args.l else None
                keywords = args.k if args.k else None

                # search
                searched_scripts = datasets(keywords, param_licenses)
                if not searched_scripts:
                    print("No available datasets found")
                else:
                    print("Available datasets : {}\n".format(len(searched_scripts)))
                    print_info(searched_scripts, keywords_license=True)

            return
        if args.command == "join":
            engine = choose_engine(args.__dict__)

            if hasattr(args, "debug") and args.debug:
                debug = True
            else:
                debug = False
                sys.tracebacklimit = 0

            if args.dataset is not None:
                scripts = name_matches(script_list, args.dataset)
            if scripts:
                for data_set in scripts:
                    print("=> Integrating", data_set.name)
                    try:
                        data_set.integrate(engine, debug=debug)
                        data_set.engine.final_cleanup()
                    except KeyboardInterrupt:
                        pass
                    except Exception as e:
                        print(e)
                        if debug:
                            raise


def print_info(all_scripts, keywords_license=False):
    count = 1
    for script in all_scripts:
        # Include a description if keywords_license are not used
        if not keywords_license:
            out_stm = ("{count}. {title}\n{name}\n{keywords}\n{description}\n{licenses}\n"
                       "{citation}\n".format(
                           count=count,
                           title=script.title,
                           name=script.name,
                           keywords=script.keywords,
                           description=script.description,
                           licenses=str(script.licenses),
                           citation=script.citation,
                       ))
        else:
            out_stm = "{count}. {title}\n{name}\n{keywords}\n{licenses}\n" "".format(
                count=count,
                title=script.title,
                name=script.name,
                keywords=script.keywords,
                licenses=str(script.licenses),
            )
        print(out_stm)
        count += 1


if __name__ == "__main__":
    main()
