"""Data Weaver

This package contains a framework for Integrating Data.
The package supports both tabular and spatial data
"""
from weaver.lib.tools import set_proxy, create_home_dir
from .lib import *

create_home_dir()
set_proxy()
