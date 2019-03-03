#!/usr/bin/env python
# osgav
#

from core.disco import clrprint
from core.db import create_scrape_database, new_column
from core.config import default

import optparse
import time


DB_ROOT = default.DB_ROOT
DEFAULT_DBSCHEMA = default.DEFAULT_DBSCHEMA




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
    

    # process command line options
    #
    # new or existing database is required
    if database_requested is None and database_provided is None:
        clrprint("FAIL", "\n\t[+] [ERROR] must specify either new or existing database name.")
    #
    # new database with default schema
    elif database_requested is not None and schema_file is None:
        clrprint("OKBLUE", "\n\t[+] [STARTED] creating new scrape database... [%s]" % database_requested)
        name = "%s%s.sqlite3" % (DB_ROOT, database_requested)
        create_scrape_database(name, DEFAULT_DBSCHEMA)
    #
    # new database with custom schema
    elif database_requested is not None and schema_file is not None:
        clrprint("OKBLUE", "\n\t[+] [STARTED] creating new scrape database... [%s]" % database_requested)
        name = "%s%s.sqlite3" % (DB_ROOT, database_requested)
        create_scrape_database(name, schema_file)
    #
    # existing database and schema - not allowed
    elif database_provided is not None and schema_file is not None:
        clrprint("FAIL", "\n\t[+] [ERROR] schemas can only be applied to new databases.")
    #
    # existing database with new column details
    elif database_provided is not None and col_name is not None and col_type is not None:
        scrape_database = "%s%s.sqlite3" % (DB_ROOT, database_provided)
        clrprint("OKBLUE", "\n\t[+] [STARTED] adding [%s] column [%s] to database [%s]" % (col_type, col_name, scrape_database))
        new_column(scrape_database, col_name, col_type)
    #
    # invalid options provided
    else:
        clrprint("FAIL", "\n\t[+] [ERROR] you seem to have entered invalid options, see dbops.py --help")


    # dbops.py exit point
    #
    end_time = time.time()
    elapsed_time = end_time - start_time
    clrprint("GREEN", "\n\t[+] [COMPLETED] dbops run finished in %0.1f seconds.\n\n" % elapsed_time)
    exit(0)


if __name__ == "__main__":
    main()
