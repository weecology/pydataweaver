from weaver.lib.defaults import ENCODING
from weaver.lib.models import Engine


class engine(Engine):
    """Engine instance for PostgreSQL."""

    name = "PostgreSQL"
    abbreviation = "postgres"
    max_int = 2147483647
    placeholder = "%s"
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

    def create_db_statement(self):
        """In PostgreSQL, the equivalent of a SQL database is a schema.

        CREATE SCHEMA table_name;
        """
        return Engine.create_db_statement(self).replace("DATABASE", "SCHEMA")

    def create_db(self):
        """Create Engine database."""
        try:
            Engine.create_db(self)
        except:
            self.connection.rollback()
            pass

    def drop_statement(self, objecttype, objectname):
        """In PostgreSQL, the equivalent of a SQL database is a schema."""
        statement = Engine.drop_statement(self, objecttype, objectname)
        statement += " CASCADE;"
        return statement.replace(" DATABASE ", " SCHEMA ")

    def get_connection(self):
        """
        Get db connection.
        Please update the encoding lookup table if the required encoding is not present.
        """
        import psycopg2 as dbapi
        self.get_input()
        conn = dbapi.connect(host=self.opts["host"],
                             port=int(self.opts["port"]),
                             user=self.opts["user"],
                             password=self.opts["password"],
                             database=self.opts["database"])
        encoding = ENCODING.lower()
        if self.script.encoding:
            encoding = self.script.encoding.lower()
        encoding_lookup = {'iso-8859-1': 'Latin1', 'latin-1': 'Latin1', 'utf-8': 'UTF8'}
        db_encoding = encoding_lookup.get(encoding)
        conn.set_client_encoding(db_encoding)
        return conn
