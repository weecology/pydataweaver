import json

from sqlalchemy import *

from weaver import settings_path
from weaver.lib.models import Engine


class engine(Engine):
    """Engine instance for PostgreSQL."""
    name = "Postgres"
    abbreviation = "postgres"
    datatypes = {
                 "auto": "serial",
                 "int": "integer",
                 "bigint": "bigint",
                 "double": "double precision",
                 "decimal": "decimal",
                 "char": "varchar",
                 "bool": "boolean",
                 }
    max_int = 2147483647
    required_opts = [("user",
                      "Enter your PostgreSQL username",
                      "postgres"),
                     ("password",
                      "Enter your password",
                      ""),
                     ("host",
                      "Enter your PostgreSQL host",
                      "localhost"),
                     ("port",
                      "Enter your PostgreSQL port",
                      5432),
                     ("database",
                      "Enter your PostgreSQL database name",
                      "postgres"),
                     ("database_name",
                      "Format of schema name",
                      "{db}"),
                     ("table_name",
                      "Format of table name",
                      "{db}.{table}"),
                     ]

    def url_string(self):

        url_string = "urlstring string from opts"

        return url_string

    def db_connect(self):
        """
        Performs database connection using database settings from settings.py.
        Returns sqlalchemy engine instance
        """
        return create_engine(self.url_string())

    def create_db_statement(self):
        """In PostgreSQL, the equivalent of a SQL database is a schema."""
        return Engine.create_db_statement(self).replace("DATABASE", "SCHEMA")

    def create_db(self):
        """Creates the database"""
        try:
            Engine.create_db(self)
        except:
            self.connection.rollback()
            pass

    def create_table(self):
        """PostgreSQL needs to commit operations individually."""
        Engine.create_table(self)
        self.connection.commit()

    def drop_statement(self, objecttype, objectname):
        """In PostgreSQL, the equivalent of a SQL database is a schema."""
        statement = Engine.drop_statement(self, objecttype, objectname)
        statement += " CASCADE;"
        return statement.replace(" DATABASE ", " SCHEMA ")

    def escape_single_quotes(self, value):
        return value.replace("'", "''")



