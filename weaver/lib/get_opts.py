import argparse

from weaver.engines import engine_list
from weaver.lib.defaults import VERSION

# Create the parser
parser = argparse.ArgumentParser(prog="weaver")

# Add first level arguments
parser.add_argument("-v", "--version", action="version", version=VERSION)
parser.add_argument(
    "-q", "--quiet", help="suppress command-line output", action="store_true"
)

# ..............................................................
# subparsers
# ..............................................................

subparsers = parser.add_subparsers(help="sub-command help", dest="command")
help_parser = subparsers.add_parser("help", help="")

ls_parser = subparsers.add_parser("ls", help="display a list all available datasets")
citation_parser = subparsers.add_parser("citation", help="view citation")
license_parser = subparsers.add_parser("license", help="view dataset licenses")
join_parser = subparsers.add_parser(
    "join", help="integrate data using a data package script"
)
update_parser = subparsers.add_parser(
    "update", help="download updated versions of data package scripts"
)
reset_parser = subparsers.add_parser("reset", help="reset weaver: deletes scripts")

#  ..............................................................
# subparsers with Arguments
# ...............................................................

citation_parser.add_argument(
    "dataset", help="weaver citation or dataset citation", nargs="?", default=None
)
license_parser.add_argument(
    "dataset", help="weaver license or dataset licenses", nargs="?", default=None
)

ls_parser.add_argument(
    "-l", help="search datasets with specific license(s)", nargs="*", default=False
)
ls_parser.add_argument(
    "-k", help="search datasets with keyword(s)", nargs="*", default=False
)
ls_parser.add_argument(
    "-v", help="verbose list of all datasets", nargs="*", default=False
)
join_parser.add_argument("--debug", help="run in debug mode", action="store_true")
join_subparsers = join_parser.add_subparsers(help="engine-specific help", dest="engine")
reset_parser.add_argument("scope", help="things to reset: scripts", choices=["scripts"])

for engine in engine_list:
    join_engine_parser = join_subparsers.add_parser(
        engine.abbreviation, help=engine.name
    )
    join_engine_parser.add_argument("dataset", help="file name")

    abbreviations = set("h")
    for arg in engine.required_opts:
        arg_name, help_msg, default = arg[:3]
        potential_abbreviations = [
            char for char in arg_name if not char in abbreviations
        ]
        if potential_abbreviations:
            abbreviation = potential_abbreviations[0]
            abbreviations.add(abbreviation)
        else:
            abbreviation = "-%s" % arg_name
        join_engine_parser.add_argument(
            "--%s" % arg_name,
            "-%s" % abbreviation,
            help=help_msg,
            nargs="?",
            default=default,
        )
