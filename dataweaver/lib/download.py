from __future__ import absolute_import
from __future__ import print_function

from dataweaver.engines import choose_engine
from dataweaver.lib.scripts import SCRIPT_LIST
from dataweaver.lib.engine_tools import name_matches

script_list = SCRIPT_LIST()


def download(dataset, path="./", quiet=False, subdir=False, debug=False):
    """Download scripts for dataweaver."""
    args = {
        "dataset": dataset,
        "command": "download",
        "path": path,
        "subdir": subdir,
        "quiet": quiet,
    }
    engine = choose_engine(args)
    scripts = name_matches(script_list, args["dataset"])
    if scripts:
        for dataset in scripts:
            print("=> Download csv Integrated data", dataset.name)
            try:
                dataset.integrate(engine, debug=debug)

                # Todo csv should fetch the file to path
                dataset.engine.to_csv()
                dataset.engine.final_cleanup()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(e)
                if debug:
                    raise
