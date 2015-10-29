import json

from sqlalchemy import *

from weaver.lib.models import Engine  # , no_cleanup
from weaver import settings_path


class engine(Engine):
    """Engine instance for MySQL."""
    name = "MySQL"
    abbreviation = "mysql"
    datatypes = {
        "auto": "INT(5) NOT NULL AUTO_INCREMENT",
        "int": "INT",
        "bigint": "BIGINT",
        "double": "DOUBLE",
        "decimal": "DECIMAL",
        "char": ("TEXT", "VARCHAR"),
        "bool": "BOOL",
    }
    max_int = 4294967295
    required_opts = [("user",
                      "Enter your MySQL username",
                      "root"),
                     ("password",
                      "Enter your password",
                      ""),
                     ("host",
                      "Enter your MySQL host",
                      "localhost"),
                     ("port",
                      "Enter your MySQL port",
                      3306),
                     ("database_name",
                      "Format of database name",
                      "{db}"),
                     ("table_name",
                      "Format of table name",
                      "{db}.{table}"),
                     ]

    def url_string(self):
 
        return "ToDos:url_string from opts"

    def db_connect(self):
        """
        Performs database connection using database settings from settings.py.
        Returns sqlalchemy engine instance
        """
        return create_engine(self.url_string())

    def create_db_statement(self):
        createstatement = "CREATE DATABASE IF NOT EXISTS " + self.database_name()
        return createstatement


