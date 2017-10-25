"""Data Weaver Tools

This module contains miscellaneous classes and functions used in Weaver
scripts.

"""
from __future__ import print_function

from future import standard_library

standard_library.install_aliases()

import difflib
import json
import platform
import shutil
import warnings

from hashlib import md5
from io import StringIO as newfile
from weaver.lib.defaults import HOME_DIR, ENCODING

from weaver.lib.models import *
import xml.etree.ElementTree as ET

warnings.filterwarnings("ignore")

TEST_ENGINES = dict()


def create_home_dir():
    """Create Directory for weaver."""
    current_platform = platform.system().lower()
    if current_platform != 'windows':
        import pwd

    # create the necessary directory structure for storing scripts/raw_data
    # in the ~/.weaver directory
    for dir in (HOME_DIR, os.path.join(HOME_DIR, 'raw_data'), os.path.join(HOME_DIR, 'scripts')):
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
                if (current_platform != 'windows') and os.getenv("SUDO_USER"):
                    # owner of .weaver should be user even when installing
                    # w/sudo
                    pw = pwd.getpwnam(os.getenv("SUDO_USER"))
                    os.chown(dir, pw.pw_uid, pw.pw_gid)
            except OSError:
                print("The Retriever lacks permission to access the ~/.weaver/ directory.")
                raise


def name_matches(scripts, arg):
    matches = []
    for script in scripts:
        if arg.lower() == script.name.lower():
            return [script]
        max_ratio = max([difflib.SequenceMatcher(None, arg.lower(), factor).ratio() for factor in
                         (script.name.lower(), script.title.lower(), script.filename.lower())] +
                        [difflib.SequenceMatcher(None, arg.lower(), factor).ratio() for factor in
                         [keyword.strip().lower() for keywordset in script.keywords for keyword in keywordset]]
                        )
        if arg.lower() == 'all':
            max_ratio = 1.0
        matches.append((script, max_ratio))
    matches = [m for m in sorted(matches, key=lambda m: m[1], reverse=True) if m[1] > 0.6]
    return [match[0] for match in matches]


def final_cleanup(engine):
    """Perform final cleanup operations after all scripts have run."""
    pass


def reset_weaver(scope="all"):
    """Remove stored information on scripts, data, and connections."""
    warning_messages = {
        'all': "\nRemove existing scripts, cached data, and information on database connections. \nDo you want to proceed? (y/N)\n",
        'scripts': "\nRemove existing scripts. \nSpecifically it will remove the scripts folder in {}.\nDo you want to proceed? (y/N)\n",
        'data': "\nRemove raw data cached by the Weaver. \nSpecifically it will remove the raw_data folder in {}. \nDo you want to proceed? (y/N)\n"
    }

    path = os.path.normpath(HOME_DIR)
    warn_msg = warning_messages[scope].format(path)
    confirm = input(warn_msg)
    while not (confirm.lower() in ['y', 'n', '']):
        print("Please enter either y or n.")
        confirm = input()
    if confirm.lower() == 'y':
        if scope in ['data', 'all']:
            shutil.rmtree(os.path.join(path, 'raw_data'))
        if scope in ['scripts', 'all']:
            shutil.rmtree(os.path.join(path, 'scripts'))


def getmd5(data, data_type='lines'):
    """Get MD5 of a data source."""
    checksum = md5()
    if data_type == 'lines':
        for line in data:
            if type(line) == bytes:
                checksum.update(line)
            else:
                checksum.update(str(line).encode())
        return checksum.hexdigest()
    files = []
    if data_type == 'file':
        files = [os.path.normpath(data)]
    if data_type == 'dir':
        for root, directories, filenames in os.walk(os.path.normpath(data)):
            for filename in sorted(filenames):
                files.append(os.path.normpath(os.path.join(root, filename)))
    for file_path in files:
        # don't use open_fr to keep line endings consistent across OSs
        if sys.version_info >= (3, 0, 0):
            if os.name == 'nt':
                input_file = io.open(file_path, 'r', encoding=ENCODING)
            else:
                input_file = open(file_path, 'r', encoding=ENCODING)
        else:
            input_file = io.open(file_path, encoding=ENCODING)

        for line in input_file:
            if type(line) == bytes:
                checksum.update(line)
            else:
                checksum.update(str(line).encode())
    return checksum.hexdigest()


def create_file(data, output='output_file'):
    """Write lines to file from a list."""
    output_file = os.path.normpath(output)
    with open(output_file, 'w') as testfile:
        for line in data:
            testfile.write(line)
            testfile.write("\n")
    return output_file


def file_2list(input_file):
    """Read in a csv file and return lines a list."""
    input_file = os.path.normpath(input_file)

    if sys.version_info >= (3, 0, 0):
        input_obj = io.open(input_file, 'rU')
    else:
        input_obj = io.open(input_file, encoding=ENCODING)

    abs_list = []
    for line in input_obj.readlines():
        abs_list.append(line.strip())
    return abs_list


def set_proxy():
    """Check for proxies and makes them available to urllib."""
    proxies = ["https_proxy", "http_proxy", "ftp_proxy",
               "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY"]
    for proxy in proxies:
        if os.getenv(proxy):
            if len(os.environ[proxy]) != 0:
                for i in proxies:
                    os.environ[i] = os.environ[proxy]
                break

