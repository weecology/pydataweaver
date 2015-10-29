import os
import platform
from weaver.lib.models import Engine
from weaver import DATA_DIR

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

    def create_db(self):
        """Override create_db since there is no database just a CSV file"""
        return None

    def create_table(self):
        """Create the table by creating an empty csv file"""
        self.output_file = open(self.table_name(), "w")
        self.output_file.write(','.join(['"%s"' % c[0] for c in self.table.columns]))

    def disconnect(self):
        """Close the last file in the dataset"""
        try:
            self.output_file.close()
        except:
            #when disconnect is called by app.connect_wizard.ConfirmPage to
            #confirm the connection, output_file doesn't exist yet, this is
            #fine so just pass
            pass


