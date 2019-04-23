# -*- coding: latin-1  -*-

from __future__ import absolute_import
from __future__ import print_function

import sys
from builtins import str
from imp import reload

import sphinx_rtd_theme

from weaver.lib.defaults import ENCODING

encoding = ENCODING.lower()

from weaver.lib.scripts import SCRIPT_LIST as WEAVER_ALL_SCRIPTS
from weaver.lib.tools import open_fw
from weaver.lib.defaults import VERSION, COPYRIGHT

reload(sys)
if hasattr(sys, "setdefaultencoding"):
    # set default encoding to latin-1 to decode source text
    sys.setdefaultencoding("latin-1")


def to_str(object, object_encoding=encoding):
    if sys.version_info >= (3, 0, 0):
        return str(object).encode("UTF-8").decode(encoding)
    return object


# Create the .rst file for the available datasets
datasetfile = open_fw("datasets_list.rst")
datasetfile_title = """==================
Datasets Available
==================


"""
# write the title of dataset rst file
datasetfile.write(datasetfile_title)


WEAVER_ALL_SCRIPTS = WEAVER_ALL_SCRIPTS()


for script_num, script in enumerate(WEAVER_ALL_SCRIPTS, start=1):
    name = title = script.name.strip()
    title = str(script_num) + ". **{}**\n".format(title.strip())

    datasetfile.write(title)
    datasetfile.write("-" * (len(title) - 1) + "\n\n")
    # keep the gap between : {} standard as required by restructuredtext
    datasetfile.write(":name: {}\n\n".format(name))
    datasetfile.write(":description: {}\n\n".format(script.description))
    datasetfile.write(":citation:\n\n")
    for items in script.citation:
        for cite in items.keys():
            datasetfile.write("\t**" + cite + "**: " + items[cite] + "\n\n")

    datasetfile.write("\n\n")
datasetfile.close()

needs_sphinx = "1.3"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

# General information about the project.
project = u"Data Weaver"
copyright = COPYRIGHT

version = release = VERSION

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
