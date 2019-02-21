#!/bin/sh
set -e

# Copy config files to $HOME
cp -r /weaver/cli_tools/.pgpass  ~/
cp -r /weaver/cli_tools/.my.cnf  ~/

exec "$@"
