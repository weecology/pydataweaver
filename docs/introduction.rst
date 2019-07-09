==========
User Guide
==========


The Pydata Weaver Project
=========================

The Pydataweaver is a Python tool that offers a simple to use, clean and
a robust data integration platform.

The Pydataeaver supports data integration of spatial datasets (Raster
and Vector data), as well as tabular datasets.

Problem solving in science involves and requires studying entities using
a broad range of associations among the entities under study. These
associations are obtained through collecting and integrating various
sources and forms of data.

Since these heterogenous datasets are collected by various scientists,
the datasets are domain based or centered around a unique subset of
problems.

The Pydataweaver bridges the gap scientist’s face of not having readily
unified datasets that can be used for multi dimension feature analysis.
The Pydataweaver handles the finding and integration of heterogeneous
datasets forming a new dataset.

Dependencies
------------

This package requires Python 3.3+, recommends Python 3.6+ and depends on
the following packages:

::

    retriever
    PyMySQL>=0.4
    psycopg2>=2.0
    gdal
    future
    numpydoc
    pandas

They can be installed using ``pip``.

::

   sudo pip install -r requirements.txt

The package supports the following database management systems (DBMS):

========== ================ ================
DBMS       Spatial Datasets Tabular Datasets
========== ================ ================
PostgreSQL Yes              Yes
SQLite     No               Yes
========== ================ ================

Installing From Source
----------------------

Either use pip to install directly from GitHub:

.. code:: shell

   pip install git+https://git@github.com/weecology/pydataweaver.git

or:

1. Clone the repository
2. From the directory containing setup.py, run the following command:
   ``pip install .``. You may need to include ``sudo`` at the beginning
   of the command depending on your system (i.e.,
   ``sudo pip install .``).


Using the Command Line
----------------------


After installing the package, run `pydataweaver` update to download the latest available dataset scripts.
To see the full list of command line options and datasets run `pydataweaver --help`.

$ ``pydataweaver --help``

::

    usage: pydataweaver [-h] [-v] [-q] {help,ls,citation,license,join,update} ...

    positional arguments:
      {help,ls,citation,license,join,update}
                            sub-command help
        help
        ls                  display a list all available datasets
        citation            view citation
        license             view dataset licenses
        join                integrate data using a data package script
        update              download updated versions of data package scripts

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -q, --quiet           suppress command-line output

To get a list of available dataset use `pydataweaver ls`

$ ``pydataweaver ls``

::

    Available datasets : 11

    breed-bird-routes-bioclim
    mammal-community-bioclim
    mammal-community-masses
    mammal-community-sites-all-bioclim
    mammal-community-sites-bioclim
    mammal-community-sites-harvard-linear-features
    mammal-community-sites-harvard-linear-features-soils
    mammal-community-sites-harvard-soil
    mammal-diet-mammal-life-history
    mammal-sites-bioclim-1-2
    portal-plot-species

To view the citaion of the datasets use `pydataweaver citation [dataset-name]`
Running weaver with no citation will provide the citation for the tool.


$ ``pydataweaver citation mammal-diet-mammal-life-history``


::

    Dataset:  mammal-diet-mammal-life-history
    Description:   Integrated data set of mammal-life-hist and mammal-diet
    Citations:
    mammal-life-hist:    S. K. Morgan Ernest. 2003. ....
    mammal-diet:    Kissling WD, Dalby L, Flojgaard C, Lenoir J, ...

Integrating Data
----------------

**Examples Integrating Data with the join command**
To integrate data, run pydataweaver join [data package name] and provide the connection configurations.

::

    pydataweaver join postgres -h
    usage: pydataweaver join postgres [-h] [--user [USER]] [--password [PASSWORD]]
                                [--host [HOST]] [--port [PORT]]
                                [--database [DATABASE]]
                                [--database_name [DATABASE_NAME]]
                                [--table_name [TABLE_NAME]]
                                dataset

    positional arguments:
      dataset               file name

    optional arguments:
      -h, --help            show this help message and exit
      --user [USER], -u [USER]
                            Enter your PostgreSQL username
      --password [PASSWORD], -p [PASSWORD]
                            Enter your password
      --host [HOST], -o [HOST]
                            Enter your PostgreSQL host
      --port [PORT], -r [PORT]
                            Enter your PostgreSQL port
      --database [DATABASE], -d [DATABASE]
                            Enter your PostgreSQL database name
      --database_name [DATABASE_NAME], -a [DATABASE_NAME]
                            Format of schema name
      --table_name [TABLE_NAME], -t [TABLE_NAME]
                            Format of table name

To use the pydataweaver with postges .pgpass file set

$ ``pydataweaver join postgres``

or with command line configurations supplied

$ ``pydataweaver join postgres -u name-of-user -h host-name -d database-to-use``


Contribution
------------

If you find any operation that is not supported by this package, feel free to create a Github issue. Additionally, you are more than welcome to submit a pull request for a bug fix or additional feature.

If you find any operation that is not supported by this package, feel
free to create a Github issue. Additionaly you are more than welcome to submit
a pull request for a bug fix or additional feature.

Please take a look at the `Code of Conduct`_ governing contributions to this project.


Acknowledgments
---------------

Development of this software was funded by `the Gordon and Betty Moore
Foundation’s Data-Driven Discovery Initiative`_ to Ethan White.


.. _the Gordon and Betty Moore Foundation’s Data-Driven Discovery Initiative: http://www.moore.org/programs/science/data-driven-discovery
.. _Code of Conduct: https://github.com/weecology/pydataweaver/blob/master/docs/code_of_conduct.rst