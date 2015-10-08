
""" The Weaver Project
This package provides a framework for intergrating various datasets.
"""

import imp
import os
from os.path import join, isfile, getmtime, exists
import platform
import sys


current_platform = platform.system().lower()
if current_platform != 'windows':
    import pwd

VERSION = 'v0.1'      
MASTER = True

# REPO_URL = "https://raw.github.com/weecology/retriever/"
# MASTER_BRANCH = REPO_URL + "master/"
# REPOSITORY = MASTER_BRANCH if MASTER else REPO_URL + VERSION + "/"

#===============================================================================
# create the necessary directory structure for storing scripts/raw_data
# in the ~/.weaver directory
#===============================================================================

HOME_DIR = os.path.expanduser('~/.weaver/')
for dir in (HOME_DIR, os.path.join(HOME_DIR, 'raw_data'), os.path.join(HOME_DIR, 'scripts')):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
            if (current_platform != 'windows') and os.getenv("SUDO_USER"):
                # owner of .weaver should be user even when installing w/sudo
                pw = pwd.getpwnam( os.getenv("SUDO_USER") )
                os.chown(dir, pw.pw_uid, pw.pw_gid)
        except OSError:
            print "The weaver lacks permission to access the ~/.weaver/ directory."
            raise
SCRIPT_SEARCH_PATHS =   [
                         "./",
                         "scripts",
                         os.path.join(HOME_DIR, 'scripts/'),
                         ]
SCRIPT_WRITE_PATH =     SCRIPT_SEARCH_PATHS[-1]
#===============================================================================
# script to be removed if we can create a generic dataset reader
#===============================================================================


DATA_SEARCH_PATHS =     [
                         "./",
                         "{dataset}",
                         "raw_data/{dataset}",
                         os.path.join(HOME_DIR, 'raw_data/{dataset}'),
                         ]
DATA_WRITE_PATH =       DATA_SEARCH_PATHS[-1]

#===============================================================================
# create default data directory
#===============================================================================

isgui = len(sys.argv) == 1 or ((len(sys.argv) > 1 and sys.argv[1] == 'gui'))
if current_platform == 'windows' and isgui:
    # The run path for installer based GUI on Windows is a system path.
    # Users won't expect the data to be stored there, so store it on the Desktop
    DATA_DIR = os.path.join(os.path.expanduser('~'), 'Desktop')
else:
    DATA_DIR = '.'



def set_proxy():
    """Check for proxies and makes them available to urllib"""
    proxies = ["https_proxy", "http_proxy", "ftp_proxy", "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY"]
    for proxy in proxies:
        if os.getenv(proxy):
            if len(os.environ[proxy]) != 0:
                for i in proxies:
                    os.environ[i] = os.environ[proxy]
                break

set_proxy()


sample_script = """# basic information about the script
name: Mammal Life History Database - Ernest, et al., 2003
shortname: MammalLH
description: S. K. Morgan Ernest. 2003. Life history characteristics of placental non-volant mammals. Ecology 84:3402.
tags: Taxon > Mammals, Data Type > Compilation
url: http://esapubs.org/archive/ecol/E084/093/default.htm

# tables
table: species, http://esapubs.org/archive/ecol/E084/093/Mammal_lifehistories_v2.txt"""
