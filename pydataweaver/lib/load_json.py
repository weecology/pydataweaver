from __future__ import division
from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
from builtins import zip
from builtins import str
import json
import sys
import pprint
from collections import OrderedDict
from pydataweaver.lib.templates import TEMPLATES
from pydataweaver.lib.models import myTables
from pydataweaver.lib.tools import open_fr

if sys.version_info[0] < 3:
    from codecs import open


def read_json(json_file, debug=False):
    """Read Json dataset package files"""
    json_object = OrderedDict()
    json_file_encoding = None
    json_file = str(json_file) + ".json"

    try:
        file_obj = open_fr(json_file)
        json_object = json.load(file_obj)
        if "encoding" in json_object:
            json_file_encoding = json_object["encoding"]
        file_obj.close()
    except ValueError:
        pass

    # Reload json using encoding if available
    try:
        if json_file_encoding:
            file_obj = open_fr(json_file, encoding=json_file_encoding)
        else:
            file_obj = open_fr(json_file)
        json_object = json.load(file_obj)
        file_obj.close()

    except ValueError:
        pass
    if type(json_object) is dict and "result" in json_object.keys():
        return TEMPLATES["default"](**json_object)
    return None
