#!/bin/sh
set -e

# Copy config files to $HOME
cp -r /dataweaver/cli_tools/.pgpass  ~/
cp -r /dataweaver/cli_tools/.my.cnf  ~/

exec "$@"
