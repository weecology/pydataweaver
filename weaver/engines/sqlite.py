import os

from weaver.lib.defaults import DATA_DIR
from weaver.lib.models import Engine


class engine(Engine):
    """Engine instance for SQLite."""

    name = "SQLite"
    abbreviation = "sqlite"
    datatypes = {
        "auto": ("INTEGER", "AUTOINCREMENT"),
        "int": "INTEGER",
        "bigint": "INTEGER",
        "double": "REAL",
        "decimal": "REAL",
        "char": "TEXT",
        "bool": "INTEGER",
    }
    placeholder = "?"
    required_opts = [("file",
                      "Enter the filename of your SQLite database",
                      os.path.join(DATA_DIR, "sqlite.db"),
                      ""),
                     ("table_name",
                      "Format of table name",
                      "{db}_{table}"),
                     ]

    def create_db(self):
        """Don't create database for SQLite

        SQLite doesn't create databases. Each database is a file and needs a separate
        connection. This overloads`create_db` to do nothing in this case.
        """
        return None

    def to_csv(self):
        Engine.to_csv(self)

    def get_connection(self):
        """Get db connection."""
        import sqlite3 as dbapi
        self.get_input()
        return dbapi.connect(self.opts["file"])
