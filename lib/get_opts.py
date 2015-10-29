import argparse

from weaver.engines import engine_list, engines_no_password
from weaver import VERSION


# Create the parser
parser = argparse.ArgumentParser()

# Add first level arguments
parser.add_argument('-v', '--version', action='version', version=VERSION)
parser.add_argument('-q', '--quiet', help='suppress command-line output', action='store_true')

subparsers = parser.add_subparsers(help='sub-command help', dest='command')

# ..............................................................
# subparsers
# ..............................................................

trim_parser = subparsers.add_parser('trim', help='select given attributes from a single file')
help_parser = subparsers.add_parser('help', help='')
gui_parser = subparsers.add_parser('gui', help='launch retriever in graphical mode')
ls_parser = subparsers.add_parser('ls', help='display a list all available datasets')
citation_parser = subparsers.add_parser('citation', help='view citation')
join_parser = subparsers.add_parser('dbjoin', help='integrate datasets using the configuration file')
file_join_parser = subparsers.add_parser('filejoin', help='integrate datasets using the configuration file')

#  ..............................................................
# subparsers with Arguments
# ...............................................................

citation_parser.add_argument('dataset', help='null for weaver citation or filename for dataset citatiom', nargs='?',
                             default=None)
trim_parser.add_argument('source_file', help='source data set name', default=None)
trim_parser.add_argument('dest_file', help='destination file name', default=None)
trim_parser.add_argument('attr', help='data set name', nargs='?', default=None)
file_join_parser.add_argument('config', help='join configuration file', nargs='?', default=None)

join_subparsers = join_parser.add_subparsers(help='engine-specific help', dest='engine')
join_engine_parser = {}

for engine in engine_list:
    if engine.name.lower() in engines_no_password:
        pass
    else:
        join_engine_parser = join_subparsers.add_parser(engine.abbreviation, help=engine.name)
        abbreviations = set('h')
        for arg in engine.required_opts:
            arg_name, help_msg, default = arg[:3]
            potential_abbreviations = [char for char in arg_name if not char in abbreviations]
            if potential_abbreviations:
                abbreviation = potential_abbreviations[0]
                abbreviations.add(abbreviation)
            else:
                abbreviation = '-%s' % arg_name

            if engine.name.lower() not in engines_no_password:
                join_engine_parser.add_argument('--%s' % arg_name, '-%s' % abbreviation, help=help_msg, nargs='?',
                                                default=default)
    join_engine_parser.add_argument('config', help='configuration file', nargs='?', default=None)
help_parser = subparsers.add_parser('help', help='')