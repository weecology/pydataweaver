__author__ = 'Henry Senyondo'

import os
import platform
import sys
current_platform = platform.system().lower()
if current_platform != 'windows':
    pass
current_platform = platform.system().lower()
if current_platform != 'windows':
    import pwd

VERSION = 'v0.1'


DDDD =9
# REPO_URL = "https://raw.github.com/weecology/retriever/"
# MASTER_BRANCH = REPO_URL + "master/"
# REPOSITORY = MASTER_BRANCH if MASTER else REPO_URL + VERSION + "/"

#===============================================================================
# create the necessary directory structure for storing scripts/raw_data
# in the ~/.weaver directory
#===============================================================================


HOME_DIR = os.path.abspath(os.path.expanduser('~/.weaver/'))
config_path = os.path.abspath(os.path.join(HOME_DIR, 'connections.config'))
# todo configure settings path , make opt argument
settings_path = os.path.abspath(os.path.join(os.getcwd(),"manager/config/settings.json"))

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
