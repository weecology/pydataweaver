from __future__ import absolute_import
import platform

import os

# Setuptools are preferred over distutils
from codecs import open
from setuptools import setup
from pkg_resources import parse_version
from setuptools import setup, find_packages

current_platform = platform.system().lower()
extra_includes = []

__version__ = '1.0.0'
with open(os.path.join("weaver", "_version.py"), "w") as version_file:
    version_file.write("__version__ = " + "'" + __version__ + "'\n")
    version_file.close()


def clean_version(v):
    return parse_version(v).__repr__().lstrip("<Version('").rstrip("')>")


# Get the long description from the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


if current_platform == "darwin":
    try:
        import py2app
    except ImportError:
        pass
    extra_includes = []
elif current_platform == "windows":
    try:
        import py2exe
    except ImportError:
        pass
    import sys

    extra_includes = ['pyodbc', 'inspect']
    sys.path.append("C:\\Windows\\winsxs\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91")


packages = [
    'weaver.lib',
    'weaver.engines',
    'weaver',
]

includes = [
               'xlrd',
               'future',
               'argcomplete',
               'pymysql',
               'psycopg2',
               'sqlite3',
           ] + extra_includes

excludes = [
    'pyreadline',
    'doctest',
    'pickle',
    'pdb',
    'pywin', 'pywin.debugger',
    'pywin.debugger.dbgcon',
    'pywin.dialogs', 'pywin.dialogs.list',
    'Tkconstants', 'Tkinter', 'tcl', 'tk'
]

setup(name='weaver',
      version=clean_version(__version__),
      description='Data weaver',
      author='Ethan White',
      author_email='ethan@weecology.org',
      url='https://github.com/weecology/weaver',
      classifiers=['Intended Audience :: Science/Research',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3', ],
      packages=find_packages(
          exclude=['hooks',
                   'docs',
                   'tests',
                   'scripts',
                   'docker',
                   ".cache" ]),

      entry_points={
          'console_scripts': [
              'weaver = weaver.__main__:main',
          ],
      },
      install_requires=[
          'xlrd',
          'future',
          'argcomplete'
      ],

      data_files=[('', ['CITATION'])],
      setup_requires=[],
      )

