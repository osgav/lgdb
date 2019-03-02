#!/usr/bin/env python
# osgav
#

from disco import clrprint
import sqlite3
import os


#
# move to a config file
#
DB_ROOT = 'database/'
#
#
#



def create_scrape_database(name, schema):
    '''
    create sqlite3 database for storing scrape data
    '''

    scrape_database = "%s%s.sqlite3" % (DB_ROOT, name)
    if os.path.exists(scrape_database):
        clrprint("FAIL", "\t[+] [FAIL] database [%s] already exists.\n" % name)
    else:
        with sqlite3.connect(scrape_database) as conn:
            with open(schema, 'rt') as handle:
                apply_schema = handle.read()
                conn.executescript(apply_schema)

        clrprint("GREEN", "\t[+] [DONE] created [%s] database with [%s] schema." % (name, schema))


def new_column(scrape_database, column_name, data_type):
    '''
    add new column to glasses table in specified database
    '''
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute("""
        ALTER TABLE glasses ADD COLUMN '%s' '%s'
        """ % (column_name, data_type))
    clrprint("GREEN", "\t[+] [DONE] added column [%s] to database [%s]" % (column_name, scrape_database))


def check_scrape_database(scrape_database):
    '''
    confirm named database exists
    print stats about it if it does
    '''
    if not os.path.exists(scrape_database):
        clrprint("FAIL", "\t[+] [ERROR] database [%s] does not exist.\n" % scrape_database)
    else:
        clrprint("OKBLUE", "\n\t[+] [INFO] database [%s] does indeed exist." % scrape_database)
        with sqlite3.connect(scrape_database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM glasses")
            rows = cur.fetchall()
            clrprint("OKBLUE", "\t[+] [INFO] database [%s] table 'glasses' has [%d] rows" % (scrape_database, len(rows)))


def scrape_db_has_glasses(scrape_database):
    '''
    pre-scrape database check: has an empty database been provided?
    pre-crawl database check: are there glass URLs to crawl?
    return False when database doesnt exist
    return False when database exists but has no glass URLs
    return True when database exists and has at least 1 glass URL
    '''
    if os.path.exists(scrape_database):
        with sqlite3.connect(scrape_database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM glasses")
            rows = cur.fetchall()
            glasscount = len(rows)
        return bool(glasscount)
    else:
        return False
