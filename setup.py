from __future__ import absolute_import
import platform

import os


# Always prefer setuptools over distutils
from codecs import open
from setuptools import setup
from pkg_resources import parse_version

current_platform = platform.system().lower()
extra_includes = []

__version__ = 'v0.0.dev'
with open(os.path.join("weaver", "_version.py"), "w") as version_file:
    version_file.write("__version__ = " + "'" + __version__ + "'\n")
    version_file.close()


def clean_version(v):
    return parse_version(v).__repr__().lstrip("<Version('").rstrip("')>")


# Get the long description from the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()    
    

if current_platform == "darwin":
    try: import py2app
    except ImportError: pass
    extra_includes = []
elif current_platform == "windows":
    try: import py2exe
    except ImportError: pass
    import sys
    extra_includes = ['pyodbc', 'inspect']
    sys.path.append("C:\\Windows\\winsxs\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91")


def is_wxpython_installed():
    """Returns True if  wxpython is installed"""
    try:
        return __import__("wx")
    except ImportError:
        return False

packages = [
            'weaver.engines',
            'weaver.lib',
            'weaver.util',
            'weaver',
            ]

includes = [
            'xlrd',
            'future',
            'pymysql',
            'psycopg2',
            'sqlite3',
            'sqlalchemy'
            ] + extra_includes

excludes = [
            'pyreadline',
            'doctest',
            'pickle',
            'calendar',
            'pdb',
            'pywin', 'pywin.debugger',
            'pywin.debugger.dbgcon',
            'pywin.dialogs', 'pywin.dialogs.list',
            'Tkconstants', 'Tkinter', 'tcl', 'tk'
            ]


#===============================================================================
# setting up the main set up attributes
#===============================================================================
setup(
    name='weaver',
    version=clean_version(__version__),
    description='Data Weaver',
    long_description=long_description,
    url='http://weecology.org/',
    author='Henry Senyondo, Ethan White',
    author_email='ethan@weecology.org',
    classifiers=['Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Operating System :: OS Independent',
                 ],
    license='MIT',
    keywords='data integration, data science',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'sample']),
    packages=packages,
    package_dir={
              'weaver':'weaver'
              },
    entry_points={
        'console_scripts': [
            'weaver = weaver.__main__:main',
        ],
      },
    install_requires=['xlrd', 'future'],

    # py2app flags
    app=['__main__.py'],
    data_files=[('', ['CITATION'])],
    setup_requires=[],
    
    # options
    # optimize is set to 1 of py2app to avoid errors with pymysql
    # bundle_files = 1 or 2 was causing failed builds so we moved
    # to bundle_files = 3 and Inno Setup
    # options = {'py2exe': {'bundle_files': 3,
    #                       'compressed': 2,
    #                       'optimize': 1,
    #                       'packages': packages,
    #                       'includes': includes,
    #                       'excludes': excludes,
    #                       },
    #            'py2app': {'packages': ['weaver'],
    #                       'includes': includes,
    #                       'site_packages': True,
    #                       'resources': [],
    #                       'optimize': 1,
    #                       'argv_emulation': True,
    #                       'no_chdir': True,
    #                       'iconfile': 'osx_icon.icns',
    #                       },
    #           },

)
