#!/usr/bin/env python
'''database operations'''

# osgav
# 28 July 2017

from __future__ import print_function
from core.disco import clrprint

import os
import sqlite3
import optparse
import time


LG_DB = 'database/lgdb.sqlite3'
LG_DBSCHEMA = 'config/lgdb_schema_ext5.sql' # default schema if none specified via --schema


# -n --newdb
# --> create new sqlite3 database file and apply schema
#
def create_fresh_database(db_name, db_schema):
    '''create a new sqlite3 database'''

    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    lg_db_is_new = not os.path.exists(lg_db)
    with sqlite3.connect(lg_db) as conn:

        # if database does not exist already
        # create it and apply schema
        #
        if lg_db_is_new:
            with open(db_schema, 'rt') as fhandle:
                apply_schema = fhandle.read()
                conn.executescript(apply_schema)
            clrprint("GREEN", "\t[+] [DONE] created [%s] database with [%s] schema." % (db_name, db_schema))
        else:
            clrprint("WARNING", "\t[+] [SKIPPING] database already exists - not applying schema.\n")
            exit(0)
    return


# --col --type
# --> add new column to existing database...
#
def new_column(db_name, column_name, data_type):
    '''add new column to glasses table in specified database'''

    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    with sqlite3.connect(lg_db) as conn:
        cur = conn.cursor()
        cur.execute("""
        ALTER TABLE glasses ADD COLUMN '%s' '%s'
        """ % (column_name, data_type))

    clrprint("GREEN", "\t[+] [DONE] added column [%s] to database [%s]" % (column_name, db_name))


USAGE = """

dbops.py -n newdatabase [-s schema]
OR
dbops.py -d existingdatabase -c col -t type
"""

# START
#
def main():
    '''dbops.py entry point'''
    start_time = time.time()

    parser = optparse.OptionParser(USAGE)

    parser.add_option('-n',
                      '--new-db',
                      dest='newdb',
                      type='string',
                      help='create new db')

    parser.add_option('-s',
                      '--schema',
                      dest='sf',
                      type='string',
                      help='specify schema file')

    parser.add_option('-d',
                      '--db',
                      dest='db',
                      type='string',
                      help='specify existing db')

    parser.add_option('-c',
                      '--col',
                      dest='col',
                      type='string',
                      help='specify new column name')

    parser.add_option('-t',
                      '--type',
                      dest='dt',
                      type='string',
                      help='specify new column data type')

    (options, args) = parser.parse_args()
    database_requested = options.newdb
    database_provided = options.db
    schema_file = options.sf
    col_name = options.col
    col_type = options.dt
    active_database = ""

    #### start processing command line options <<<<

    # can't proceed with no options!
    if database_requested is None and \
       schema_file is None and \
       database_provided is None and \
       col_name is None and \
       col_type is None:
        clrprint("FAIL", "\n\t $ python dbops.py --help\n\n")
        exit(0)

    # optional schema file referenced?
    #
    if schema_file is not None:
        db_schema = schema_file
    else:
        # use default (hardcoded in here) setting for schema file
        db_schema = LG_DBSCHEMA

    # set 'active_database'
    if database_requested is None:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not creating new database.")
        if database_provided is None:
            clrprint("FAIL", "\t[+] [ERROR] must specify either new or existing database name.\n")
            exit(0)
        else:
            active_database = database_provided
    else:
        clrprint("OKBLUE", "\n\t[+] [STARTED] creating fresh database... [%s]" % database_requested)
        active_database = database_requested
        create_fresh_database(active_database, db_schema)

    # column to be added?
    #
    if col_name is not None and col_type is not None:

        # add column to active_database!
        clrprint("OKBLUE", "\n\t[+] [STARTED] adding column [%s] to database [%s]" % (col_name, active_database))
        new_column(active_database, col_name, col_type)
    else:
        clrprint("WARNING", "\n\t[+] [SKIPPING] no columns to be added.")

    #### stop processing command line options <<<<

    end_time = time.time()
    elapsed_time = end_time - start_time

    clrprint("GREEN", "\n\t[+] [COMPLETED] dbops run finished in %0.1f seconds.\n\n" % elapsed_time)
    exit(0)


if __name__ == "__main__":
    main()
