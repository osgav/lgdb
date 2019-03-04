#!/usr/bin/env python
# osgav
#

from core.disco import clrprint
from core.scrape import scrape_glasses
from core.crawl import crawl_glasses
from core.db import check_scrape_database
from core.config import default

import optparse
import time


DEFAULT_LIMIT = default.DEFAULT_LIMIT
DB_ROOT = default.DB_ROOT




USAGE = """

$ glassops.py -d database [--scrape] [--crawl] [LIMITER]

you need to provide at least one of 'scrape' or 'crawl'

you need to provide LIMITER, an integer, to scrape or
crawl multiple URLs. the default is 1.
"""

# START
#
def main():
    '''glassops.py entry point'''
    start_time = time.time()

    parser = optparse.OptionParser(USAGE)

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
    limiter = args[0] if args else False


    # process any additional arguments - LIMITER
    #
    limit = DEFAULT_LIMIT
    if limiter:
        try:
            limit = int(limiter)
        except ValueError:
            clrprint("FAIL", "\n\t[+] [ERROR] can't limit to '%s' records. try an integer." % limiter)
            exit(0)


    # evaluate presence of -d
    #
    scrape_database = ""
    if database_provided is None:
        clrprint("FAIL", "\n\t $ python glassops.py --help\n\n")
        exit(0)
    else:
        scrape_database = "%s%s.sqlite3" % (DB_ROOT, database_provided)
        check_scrape_database(scrape_database)


    # evaluate presence of --scrape
    #
    if scrape_requested is not None:
        scrape_glasses(scrape_database, limit)
    else:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not scraping glasses source.")


    # evaluate presence of --crawl
    #
    if crawl_requested is not None:
        crawl_glasses(scrape_database, limit)
    else:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not crawling glasses URLs.")


    # glassops.py exit point
    #
    end_time = time.time()
    elapsed_time = end_time - start_time
    clrprint("GREEN", "\n\t[+] [COMPLETED] glassops run finished in %0.1f seconds.\n\n" % elapsed_time)
    exit(0)


if __name__ == "__main__":
    main()
