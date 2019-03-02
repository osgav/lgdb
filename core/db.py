#!/usr/bin/env python
# osgav
#

from disco import clrprint
import sqlite3
import os


LG_DB = 'database/lgdb.sqlite3'




# -n --new-db  create new sqlite3 database file and apply schema
#
def create_fresh_database(db_name, db_schema):
    '''create a new sqlite3 database'''
    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    lg_db_is_new = not os.path.exists(lg_db)

    with sqlite3.connect(lg_db) as conn:
        # if database does not exist already
        # create it and apply schema
        if lg_db_is_new:
            with open(db_schema, 'rt') as fhandle:
                apply_schema = fhandle.read()
                conn.executescript(apply_schema)
            clrprint("GREEN", "\t[+] [DONE] created [%s] database with [%s] schema." % (db_name, db_schema))
        else:
            clrprint("WARNING", "\t[+] [SKIPPING] database already exists - not applying schema.\n")
            exit(0)
    return


# --col --type  add new column to existing database...
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


# pre scrape/crawl database check
#
def db_has_glasses(db_name):
    '''count rows in glasses table of specified database'''

    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    #
    # TODO: check db file exists before trying to use it
    #
    with sqlite3.connect(lg_db) as conn:

        cur = conn.cursor()
        cur.execute("SELECT * FROM glasses")
        rows = cur.fetchall()

        clrprint("OKBLUE", "\n\t[+] [INFO] number of rows in database [%s]: %d" % (db_name, len(rows)))

        glasscount = len(rows)
        return bool(glasscount)
