import os

from sqlalchemy import *

from weaver import DATA_DIR
from weaver.lib.models import Engine


class engine(Engine):
    """Engine class for SQLite."""
    name = "SQLite"
    abbreviation = "sqlite"
    sqlite_path = ""
    datatypes = {
                 "auto": "INTEGER",
                 "int": "INTEGER",
                 "bigint": "INTEGER",
                 "double": "REAL",
                 "decimal": "REAL",
                 "char": "TEXT",
                 "bool": "INTEGER",
                 }
    required_opts = [("file",
                      "Enter the filename of your SQLite database",
                      os.path.join(DATA_DIR, "sqlite.db"),
                      ""),
                     ("table_name",
                      "Format of table name",
                      "{db}_{table}"),
                     ]

    def url_string(self):

        if self.sqlite_path =="":
             sqlalchemy_url_string = var = self.name.lower() + '://'
        else:
            sqlalchemy_url_string = self.name.lower() + '://' + self.sqlite_path + '.db'
        print (sqlalchemy_url_string)
        return sqlalchemy_url_string

    def db_connect(self):
        """
        Performs database connection using database settings from settings.py.
        Returns sqlalchemy engine instance
        """
        return create_engine(self.url_string())