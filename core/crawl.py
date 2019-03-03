#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_success, print_error, print_redir, print_fail, print_dbf
from db import scrape_db_has_glasses, select_all_glasses, select_X_glasses
from prober import probe_glass
from parser import scrape_parser
from logger import scrape_logger

import sqlite3
import requests
import re
import time




# entrypoint
#
def crawl_glasses(scrape_database, limiter):
    '''
    confirm database has glass URLs to crawl
    crawl URLs
    send responses to parser and logger
    '''
    if not scrape_db_has_glasses(scrape_database):
        clrprint("FAIL", "\n\t[+] [ERROR] no URLs to crawl in database [%s]" % scrape_database)
    else:
        clrprint("OKBLUE", "\n\t[+] [STARTED] crawling looking glasses...\n")
        glasses = select_X_glasses(scrape_database, limiter)

        for glass_record in glasses:  # glass_record = a tuple representing a row from the database
            glass_url = glass_record[5]  # magic number - find way to retrieve URL more clearly

            crawl_response = probe_glass(glass_url)           # exception handling in prober, it will always return object to pass along
            scrape_parser(scrape_database, glass_record, crawl_response)       # parser and
            # scrape_logger(glass_record, crawl_response)                      # logger will both
                                                                               # determine what to do with 'responses' vs 'exceptions'
                                                                               # on their own
