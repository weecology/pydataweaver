"""Data Weaver Wizard

Main entry for CLI

"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys

from weaver.lib.datasets import datasets,  dataset_names, license
from weaver.lib.defaults import CITATION, SCRIPT_SEARCH_PATHS
from weaver.lib.engine_tools import name_matches
from weaver.lib.get_opts import parser
from weaver.lib.process import Processor
from weaver.lib.repository import check_for_updates
from weaver.lib.scripts import SCRIPT_LIST, get_script


def main():
    """This function launches the weaver."""
    if len(sys.argv) == 1:
        # if no command line args are passed, show the help options
        parser.parse_args(['-h'])
    else:
        if not os.path.isdir(SCRIPT_SEARCH_PATHS[1]) and not \
                [f for f in os.listdir(SCRIPT_SEARCH_PATHS[-1])
                 if os.path.exists(SCRIPT_SEARCH_PATHS[-1])]:
            check_for_updates()
        script_list = SCRIPT_LIST()

        args = parser.parse_args()

        if args.quiet:
            sys.stdout = open(os.devnull, 'w')

        if args.command == 'help':
            parser.parse_args(['-h'])

        if args.command == 'citation':
            if args.dataset is None:
                # get the citation of weaver
                print(CITATION)
                return
            else:
                scripts = name_matches(script_list, args.dataset)
                for dataset in scripts:
                    print("\nDataset:  {}".format(dataset.name))
                    print("Description:   {}".format(dataset.description))
                    print("Citations:")
                    for cite in dataset.citation:
                        for key, value in cite.items():
                            print ("{k}:    {v}".format(k=key, v=value))
        if args.command == 'license':
            dataset_license = license(args.dataset)
            if dataset_license:
                print(dataset_license)
            else:
                print("There is no license information for {}".format(args.dataset))
            return

        # list the data sets available
        if args.command == 'ls':
            # If scripts have never been downloaded there is nothing to list
            if not script_list:
                print("No scripts are currently available. Updating scripts now...")
                check_for_updates(False)
                print("\n\nScripts downloaded.\n")
            if not (args.l or args.k or isinstance(args.v, list)):
                all_scripts = dataset_names()
                print("Available datasets : {}\n".format(len(all_scripts)))
                from weaver import lscolumns
                lscolumns.printls(all_scripts)

            # if weaver ls  -v has a list of scripts, ie item1, item2
            # print the items' information else consider all scripts
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
        if args.command == 'join':
            if args.config is not None:
                scripts = name_matches(script_list, args.config)
            if scripts:
                for dataset in scripts:
                    print("=> Integrating", dataset.name)
                    Processor.make_sql(dataset)

                    # try:
                    #     dataset.download(engine, debug=debug)
                    #     dataset.engine.final_cleanup()
                    # except KeyboardInterrupt:
                    #     pass
                    # except Exception as e:
                    #     print(e)
                    #     if debug:
                    #         raise


def print_info(all_scripts, keywords_license=False):
    count = 1
    for script in all_scripts:
        # include description if keywords_license are not used
        if not keywords_license:
            out_stm = "{count}. {title}\n{name}\n{keywords}\n{description}\n{licenses}\n" \
                      "{citation}\n".format(count=count, title=script.title, name=script.name,
                                 keywords=script.keywords, description=script.description,
                                 licenses=str(script.licenses), citation=script.citation)
        else:
            out_stm = "{count}. {title}\n{name}\n{keywords}\n{licenses}\n" \
                       "".format(count=count, title=script.title, name=script.name,
                                 keywords=script.keywords,
                                 licenses=str(script.licenses))
        print(out_stm)
        count += 1


if __name__ == "__main__":
    main()

