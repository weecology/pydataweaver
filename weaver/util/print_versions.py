import os
import platform
import sys
import struct
import subprocess
import codecs
import locale
import importlib


def get_sys_info():
    """Get system information"""

    system_info = []
    try:
        (system, node, release, version, machine, processor) = platform.uname()
        system_info.extend([
            ("Python", "%d.%d.%d.%s.%s" % sys.version_info[:]),
            ("Python-bits", struct.calcsize("P") * 8),
            ("OS_name", "%s" % (system)),
            ("OS_release", "%s" % (release)),
            # ("Version", "%s" % (version)),
            ("Machine", "%s" % (machine)),
            ("Processor", "%s" % (processor)),
            ("Byteorder", "%s" % sys.byteorder),
            ("LC_ALL", "%s" % os.environ.get('LC_ALL', "None")),
            ("LANG", "%s" % os.environ.get('LANG', "None")),
            ("LOCALE", "%s.%s" % locale.getlocale()),

        ])
    except:
        pass

    return system_info


def get_versions():
    """Return version of dependencies"""

    sys_info = get_sys_info()

    dependencies = [
        # (MODULE_NAME, f(mod) -> mod version)
        # ("pandas", lambda mod: mod.__version__),
        # ("nose", lambda mod: mod.__version__),
        ("pip", lambda mod: mod.__version__),
        # ("setuptools", lambda mod: mod.__version__),
        # ("Cython", lambda mod: mod.__version__),
        # ("numpy", lambda mod: mod.version.version),
        # ("scipy", lambda mod: mod.version.version),
        # ("statsmodels", lambda mod: mod.__version__),
        # ("xarray", lambda mod: mod.__version__),
        # ("IPython", lambda mod: mod.__version__),
        # ("sphinx", lambda mod: mod.__version__),
        # ("patsy", lambda mod: mod.__version__),
        # ("dateutil", lambda mod: mod.__version__),
        # ("pytz", lambda mod: mod.VERSION),
        # ("blosc", lambda mod: mod.__version__),
        # ("bottleneck", lambda mod: mod.__version__),
        # ("tables", lambda mod: mod.__version__),
        # ("numexpr", lambda mod: mod.__version__),
        # ("matplotlib", lambda mod: mod.__version__),
        # ("openpyxl", lambda mod: mod.__version__),
        ("xlrd", lambda mod: mod.__VERSION__),
        # ("xlwt", lambda mod: mod.__VERSION__),
        # ("xlsxwriter", lambda mod: mod.__version__),
        # ("lxml", lambda mod: mod.etree.__version__),
        # ("bs4", lambda mod: mod.__version__),
        # ("html5lib", lambda mod: mod.__version__),
        # ("httplib2", lambda mod: mod.__version__),
        # ("apiclient", lambda mod: mod.__version__),
        ("sqlalchemy", lambda mod: mod.__version__),
        ("pymysql", lambda mod: mod.__version__),
        ("psycopg2", lambda mod: mod.__version__)
        # ("jinja2", lambda mod: mod.__version__),
        # ("boto", lambda mod: mod.__version__),
        # ("pandas_datareader", lambda mod: mod.__version__)
    ]

    deps_info = list()
    for (mod_name, version_fun) in dependencies:
        try:
            if mod_name in sys.modules:
                mod = sys.modules[mod_name]
            else:
                mod = importlib.import_module(mod_name)
            vers = version_fun(mod)
            deps_info.append((mod_name, vers))
        except:
            deps_info.append((mod_name, None))

    return deps_info


def display_version(format=False):

    if format is False:
        print("\nSystem Info\n\n")
        for k, stat in get_sys_info():
            print("{}: {}".format(k, stat))
        print("\nDepedency versions")
        for k, stat in get_versions():
            print("{}: {}".format(k, stat))
    else:
        try:
            import json
        except:
            import simplejson as json

        json_format = dict(system=dict(get_sys_info()), dependencies=dict(get_versions()))

        if format is None:
            print(json.dumps(json_format, indent=4, sort_keys=True))
        else:
            with codecs.open(format, "wb", encoding='utf8') as file:
                json.dump(json_format, file, indent=4)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', nargs='?', default=False)
    args = parser.parse_args()

    display_version(args.json)
    return 0

if __name__ == "__main__":
    sys.exit(main())
