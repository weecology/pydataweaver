#!/bin/sh
set -e

# Copy config files to $HOME
cp -r /pydataweaver/cli_tools/.pgpass  ~/
cp -r /pydataweaver/cli_tools/.my.cnf  ~/

exec "$@"
