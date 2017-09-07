from builtins import str
from builtins import object

import os
import io
import sys
import csv

from weaver.lib.models import Engine
from weaver import open_fw, open_csvw
from weaver.util.settings import DATA_DIR
# from retriever.lib.tools import sort_csv


class DummyConnection(object):

    def cursor(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class DummyCursor(DummyConnection):
    pass


class engine(Engine):
    """Engine instance for writing data to a CSV file."""
    name = "CSV"
    abbreviation = "csv"
    datatypes = {
        "auto": "INTEGER",
        "int": "INTEGER",
        "bigint": "INTEGER",
        "double": "REAL",
        "decimal": "REAL",
        "char": "TEXT",
        "bool": "INTEGER",
    }
    required_opts = [
        ("table_name",
         "Format of table name",
         os.path.join(DATA_DIR, "{db}_{table}.csv")),
    ]
    table_names = []

    def create_db(self):
        """Override create_db since there is no database just a CSV file"""
        return None

    def create_table(self):
        """Create the table by creating an empty csv file"""
        self.auto_column_number = 1
        self.file = open_fw(self.table_name())
        self.output_file = open_csvw(self.file)
        self.output_file.writerow([u'{}'.format(val) for val in self.table.get_insert_columns(join=False,create=True)])
        self.table_names.append((self.file, self.table_name()))

    def disconnect(self):
        """Close the last file in the dataset"""
        try:
            self.output_file.close()
        except:
            #when disconnect is called by app.connect_wizard.ConfirmPage to
            #confirm the connection, output_file doesn't exist yet, this is
            #fine so just pass
            pass

