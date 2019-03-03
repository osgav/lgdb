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

        for glass in glasses:  # glass = a tuple representing a row from the database
            glass_url = glass[5]  # magic number - find way to retrieve URL more clearly

            crawl_response = probe_glass(glass_url)  # exception handling in prober, it will always return object to pass along
            scrape_parser(glass, crawl_response)     # parser and
            # scrape_logger(glass, crawl_response)     # logger will both
                                                     # determine what to do with 'responses' vs 'exceptions'
                                                     # on their own




# # --crawl Part I
# #
# def run_crawl(scrape_database, limiter):
#     '''iterate through glass records and update database with (new) crawl data'''

#     # grab glass records from specified database
#     with sqlite3.connect(scrape_database) as conn:
#         cursor = conn.cursor()
#         cursor.execute('select lgid, glass_url_source from glasses')

#         for row_to_update in cursor.fetchmany(limiter):
#             # unpack glass ID and URL for probe_glass function
#             lgid, glass = row_to_update

#             # obtain glass crawl data and import to database
#             probe_details, last_updated = probe_glass(lgid, glass)
#             try:
#                 # check if crawl data in database needs updated or not first
#                 for key, value in probe_details.iteritems():

#                     # select current data for comparison to new data
#                     cursor.execute('select lgid, %s from glasses where lgid = %d' \
#                     % (key, lgid))

#                     for detail in cursor.fetchall():
#                         lgid, current_value = detail

#                         if str(current_value).encode('utf-8') == str(value).encode('utf-8'):
#                             database_was_updated = False
#                         else:
#                             # update database: overwrite current_value with (new) value
#                             cursor.execute('update glasses set %s = "%s" where lgid = %d' \
#                             % (key, value, lgid))
#                             database_was_updated = True

#                 # update last_changed if necessary
#                 if database_was_updated:
#                     cursor.execute('update glasses set last_changed = "%s" where lgid = %d' \
#                     % (last_updated, lgid))

#                 # update last_updated
#                 cursor.execute('update glasses set last_updated = "%s" where lgid = %d' \
#                 % (last_updated, lgid))

#                 conn.commit()

#             except Exception as err:
#                 print_dbf()
#                 print("\n\n")
#                 print(err)

#     clrprint("GREEN", "\n\n\t[+] [DONE] database [%s] updated with crawl data." % scrape_database)
#     return
