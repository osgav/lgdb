#!/usr/bin/env python
'''looking glass operations'''

# osgav
# 26 July 2017
#
# 03 March 2018 --> add 'disco' imports / associated 'print' changes
#
#

from __future__ import print_function
from disco import clrprint
from disco import clrz

import sqlite3
import optparse
import re
import sys
import time
import requests
from bs4 import BeautifulSoup


LG_DB = 'database/lgdb.sqlite3'
LIMITER = 10 # default scrape / crawl limit


# pre scrape/crawl database check
#
def db_has_glasses(db_name):
    '''count rows in glasses table of specified database'''

    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    with sqlite3.connect(lg_db) as conn:

        cur = conn.cursor()
        cur.execute("SELECT * FROM glasses")
        rows = cur.fetchall()

        clrprint("OKBLUE", "\t[+] [INFO] number of rows in database [%s]: %d" % (db_name, len(rows)))

        glasscount = len(rows)
        return bool(glasscount)


# --scrape Part I
#
def scrape_bgpdb():
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
    return table_data[:LIMITER]


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


# --crawl Part I
#
def crawl_glasses(db_name):
    '''iterate through glass records and update database with (new) crawl data'''

    # grab glass records from specified database
    lg_db = LG_DB.replace("lgdb", "lgdb_%s" % db_name)
    with sqlite3.connect(lg_db) as conn:
        cursor = conn.cursor()
        cursor.execute('select lgid, glass_url_source from glasses')

        for row_to_update in cursor.fetchmany(LIMITER):
            # unpack glass ID and URL for probe_glass function
            lgid, glass = row_to_update

            # obtain glass crawl data and import to database
            probe_details, last_updated = probe_glass(lgid, glass)
            try:
                # check if crawl data in database needs updated or not first
                for key, value in probe_details.iteritems():

                    # select current data for comparison to new data
                    cursor.execute('select lgid, %s from glasses where lgid = %d' \
                    % (key, lgid))

                    for detail in cursor.fetchall():
                        lgid, current_value = detail

                        if str(current_value).encode('utf-8') == str(value).encode('utf-8'):
                            database_was_updated = False
                        else:
                            # update database: overwrite current_value with (new) value
                            cursor.execute('update glasses set %s = "%s" where lgid = %d' \
                            % (key, value, lgid))
                            database_was_updated = True

                # update last_changed if necessary
                if database_was_updated:
                    cursor.execute('update glasses set last_changed = "%s" where lgid = %d' \
                    % (last_updated, lgid))

                # update last_updated
                cursor.execute('update glasses set last_updated = "%s" where lgid = %d' \
                % (last_updated, lgid))

                conn.commit()

            except Exception as err:
                print_dbf()
                print("\n\n")
                print(err)

    clrprint("GREEN", "\n\n\t[+] [DONE] database [%s] updated with crawl data." % db_name)
    return


# --crawl Part II (subroutine)
#
def probe_glass(lgid, glass_url):
    '''request glass URL, collect crawl data for database and maintain log files'''

    probe_details = {}
    # details (columns) to collect data for:
    #   protocol_source
    #   http_status
    #   is_redirect
    #   glass_url_destination --> see probe_glass_redirect()
    #   headers_count
    #   headers_bytes
    #   response_bytes

    # GET PROBE DETAILS
    check_https_url_src = re.compile(r'^https:\/\/.*')
    if len(re.findall(check_https_url_src, glass_url)) == 1:
        probe_details['protocol_source'] = "HTTPS"
    else:
        probe_details['protocol_source'] = "HTTP"

    # request the glass url!
    exception_status = None
    localtime = time.localtime()
    last_updated = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)
    try:
        response = requests.get(glass_url)
        log_response_details(lgid, glass_url, response)

        # progress meter for visual tracking
        if len(response.history):
            print_redir()

            locations = []
            for resp in response.history:
                locations.append(resp.headers['Location'])

            # GET PROBE DETAILS
            probe_details['glass_url_destination'] = locations[-1]

            check_https_url_dest = re.compile(r'^https:\/\/.*')
            if len(re.findall(check_https_url_dest, probe_details['glass_url_destination'])) == 1:
                probe_details['protocol_destination'] = "HTTPS"
            else:
                probe_details['protocol_destination'] = "HTTP"

        elif response.ok:
            print_success()
        else:
            print_failure()

        # GET PROBE DETAILS
        probe_details['http_status'] = response.status_code
        if len(response.history):
            probe_details['is_redirect'] = "True"
        else:
            probe_details['is_redirect'] = "False"

        # GET PROBE DETAILS
        header_bytes = 0
        for header, value in response.headers.iteritems():
            hstring = "%s: %s" % (header, value)
            header_bytes += len(hstring.encode('utf-8'))
        probe_details['headers_bytes'] = header_bytes
        probe_details['headers_count'] = len(response.headers)
        probe_details['response_bytes'] = len(response.text.encode('utf-8'))

    except requests.HTTPError as err:
        print_fuck()
        log_exception_details(glass_url, err)
        exception_status = "HTTPERROR"
    except requests.Timeout as err:
        print_fuck()
        log_exception_details(glass_url, err)
        exception_status = "TIMEOUT"
    except requests.ConnectionError as err:
        print_fuck()
        log_exception_details(glass_url, err)
        exception_status = "CONNECTIONERROR"
    except:
        print_fuck()
        log_exception_details(glass_url, "something terrible seems to have happened")
        exception_status = "ERROR 666"

    if exception_status is not None:
        probe_details['glass_url_destination'] = exception_status
        probe_details['protocol_destination'] = exception_status
        probe_details['http_status'] = exception_status
        probe_details['is_redirect'] = exception_status
        probe_details['headers_bytes'] = exception_status
        probe_details['headers_count'] = exception_status
        probe_details['response_bytes'] = exception_status

    return probe_details, last_updated


# --crawl Part III (subsubroutine)
#
# def probe_glass_redirect(lgid, glass_url):
    # '''inspect 3xx redirect chains...'''

    # redirect_details = {}
    # details (columns) to collect data for:
    #   glass_url_destination
    #

    # re-request the glass url and follow redirects!
    # exception_status = None
    # try:
    #     response = requests.get(glass_url)

    #     locations = []
    #     for resp in response.history:
    #         locations.append(resp.headers['Location'])

    #     # GET PROBE DETAILS
    #     # set glass_url_destination to the value of last Location header in redirect chain
    #     redirect_details['glass_url_destination'] = locations[-1]

    #     # different log file: redirects.log
    #     # may want to slightly change the format / info for a single entry..
    #     log_redirect_details(lgid, glass_url, locations[-1], response)

    #     # update progress meter
    #     if response.ok:
    #         print_redir_success()
    #     else:
    #         print_redir_failure()

    # except requests.HTTPError as err:
    #     print_fuck()
    #     log_exception_details(glass_url, err)
    #     exception_status = "RED HTTPERROR"
    # except requests.Timeout as err:
    #     print_fuck()
    #     log_exception_details(glass_url, err)
    #     exception_status = "RED TIMEOUT"
    # except requests.ConnectionError as err:
    #     print_fuck()
    #     log_exception_details(glass_url, err)
    #     exception_status = "RED CONNECTIONERROR"
    # except:
    #     print_fuck()
    #     log_exception_details(glass_url, "something terrible seems to have happened")
    #     exception_status = "RED ERROR 666"

    # if exception_status is not None:
    #     redirect_details['glass_url_destination'] = exception_status

    # return redirect_details


# logging - headers, redirects and exceptions
#
def log_response_details(lgid, glass_url, response_obj):
    '''write details to log file outside of database'''

    localtime = time.localtime()
    time_string = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)

    with open("headers.log", "a") as logfile:
        logfile.write("=====================================================================\n")
        logfile.write("%s\n" % time_string)
        logfile.write("lgid: %s\n" % lgid)
        logfile.write("url: %s\n" % glass_url)
        logfile.write("status: %s\n\n" % str(response_obj.status_code))
        # for header, value in response_obj.request.headers.iteritems():
            # logfile.write("%s: %s\n" % (header, value))
        # logfile.write("\n\n\n")
        logfile.write("- - - - - - - - - -\n")
        for resp in response_obj.history:
            logfile.write("status code: %s\n" % resp.status_code)
            for header, value in resp.headers.iteritems():
                logfile.write("%s: %s\n" % (header, value))
            logfile.write("- - - - - - - - - -\n")
        logfile.write("status: %s\n" % response_obj.status_code)        
        for header, value in response_obj.headers.iteritems():
            logfile.write("%s: %s\n" % (header, value))
        logfile.write("=====================================================================\n\n")
        logfile.write("\n\n\n")


# def log_redirect_details(lgid, glass_url_src, glass_url_dest, response_obj):
#     '''write details to log file outside of database'''

#     localtime = time.localtime()
#     time_string = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)

#     with open("redirects.log", "a") as logfile:
#         logfile.write("=====================================================================\n")
#         logfile.write("%s\n" % time_string)
#         logfile.write("lgid: %s\n" % lgid)
#         logfile.write("url source:\t%s\n" % glass_url_src)
#         logfile.write("url dest:\t%s\n" % glass_url_dest)
#         # for header, value in response_obj.request.headers.iteritems():
#             # logfile.write("%s: %s\n" % (header, value))
#         # logfile.write("\n\n\n")
#         logfile.write("- - - - - - - - - -\n")
#         for resp in response_obj.history:
#             logfile.write("status code: %s\n" % resp.status_code)
#             for header, value in resp.headers.iteritems():
#                 logfile.write("%s: %s\n" % (header, value))
#             logfile.write("- - - - - - - - - -\n")
#         logfile.write("status: %s\n" % response_obj.status_code)
#         for header, value in response_obj.headers.iteritems():
#             logfile.write("%s: %s\n" % (header, value))

#         logfile.write("=====================================================================\n\n")
#         logfile.write("\n\n\n")

def log_exception_details(glass_url, exception_obj):
    '''write exceptions to log file'''

    with open("exceptions.log", "a") as logfile:
        logfile.write("=====================================================================\n")
        logfile.write("url: %s\n\n" % glass_url)
        logfile.write(str(exception_obj))
        logfile.write("\n\n\n")


# progress meter functions
#
def print_success():
    '''print a green thing'''
    print(clrz['BBG'] + clrz['GREEN'] +"[+]"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_failure():
    '''print a red thing'''
    print(clrz['BBG'] + clrz['FAIL'] +"[-]"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_redir():
    '''print a yellow thing'''
    print(clrz['BBG'] + clrz['WARNING'] +"[-]"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_redir_success():
    '''print a green thing'''
    print(clrz['BBG'] + clrz['GREEN'] +"{+}"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_redir_failure():
    '''print a red thing'''
    print(clrz['BBG'] + clrz['FAIL'] +"{-}"+ clrz['ENDC'], end="")
    sys.stdout.flush()    

def print_fuck():
    '''print fuck'''
    print(clrz['BBG'] + clrz['FAIL'] +"fuck"+ clrz['ENDC'], end="")
    sys.stdout.flush()
def print_dbf():
    '''print database fuck'''
    print(clrz['BBG'] + clrz['FAIL'] +"database fuck"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_purple():
    '''print a purple thing'''
    print(clrz['HEADER'] +"*"+ clrz['ENDC'], end="")
    sys.stdout.flush()
    time.sleep(0.01)


# START
#
def main():
    '''glassops.py entry point'''
    start_time = time.time()


    # construct command line options and read them
    #
    parser = optparse.OptionParser("\n\tglassops.py -d database [--scrape] [--crawl] [LIMITER]")
    parser.add_option('-d', '--db', dest='db', type='string', help='specify database')
    parser.add_option('--scrape', action='store_true', dest='scrp', help='scrape html, feed db')
    parser.add_option('--crawl', action='store_true', dest='crwl', help='crawl glasses, update db')
    parser.add_option('--tmpp', action='store_true', dest='tmpp', help='tmp print')

    (options, args) = parser.parse_args()
    existing_database = options.db
    should_i_scrape = options.scrp
    should_i_crawl = options.crwl
    temp_print = options.tmpp
    active_database = ""

    #### start processing command line options <<<<

    # can't proceed with no options!
    #
    if existing_database is None and \
       should_i_scrape is None and \
       should_i_crawl is None:
        clrprint("FAIL", "\n\t $ python glassops.py --help\n\n")
        exit(0)


    # process any additional arguments - LIMITER
    #
    if args:
        try:
            global LIMITER
            LIMITER = int(args[0])
            clrprint("GREEN", "\n\t[+] [DONE] setting scrape/crawl LIMITER to %s records" % LIMITER)
            # if len(args) > 1:
                # print("ignoring additional arguments: %s" % " ".join(args[1:]))

        except ValueError:
            clrprint("FAIL", "\n\t[+] [ERROR] can't limit to '%s' records. try an integer." % args[0])
    else:
        clrprint("OKBLUE", "\n\t[+] [INFO] using default scrape/crawl LIMITER of %d" % LIMITER)


    # set 'active_database'
    #
    if existing_database is None:
        clrprint("FAIL", "\n\t $ python glassops.py --help\n\n")
        exit(0) # mandatory: if not set can't proceed
    else:
        active_database = existing_database


    # evaluate presence of --scrape
    #
    if should_i_scrape is None:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not scraping bgpdb.html source.")
        clrprint("WARNING", "\t[+] [SKIPPING] not feeding database.\n")

    elif db_has_glasses(active_database):
        clrprint("WARNING", "\n\t[+] [WARNING] this database already has records in 'glasses' table.")
        clrprint("WARNING", "\t[+] [WARNING] are you sure you want to --scrape more data into it?")
        clrprint("FAIL", "\n\t[+] type [yes] to scrape, or [no] to proceed without scraping:\n\n")

        user_answer = raw_input(clrz['FAIL'] + clrz['BOLD'] + "\t[+] " + clrz['ENDC'])

        if user_answer == "yes":
            clrprint("OKBLUE", "\n\t[+] [STARTING] scraping %d records into database [%s]\n" % (LIMITER, active_database))
            scrape_data = scrape_bgpdb()
            feed_database(active_database, scrape_data)

        elif user_answer == "no":
            clrprint("WARNING", "\n\t[+] [SKIPPING] not adding anything to database.\n")

        else:
            clrprint("FAIL", "\n\t please type [yes] or [no]")

    else:
        # --scrape supplied and active_database is empty
        # proceed with feed_database()
        clrprint("OKBLUE", "\n\t[+] [STARTED] scraping HTML & feeding database...")
        scrape_data = scrape_bgpdb()
        feed_database(active_database, scrape_data)
        clrprint("OKBLUE", "\t    %s records inserted.\n" % len(scrape_data))


    # evaluate presence of --crawl
    #
    if should_i_crawl is None:
        clrprint("WARNING", "\n\t[+] [SKIPPING] not crawling looking glass URLs.")
        clrprint("WARNING", "\t[+] [SKIPPING] not updating database [%s] with crawl data.\n" % active_database)

    elif db_has_glasses(active_database):
        clrprint("OKBLUE", "\n\t[+] [STARTED] crawling looking glasses...\n")
        crawl_glasses(active_database)

    else:
        clrprint("FAIL", "\n\t[+] [ERROR] no data in database [%s]" % active_database)

    #### stop processing command line options <<<<

    # glassops.py exit point
    end_time = time.time()
    elapsed_time = end_time - start_time
    clrprint("GREEN", "\n\t[+] [COMPLETED] glassops run finished in %0.1f seconds.\n\n" % elapsed_time)
    exit(0)


if __name__ == "__main__":
    main()
