#!/usr/bin/env python
# osgav
#


from disco import clrprint, clrz, print_success, print_error, print_redir, print_fail, print_dbf, print_purple
import sqlite3




LG_DB = 'database/lgdb.sqlite3'

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

        clrprint("OKBLUE", "\t[+] [INFO] number of rows in database [%s]: %d" % (db_name, len(rows)))

        glasscount = len(rows)
        return bool(glasscount)