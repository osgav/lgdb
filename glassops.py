#!/usr/bin/env python
# osgav
#

from __future__ import print_function
from core.disco import clrprint, clrz, print_success, print_error, print_redir, print_fail, print_dbf, print_purple
from core.db import db_has_glasses
from core.scrape import scrape_bgpdb, feed_database
from core.crawl import crawl_glasses

import optparse
import sys
import time


LG_DB = 'database/lgdb.sqlite3'




# START
#
def main():
    '''glassops.py entry point'''
    start_time = time.time()

    parser = optparse.OptionParser("\n\tglassops.py -d database [--scrape] [--crawl] [LIMITER]")

    parser.add_option('-d',
                      '--db',
                      dest='db',
                      type='string',
                      help='specify database')

    parser.add_option('--scrape',
                      action='store_true',
                      dest='scrape',
                      help='scrape html, feed db')

    parser.add_option('--crawl',
                      action='store_true',
                      dest='crawl',
                      help='crawl glasses, update db')

    (options, args) = parser.parse_args()
    database_provided = options.db
    scrape_requested = options.scrape
    crawl_requested = options.crawl
    active_database = ""
    limiter = args[0] if args else False


    # can't proceed without options or a database!
    #
    if database_provided is None and \
       scrape_requested is None and \
       crawl_requested is None:
        clrprint("FAIL", "\n\t $ python glassops.py --help\n\n")
        exit(0)
    elif database_provided is None:
        clrprint("FAIL", "\n\t $ python glassops.py --help\n\n")
        exit(0)
    else:
        active_database = database_provided


    # process any additional arguments - LIMITER
    #
    if limiter:
        try:
            limit = int(limiter)
        except ValueError:
            clrprint("FAIL", "\n\t[+] [ERROR] can't limit to '%s' records. try an integer." % limiter)
            exit(0)


    # evaluate presence of --scrape
    #
    if scrape_requested is None:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not scraping bgpdb.html source.")
        clrprint("WARNING", "\t[+] [SKIPPING] not feeding database.\n")
    elif db_has_glasses(active_database):
        clrprint("WARNING", "\n\t[+] [WARNING] this database already has records in 'glasses' table.")
        clrprint("WARNING", "\t[+] [WARNING] are you sure you want to --scrape more data into it?")
        clrprint("FAIL", "\n\t[+] type [yes] to scrape, or [no] to proceed without scraping:\n\n")

        user_answer = raw_input(clrz['FAIL'] + clrz['BOLD'] + "\t[+] " + clrz['ENDC'])

        if user_answer == "yes":
            clrprint("OKBLUE", "\n\t[+] [STARTING] scraping more records into database [%s]\n" % active_database)
            
            if limiter:
                scrape_data = scrape_bgpdb(limiter=limit)
            else:
                scrape_data = scrape_bgpdb()

            feed_database(active_database, scrape_data)
        
        elif user_answer == "no":
            clrprint("WARNING", "\n\t[+] [SKIPPING] not adding anything to database.\n")
        else:
            clrprint("FAIL", "\n\t please type [yes] or [no]")
    else:
        # --scrape supplied and active_database is empty, proceed with feed_database()
        clrprint("OKBLUE", "\n\t[+] [STARTED] scraping HTML & feeding database...")

        if limiter:
            scrape_data = scrape_bgpdb(limiter=limit)
        else:
            scrape_data = scrape_bgpdb()

        feed_database(active_database, scrape_data)

        clrprint("OKBLUE", "\t    [%s records inserted]\n" % len(scrape_data))


    # evaluate presence of --crawl
    #
    if crawl_requested is None:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not crawling looking glass URLs.")
        clrprint("WARNING", "\t[+] [SKIPPING] not updating database [%s] with crawl data.\n" % active_database)
    elif db_has_glasses(active_database):
        clrprint("OKBLUE", "\n\t[+] [STARTED] crawling looking glasses...\n")

        if limiter:
            crawl_glasses(active_database, limiter=limit)
        else:
            crawl_glasses(active_database)

    else:
        clrprint("FAIL", "\n\t[+] [ERROR] no URLs to crawl in database [%s]" % active_database)


    # glassops.py exit point
    #
    end_time = time.time()
    elapsed_time = end_time - start_time
    clrprint("GREEN", "\n\t[+] [COMPLETED] glassops run finished in %0.1f seconds.\n\n" % elapsed_time)
    exit(0)


if __name__ == "__main__":
    main()
