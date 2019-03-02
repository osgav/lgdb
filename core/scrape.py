#!/usr/bin/env python
# osgav
#


from disco import clrprint, print_purple
import sqlite3
from bs4 import BeautifulSoup




LG_DB = 'database/lgdb.sqlite3'
DEFAULT_SCRAPE_LIMIT = 10



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




# --scrape Part I
#
def scrape_bgpdb(limiter=DEFAULT_SCRAPE_LIMIT):
    '''scrape original datasource bgpdb.html'''

    soup = BeautifulSoup(open("source/bgpdb.html"), "lxml")
    souptable = soup.find("table")
    table_body = souptable.find("tbody")

    table_rows = table_body.find_all("tr")
    table_data = []
    for row in table_rows:

        row_cells = row.find_all("td")
        row_data = []
        for row_cell in row_cells:
            cell_data = row_cell.text
            row_data.append(cell_data)
        if len(row_data) > 1:
            table_data.append(row_data)
        # add row_data to table_data omitting header rows

    clrprint("GREEN", "\t[+] [DONE] bgpdb.html scraped.\n")
    return table_data[:limiter]




# --scrape Part II
#
def feed_database(db_name, scrape_data):
    '''insert scrape data into sqlite3 database'''

    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    with sqlite3.connect(lg_db) as conn:

        # FEEEED
        for row in scrape_data:
            conn.execute("""
            insert into glasses (name, asn, glass_url_source)
            values ('%s', '%s', '%s')
            """ % (row[0], row[1], row[2]))
            print_purple()

    clrprint("GREEN", "\n\n\t[+] [DONE] database [%s] has been fed." % db_name)
    return