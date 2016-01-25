"""
A setuptools based setup module.
"""
import platform
import warnings

from __init__ import VERSION


# Always prefer setuptools over distutils
from codecs import open
from os import path
from setuptools import setup

# To use a consistent encoding
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()    
    
    
current_platform = platform.system().lower()
extra_includes = []
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


def clean_version(v):
    """Returns the CLean version number"""
    if v == 'master':
        return '1.0.0'
    return v.replace('v', '').replace('.rc', '').replace('.beta', '')

packages = [
            'weaver.lib',
            'weaver.engines',
            'weaver.app',
            'weaver',
            ]

includes = [
            'xlrd',
            'wx',
            'pymysql',
            'psycopg2',
            'sqlite3',
            'sqlalchemy'
            'gdal'
            ] + extra_includes

excludes = [
            'pyreadline',
            'doctest',
            'optparse',
            'getopt',
            'pickle',
            'calendar',
            'pdb',
            'inspect',
            'email',
            'pywin', 'pywin.debugger',
            'pywin.debugger.dbgcon',
            'pywin.dialogs', 'pywin.dialogs.list',
            'Tkconstants', 'Tkinter', 'tcl',
            ]
# Check if python is installed
wx_installed = is_wxpython_installed()
if wx_installed is False:
    warnings.warn("""wxpython is not installed.
                  Weaver will not work in GUI mode.
                  For Weaver-gui install python-wxpython and
                  run 'python setup.py install' again.""",
                  UserWarning
                  )

setup(

    name='weaver',
    version=clean_version(VERSION),
    description='Data Weaver',
    
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/weecology/weaver',

    # Author details
    author='Ethan White, Henry Senyondo',
    author_email='ethan@weecology.org',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Intended Audience :: Science/Research',
               'License :: OSI Approved :: MIT License',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',],

    # What does your project relate to?
    keywords='data integration, ecological data',

    # packages=find_packages(exclude=['contrib', 'docs', 'test*', 'sample']),
    packages=packages,
    package_dir={
              'weaver': ''
              },
    entry_points={
        'console_scripts': [
            'weaver = weaver.__main__:main',
        ],
      },
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['xlrd'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    
    
    # py2exe flags
    console = [{'script': "__main__.py",
                'dest_base': "weaver",
               # 'icon_resources':[(1,'icon.ico')]
                }],
    zipfile = None,
    
    # py2app flags
    app=['__main__.py'],
    data_files=[('', ['CITATION'])],
    setup_requires=['py2app'] if current_platform == 'darwin' else [],
    
    # options
    # optimize is set to 1 of py2app to avoid errors with pymysql
    # bundle_files = 1 or 2 was causing failed builds so we moved
    # to bundle_files = 3 and Inno Setup
    options = {'py2exe': {'bundle_files': 3,
                          'compressed': 2,
                          'optimize': 1,
                          'packages': packages,
                          'includes': includes,
                          'excludes': excludes,
                          },
               'py2app': {'packages': ['weaver'],
                          'includes': includes,
                          'site_packages': True,
                          'resources': [],
                          'optimize': 1,
                          'argv_emulation': True,
                          'no_chdir': True,
                          'iconfile': 'osx_icon.icns',
                          },
              },

)
