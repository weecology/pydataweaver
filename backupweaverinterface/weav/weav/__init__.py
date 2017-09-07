"""Data Retriever

This package contains a framework for creating and running scripts designed to
download published ecological data, and store the data in a database.

"""
from weav.lib.tools import set_proxy, create_home_dir
from .lib import *

create_home_dir()
set_proxy()
