#!/usr/bin/env python
# osgav
#

from __future__ import print_function
from core.disco import clrprint
from core.db import create_scrape_database, new_column

import optparse
import time


#
# move to a config file
#
LG_DBSCHEMA = 'config/lgdb_schema_ext5.sql' # default schema if none specified via --schema
#
#
#



USAGE = """

$ dbops.py -n newdatabase [-s schemafile]

OR

$ dbops.py -d existingdatabase -c col -t type
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


    # can't proceed with no options!
    #
    if database_requested is None and \
       schema_file is None and \
       database_provided is None and \
       col_name is None and \
       col_type is None:
        clrprint("FAIL", "\n\t $ python dbops.py --help\n\n")
        exit(0)
    elif schema_file is not None:
        db_schema = schema_file
    else:
        # use default schema file
        db_schema = LG_DBSCHEMA

    # set 'active_database'
    #
    if database_requested is None:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not creating new database.")
        if database_provided is None:
            clrprint("FAIL", "\t[+] [ERROR] must specify either new or existing database name.\n")
            exit(0)
        else:
            active_database = database_provided
    else:
        clrprint("OKBLUE", "\n\t[+] [STARTED] creating new scrape database... [%s]" % database_requested)
        active_database = database_requested
        create_scrape_database(active_database, db_schema)

    # column to be added?
    #
    if col_name is not None and col_type is not None:

        # add column to active_database!
        clrprint("OKBLUE", "\n\t[+] [STARTED] adding column [%s] to database [%s]" % (col_name, active_database))
        new_column(active_database, col_name, col_type)
    else:
        clrprint("WARNING", "\n\t[+] [SKIPPING] no columns to be added.")


    # dbops.py exit point
    #
    end_time = time.time()
    elapsed_time = end_time - start_time
    clrprint("GREEN", "\n\t[+] [COMPLETED] dbops run finished in %0.1f seconds.\n\n" % elapsed_time)
    exit(0)


if __name__ == "__main__":
    main()
