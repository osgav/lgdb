#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_purple
from config import default

import sqlite3
import os




def create_scrape_database(name, schema):
    '''
    create sqlite3 database for storing scrape data
    '''
    if os.path.exists(name):
        clrprint("FAIL", "\t[+] [FAIL] database [%s] already exists." % name)
    else:
        with sqlite3.connect(name) as conn:
            with open(schema, 'rt') as handle:
                scrape_db_schema = handle.read()
                conn.executescript(scrape_db_schema)
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
        clrprint("FAIL", "\n\t[+] [ERROR] database [%s] does not exist." % scrape_database)
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


def feed_database(scrape_database, scrape_data):
    '''
    insert scrape data into sqlite3 database
    '''
    with sqlite3.connect(scrape_database) as conn:
        # FEEEED
        for row in scrape_data:
            conn.execute("""
            insert into glasses (name, asn, glass_url_source)
            values ('%s', '%s', '%s')
            """ % (row[0], row[1], row[2]))
            print_purple()
    clrprint("GREEN", "\n\n\t[+] [DONE] database [%s] has been fed." % scrape_database)


def select_all_glasses(scrape_database):
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM glasses")
        rows = cur.fetchall()
        return rows


def select_X_glasses(scrape_database, limiter):
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM glasses")
        rows = cur.fetchmany(limiter)
        return rows

def select_one_glass(scrape_database, lgid):
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM glasses WHERE lgid = %s" % lgid)
        rows = cur.fetchall()
        return rows

def update_one_glass_detail(scrape_database, glass_record, detail, new_value):
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute('UPDATE glasses SET %s = "%s" WHERE lgid = %d' % (detail, new_value, glass_record[0]))  # magic number for lgid
        conn.commit()
        return

def update_one_glass_last_changed(scrape_database, glass_record, timestamp):
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute('UPDATE glasses SET last_changed = "%s" WHERE lgid = %d' % (timestamp, glass_record[0]))  # magic number for lgid
        conn.commit()
        return

def update_one_glass_last_checked(scrape_database, glass_record, timestamp):
    with sqlite3.connect(scrape_database) as conn:
        cur = conn.cursor()
        cur.execute('UPDATE glasses SET last_updated = "%s" WHERE lgid = %d' % (timestamp, glass_record[0]))  # magic number for lgid
        #
        # change db schema to create last_checked field instead of last_updated
        #
        conn.commit()
        return
