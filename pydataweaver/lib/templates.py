"""Datasets are defined as scripts and have unique properties.
The Module defines generic dataset properties and models the
functions available for inheritance by the scripts or datasets.
"""
from __future__ import print_function

from pydataweaver.engines import choose_engine
from pydataweaver.lib.models import *
from pydataweaver.lib.process import make_sql


class Script(object):
    """This class defines the properties of a generic dataset.

    Each Dataset inherits attributes from this class to define
    it's Unique functionality.
    """

    def __init__(
        self,
        title="",
        description="",
        name="",
        urls=dict(),
        tables=dict(),
        ref="",
        public=True,
        addendum=None,
        citation="Not currently available",
        licenses=[{"name": None}],
        retriever_minimum_version="",
        version="",
        encoding="",
        message="",
        **kwargs
    ):

        self.title = title
        self.name = name
        self.filename = __name__
        self.description = description
        self.urls = urls
        self.tables = tables
        self.ref = ref
        self.public = public
        self.addendum = addendum
        self.citation = citation
        self.licenses = licenses
        self.keywords = []
        self.retriever_minimum_version = retriever_minimum_version
        self.encoding = encoding
        self.version = version
        self.message = message
        for key, item in list(kwargs.items()):
            setattr(self, key, item[0] if isinstance(item, tuple) else item)

    def __str__(self):
        desc = self.name
        if self.reference_url():
            desc += "\n" + self.reference_url()
        return desc

    def integrate(self, engine=None, debug=False):
        """Generic function to prepare for integration."""
        self.engine = self.checkengine(engine)
        self.engine.debug = debug
        self.engine.db_name = self.name
        self.engine.create_db()

    def reference_url(self):
        if self.ref:
            return self.ref
        else:
            if len(self.urls) == 1:
                return self.urls[list(self.urls.keys())[0]]
            else:
                return None

    def checkengine(self, engine=None):
        """Returns the required engine instance"""
        if engine is None:
            opts = {}
            engine = choose_engine(opts)
        engine.get_input()
        engine.script = self
        return engine

    def exists(self, engine=None):
        if engine:
            return engine.exists(self)
        else:
            return False

    def matches_terms(self, terms):
        try:
            search_string = " ".join(
                [self.name, self.description, self.name] + self.keywords
            ).upper()

            for term in terms:
                if not term.upper() in search_string:
                    return False
            return True
        except:
            return False


class BasicTextTemplate(Script):
    """Defines the pre processing required for scripts.

    Scripts that need pre processing should use the download function
    from this class.
    Scripts that require extra tune up, should override this class.
    """

    def __init__(self, **kwargs):
        Script.__init__(self, **kwargs)
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.db_table_name = None

    def integrate(self, engine=None, debug=False):
        """Create the SQL query to be sent to the Engine

        Uses the scripts' integrate function to prepare the engine
        and it creates the database to store the result.
        """
        Script.integrate(self, engine, debug)
        sql_statement = make_sql(self)
        result_db = engine.database_name()
        result_table = self.result["table"]
        db_table_name = "{db_name}.{table_name}".format(
            db_name=result_db, table_name=result_table
        )

        self.db_table_name = db_table_name
        Script.db_table_name = db_table_name

        drop_query = self.engine.drop_statement("TABLE", db_table_name)
        join_query = sql_statement.format(
            result_dbi=result_db, result_tablei=result_table
        )
        try:
            if self.engine.debug:
                print(drop_query)
            self.engine.execute(drop_query)
        except:
            pass
        try:
            if self.engine.debug:
                print(join_query)
            self.engine.execute(join_query)
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception as _:
                pass
            print(e)
        print("Process successfully launched in Database.")
        print("Please wait for the table to render")
        return engine


TEMPLATES = {"default": BasicTextTemplate}
