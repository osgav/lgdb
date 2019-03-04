#!/usr/bin/env python
# osgav
#

from disco import clrprint
from db import scrape_db_has_glasses, select_all_glasses, select_X_glasses
from prober import probe_glass
from parser import crawl_parser
from logger import crawl_logger

import sqlite3
import requests
import re
import time




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

        for glass_record in glasses: 
            glass_url = glass_record[5]  # magic number for glass_url
            crawl_response = probe_glass(glass_url)
            crawl_logger(glass_record, crawl_response)
            crawl_parser(scrape_database, glass_record, crawl_response)
        
        clrprint("GREEN", "\n\n\t[+] [DONE] database [%s] updated (or not) with crawl data." % scrape_database)
