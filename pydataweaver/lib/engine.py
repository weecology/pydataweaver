from __future__ import division
from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
from builtins import object
from builtins import range
from builtins import input
from builtins import next
from builtins import str
import sys
import os
import getpass
import csv
import re
import time
from urllib.request import urlretrieve
from pydataweaver.lib.tools import open_fr, open_fw, open_csvw
from pydataweaver.lib.warning import Warning


class Engine(object):
    """A generic database system. Specific database platforms will inherit
    from this class."""

    name = ""
    instructions = "Enter your database connection information:"
    db = None
    table = None
    _connection = None
    _cursor = None
    datatypes = []
    required_opts = []
    pkformat = "%s PRIMARY KEY %s "
    script = None
    use_cache = True
    debug = False
    warnings = []

    def connect(self, force_reconnect=False):
        if force_reconnect:
            self.disconnect()

        if self._connection is None:
            self._connection = self.get_connection()

        return self._connection

    connection = property(connect)

    def disconnect(self):
        if self._connection:
            self.connection.close()
            self._connection = None
            self._cursor = None

    def get_connection(self):
        """This method should be overloaded by specific implementations
        of Engine."""
        pass

    def create_db(self):
        """Create a new database based on settings supplied in Database object
        engine.db."""
        db_name = self.database_name()
        if db_name:
            print("Creating database " + db_name + "...\n")
            # Create the database
            create_stmt = self.create_db_statement()
            if self.debug:
                print(create_stmt)
            try:
                self.execute(create_stmt)
            except Exception as e:
                try:
                    self.connection.rollback()
                except:
                    pass
                print(
                    "Couldn't create database (%s). "
                    "\nTrying to continue the integration..." % e
                )

    def create_db_statement(self):
        """Return SQL statement to create a database."""
        create_stmt = "CREATE DATABASE " + self.database_name()
        return create_stmt

    def database_name(self, name=None):
        """Return name of the database."""
        if not name:
            try:
                name = self.script.name
            except AttributeError:
                name = "{db}"
        try:
            db_name = self.opts["database_name"].format(db=name)
        except KeyError:
            db_name = name
        return db_name.replace("-", "_")

    def drop_statement(self, objecttype, objectname):
        """Return drop table or database SQL statement."""
        dropstatement = "DROP %s IF EXISTS %s" % (objecttype, objectname)
        return dropstatement

    def execute(self, statement, commit=True):
        """Execute given statement."""
        self.cursor.execute(statement)
        if commit:
            self.connection.commit()

    def executemany(self, statement, values, commit=True):
        """Execute given statement with multiple values."""
        self.cursor.executemany(statement, values)
        if commit:
            self.connection.commit()

    def exists(self, script):
        """Check to see if the given table exists."""
        return all(
            [
                self.table_exists(script.name, key)
                for key in list(script.urls.keys())
                if key
            ]
        )

    def exists(self, database, table_name):
        """Check to see if the given table exists."""
        return self.table_exists(database, table_name)

    def final_cleanup(self):
        """Close the database connection."""
        if self.warnings:
            print("\n".join(str(w) for w in self.warnings))

        self.disconnect()

    def get_cursor(self):
        """Get db cursor."""
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    cursor = property(get_cursor)

    def get_input(self):
        """Manually get user input for connection information when script is
        run from terminal."""
        for opt in self.required_opts:
            if not (opt[0] in list(self.opts.keys())):
                if opt[0] == "password":
                    print(opt[1])
                    self.opts[opt[0]] = getpass.getpass(" ")
                else:
                    prompt = opt[1]
                    if opt[2]:
                        prompt += " or press Enter for the default, %s" % opt[2]
                    prompt += ": "
                    self.opts[opt[0]] = input(prompt)
            if self.opts[opt[0]] in ["", "default"]:
                self.opts[opt[0]] = opt[2]

    def set_engine_encoding(self):
        pass

    def set_table_delimiter(self, file_path):
        dataset_file = open_fr(file_path)
        self.auto_get_delimiter(dataset_file.readline())
        dataset_file.close()

    def table_exists(self, dbname, tablename):
        """This can be overridden to return True if a table exists. It
        returns False by default."""
        return False

    def table_name(self, name=None, dbname=None):
        """Return full tablename."""
        if not name:
            name = self.table.name
        if not dbname:
            dbname = self.database_name()
            if not dbname:
                dbname = ""
        return self.opts["table_name"].format(db=dbname, table=name)

    def to_csv(self, sort=True, path=os.getcwd(), table_name=None):
        if not table_name:
            # use the script result-name
            if self.script.db_table_name:
                table_name = self.script.db_table_name
                print("no table specified")
            # return
        csv_file_output = os.path.normpath(os.path.join(path, table_name + ".csv"))
        csv_file = open_fw(csv_file_output)
        csv_writer = open_csvw(csv_file)
        self.get_cursor()
        self.set_engine_encoding()
        self.cursor.execute("SELECT * FROM  {};".format(table_name))
        row = self.cursor.fetchone()
        column_names = [u"{}".format(tuple_i[0]) for tuple_i in self.cursor.description]
        csv_writer.writerow(column_names)
        while row is not None:
            csv_writer.writerow(row)
            row = self.cursor.fetchone()
        csv_file.close()
        # TODO: later for regression tests
        # if sort:
        #     sort_csv(csv_file_output)
        self.disconnect()
        return csv_file_output

    def warning(self, warning):
        new_warning = Warning("%s:%s" % (self.script.name, self.table.name), warning)
        self.warnings.append(new_warning)

    def gis_import(self, table):
        self.table = table
        return table


def skip_rows(rows, source):
    """Skip over the header lines by reading them before processing."""
    lines = gen_from_source(source)
    for i in range(rows):
        next(lines)
    return lines


def file_exists(path):
    """Return true if a file exists and its size is greater than 0."""
    return os.path.isfile(path) and os.path.getsize(path) > 0


def filename_from_url(url):
    """Extract and returns the filename from the url."""
    return url.split("/")[-1].split("?")[0]


def gen_from_source(source):
    """Return generator from a source tuple.

    Source tuples are of the form (callable, args) where callable(\*args)
    returns either a generator or another source tuple.
    This allows indefinite regeneration of data sources.
    """
    while isinstance(source, tuple):
        gen, args = source
        source = gen(*args)
    return source


def reporthook(count, block_size, total_size):
    """Generate the progress bar.

    Uses file size to calculate the percentage of file size downloaded.
    If the total_size of the file being downloaded is not in the header,
    provide progress as size of bytes downloaded in either KB, MB and GB.
    """
    progress_size = int(count * block_size)
    if total_size != -1:
        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        if duration != 0:
            speed = int(progress_size / (1024 * duration))
            percent = min(int(count * block_size * 100 / total_size), 100)
            sys.stdout.write("\r%2d%%  %d seconds " % (percent, duration))
            sys.stdout.flush()
    else:
        if 1000 >= progress_size / 1000:
            sys.stdout.write("\r%d  KB" % (progress_size / 1000))
            sys.stdout.flush()
        elif 1000000 >= progress_size / 1000000:
            sys.stdout.write("\r%d  MB" % (progress_size / 1000000))
            sys.stdout.flush()
        elif 1000000000 >= progress_size / 1000000000:
            sys.stdout.write("\r%d  GB" % (progress_size / 1000000000))
            sys.stdout.flush()
