from weaver.lib.tools import get_default_connection, get_saved_connection, choose_engine


class App:
    def __init__(self, engine_name):
        engine_name = engine_name
        
        default_connection = get_default_connection()
        if default_connection:
            parameters = get_saved_connection(default_connection)
            parameters["engine"] = default_connection
            engine = choose_engine(parameters)
        else:
            print " APPRUNNER 1"
        try:
            engine.get_connection()
        except:
            pass