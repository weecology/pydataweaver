"""Data weaver

This package contains a framework for integrating datasets

"""
from weaver.lib.engine_tools import set_proxy, create_home_dir
from .lib import *

create_home_dir()
set_proxy()
