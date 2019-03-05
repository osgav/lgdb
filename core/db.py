#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_purple

import sqlalchemy
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




def connect_to_scrape_database(name):
    '''
    return connection to named database
    '''
    engine = sqlalchemy.create_engine('sqlite:///%s' % name)
    connection = engine.connect()
    return connection

def select_X_glasses(scrape_database, limiter):
    conn = connect_to_scrape_database(scrape_database)
    select = "SELECT * FROM glasses"
    result = conn.execute(select).fetchmany(limiter)
    conn.close()
    return result

def select_one_glass(scrape_database, lgid):
    conn = connect_to_scrape_database(scrape_database)
    select = "SELECT * FROM glasses WHERE lgid = :id"
    result = conn.execute(select, id=lgid).fetchall()
    conn.close()
    return result

def update_one_glass_detail(scrape_database, glass_record, detail, new_value):
    conn = connect_to_scrape_database(scrape_database)
    update = "UPDATE glasses SET %s = :new_value WHERE lgid = :id" % detail
    conn.execute(update, new_value=new_value, id=glass_record[0])  # magic number for lgid
    conn.close()
    return

def update_one_glass_last_changed(scrape_database, glass_record, timestamp):
    conn = connect_to_scrape_database(scrape_database)
    update = "UPDATE glasses SET last_changed = :timestamp WHERE lgid = :id"
    conn.execute(update, timestamp=timestamp, id=glass_record[0])  # magic number for lgid
    conn.close()
    return

def update_one_glass_last_checked(scrape_database, glass_record, timestamp):
    conn = connect_to_scrape_database(scrape_database)
    update = "UPDATE glasses SET last_checked = :timestamp WHERE lgid = :id"
    conn.execute(update, timestamp=timestamp, id=glass_record[0])  # magic number for lgid
    conn.close()
    return
