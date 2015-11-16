import getpass

from weaver.lib.models import *
import weaver
from weaver import config_path
from weaver.engines import engine_list


def get_saved_connection(engine_name):
    """Given the name of an engine, returns the stored connection for that engine
    from connections.config."""
    parameters = {}
    if os.path.isfile(config_path):
        config = open(config_path, "rb")
        for line in config:
            values = line.rstrip('\n').split(',')
            if values[0] == engine_name:
                try:
                    parameters = eval(','.join(values[1:]))
                except:
                    pass
    return parameters


def save_connection(engine_name, values_dict):
    """Saves connection information for an engine in connections.config."""
    lines = []
    if os.path.isfile(config_path):
        config = open(config_path, "rb")
        for line in config:
            if line.split(',')[0] != engine_name:
                lines.append('\n' + line.rstrip('\n'))
        config.close()
        os.remove(config_path)
        config = open(weaver.config_path, "wb")
    else:
        config = open(config_path, "wb")
    if "file" in values_dict:
        values_dict["file"] = os.path.abspath(values_dict["file"])
    config.write(engine_name + "," + str(values_dict))
    for line in lines:
        config.write(line)
    config.close()


def get_default_connection():
    """Gets the first (most recently used) stored connection from
    connections.config."""
    print(config_path)
    if os.path.isfile(config_path):
        config = open(config_path, "rb")
        default_connection = config.readline().split(",")[0]
        config.close()
        return default_connection
    else:
        return None


def choose_engine(opts, choice=True):
    """
     choose an engine based on the options provided
    """
    # check if we have a requested engine
    if "engine" in opts.keys():
        # get the name of the engine
        engine_name = opts["engine"]
    elif opts["command"] == "download":
            engine_name = "download"
            print("HENRY TODOS: this part may need to be removed")
    else:
        print("HENRY TODOS: Error handling needs implementation: may never be reached")
        print("yesss")

    engine = Engine()

    # match engine instance with request engine_name
    for this_engine in engine_list:
        if engine_name.lower() == this_engine.name.lower() or this_engine.abbreviation.lower() and engine_name.lower() == this_engine.abbreviation.lower():
            engine = this_engine
            engine.opts=opts

            # check if the args contain a password
            # get the password from user without displaying it over the terminal
            if 'password' in engine.opts:
                if not engine.opts['password']:
                    # # works well on linux not on window, can work on terminal
                    # engine.opts['password'] = getpass.getpass(
                    #     'enter password for user: ' + engine.opts["user"] + " on " + engine.name)

                    print('enter password for user: '+engine.opts["user"]+" on "+engine.name)
                    engine.opts['password'] = sys.stdin.readline().rstrip()   #used during development else use getpass

    return engine



