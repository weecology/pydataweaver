FROM ubuntu:16.04

MAINTAINER Weecology "https://github.com/weecology/weaver"

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --force-yes build-essential wget git locales locales-all > /dev/null
RUN apt-get install -y --force-yes postgresql-client mysql-client > /dev/null

# Set encoding
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Remove python2 and install python3
RUN apt-get remove -y python && apt-get install -y python3  python3-pip curl
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN rm -f /usr/bin/pip && ln -s /usr/bin/pip3 /usr/bin/pip

RUN echo "export PATH="/usr/bin/python:$PATH"" >> ~/.profile
RUN echo "export PYTHONPATH="/usr/bin/python:$PYTHONPATH"" >> ~/.profile
RUN echo "export PGPASSFILE="~/.pgpass"" >> ~/.profile

# Add permissions to config files
# TODO:Test if line is needed
RUN chmod 0644 ~/.profile

# Install retriever dev  version, python core package
RUN pip install git+https://git@github.com/weecology/retriever.git
RUN retriever ls > /dev/null
RUN pip install  psycopg2 pymysql > /dev/null
RUN pip  install codecov pytest-cov  pytest-xdist pytest==3.9.3 -U

# Install Postgis after Python is setup
RUN apt-get install -y --force-yes postgis

COPY . ./weaver
# Use entrypoint to run more configurations.
# Set permissions.
# entrypoint.sh will set out config files
RUN chmod 0755 /weaver/cli_tools/entrypoint.sh
ENTRYPOINT ["/weaver/cli_tools/entrypoint.sh"]

WORKDIR ./weaver

# Change permissions to config files
# Do not run these CMDS before Entrypoint.
RUN chmod 600 cli_tools/.pgpass
RUN chmod 600 cli_tools/.my.cnf

CMD ["bash", "-c", "retriever -v"]
