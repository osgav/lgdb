#!/usr/bin/env python
# osgav
#

from disco import clrprint, clrz, print_purple
from db import db_has_glasses
import sqlite3
from bs4 import BeautifulSoup


LG_DB = 'database/lgdb.sqlite3'




# entrypoint
#
def scrape_glasses(db_name, limiter):
    '''
    warn if scrape database already contains records
    initiate scrape
    load scraped URLs into database
    '''

    if db_has_glasses(db_name):
        clrprint("WARNING", "\n\t[+] [WARNING] this database already has records in 'glasses' table.")
        clrprint("WARNING", "\t[+] [WARNING] are you sure you want to --scrape more data into it?")
        clrprint("FAIL", "\n\t[+] type [yes] to scrape, or [no] to proceed without scraping:\n\n")

        user_answer = raw_input(clrz['FAIL'] + clrz['BOLD'] + "\t[+] " + clrz['ENDC'])

        if user_answer == "yes":
            clrprint("OKBLUE", "\n\t[+] [STARTING] scraping more records into database [%s]\n" % db_name)
            scrape_data = scrape_bgpdb(limiter)
            feed_database(db_name, scrape_data)

        elif user_answer == "no":
            clrprint("WARNING", "\n\t[+] [SKIPPING] not adding anything to database.\n")

        else:
            clrprint("FAIL", "\n\t please type [yes] or [no]")
    else:
        # provided database is empty, proceed with feed_database()
        clrprint("OKBLUE", "\n\t[+] [STARTED] scraping HTML & feeding database...")
        scrape_data = scrape_bgpdb(limiter)
        feed_database(db_name, scrape_data)
        clrprint("OKBLUE", "\t    [%s records inserted]\n" % len(scrape_data))


# --scrape Part I
#
def scrape_bgpdb(limiter):
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
