#!/usr/bin/env python
# osgav
#

from disco import clrprint, clrz
from db import scrape_db_has_glasses, feed_database

import sqlite3
from bs4 import BeautifulSoup




# entrypoint
#
def scrape_glasses(scrape_database, limiter):
    '''
    warn if scrape database already contains records
    initiate scrape
    load scraped URLs into database
    '''

    if scrape_db_has_glasses(scrape_database):
        clrprint("WARNING", "\n\t[+] [WARNING] this database already has records in 'glasses' table.")
        clrprint("WARNING", "\t[+] [WARNING] are you sure you want to --scrape more data into it?")
        clrprint("FAIL", "\n\t[+] type [yes] to scrape, or [no] to proceed without scraping:\n\n")

        user_answer = raw_input(clrz['FAIL'] + clrz['BOLD'] + "\t[+] " + clrz['ENDC'])

        if user_answer == "yes":
            clrprint("OKBLUE", "\n\t[+] [STARTING] scraping more records into database [%s]\n" % scrape_database)
            scrape_data = scrape_bgpdb(limiter)
            feed_database(scrape_database, scrape_data)

        elif user_answer == "no":
            clrprint("WARNING", "\n\t[+] [SKIPPING] not adding anything to database.\n")

        else:
            clrprint("FAIL", "\n\t please type [yes] or [no]")
    else:
        # provided database is empty, proceed with feed_database()
        clrprint("OKBLUE", "\n\t[+] [STARTED] scraping HTML & feeding database...")
        scrape_data = scrape_bgpdb(limiter)
        feed_database(scrape_database, scrape_data)
        clrprint("OKBLUE", "\t    [%s records inserted]\n" % len(scrape_data))


def scrape_bgpdb(limiter):
    '''
    scrape original datasource bgpdb.html
    '''
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
    clrprint("GREEN", "\t[+] [DONE] bgpdb.html scraped.\n")
    return table_data[:limiter]
