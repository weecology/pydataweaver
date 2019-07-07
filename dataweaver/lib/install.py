from __future__ import absolute_import
from __future__ import print_function

import os

from dataweaver.engines import choose_engine
from dataweaver.lib.defaults import DATA_DIR, SCRIPT_WRITE_PATH
from dataweaver.lib.engine_tools import name_matches
from dataweaver.lib.repository import check_for_updates
from dataweaver.lib.scripts import SCRIPT_LIST


def _join(args, use_cache, debug, compile):
    """Install scripts for dataweaver."""
    engine = choose_engine(args)
    engine.use_cache = use_cache

    script_list = SCRIPT_LIST()
    if not (script_list or os.listdir(SCRIPT_WRITE_PATH)):
        check_for_updates()
        script_list = SCRIPT_LIST()
    scripts = name_matches(script_list, args["dataset"])
    if scripts:
        for dataset_script in scripts:
            try:
                dataset_script.integrate(engine, debug=debug)
                dataset_script.engine.final_cleanup()
            except Exception as e:
                print(e)
                if debug:
                    raise
    else:
        message = (
            'The dataset "{}" isn\'t available in the dataweaver. '
            "Run dataweaver.datasets()to list the currently available "
            "datasets".format(args["dataset"])
        )
        raise ValueError(message)
    return engine


def join_postgres(
    dataset,
    user="postgres",
    password="",
    host="localhost",
    port=5432,
    database="postgres",
    database_name=None,
    table_name=None,
    compile=False,
    debug=False,
    quiet=False,
    use_cache=True,
):
    """Install scripts in postgres."""
    if not table_name:
        table_name = "{db}.{table}"
    if not database_name:
        database_name = "{db}"

    args = {
        "command": "install",
        "database": database,
        "database_name": database_name,
        "engine": "postgres",
        "dataset": dataset,
        "debug": debug,
        "host": host,
        "port": port,
        "password": password,
        "quiet": quiet,
        "table_name": table_name,
        "user": user,
        "use_cache": use_cache,
    }

    return _join(args, use_cache, debug, compile)


def join_sqlite(
    dataset,
    file=None,
    table_name=None,
    compile=False,
    debug=False,
    quiet=False,
    use_cache=True,
):
    """Install scripts in sqlite."""
    if not table_name:
        table_name = "{db}_table"
    if not file:
        file = os.path.join(DATA_DIR, "sqlite.db")

    args = {
        "command": "install",
        "dataset": dataset,
        "engine": "sqlite",
        "file": file,
        "quiet": quiet,
        "table_name": table_name,
        "use_cache": use_cache,
    }

    return _join(args, use_cache, debug, compile)
