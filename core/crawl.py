#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_success, print_error, print_redir, print_fail, print_dbf
from db import scrape_db_has_glasses
import sqlite3
import requests
import re
import time




# entrypoint
#
def crawl_glasses(scrape_database, limiter):
    if scrape_db_has_glasses(scrape_database):
        clrprint("OKBLUE", "\n\t[+] [STARTED] crawling looking glasses...\n")
        run_crawl(scrape_database, limiter)
    else:
        clrprint("FAIL", "\n\t[+] [ERROR] no URLs to crawl in database [%s]" % scrape_database)


# --crawl Part I
#
def run_crawl(scrape_database, limiter):
    '''iterate through glass records and update database with (new) crawl data'''

    # grab glass records from specified database
    with sqlite3.connect(scrape_database) as conn:
        cursor = conn.cursor()
        cursor.execute('select lgid, glass_url_source from glasses')

        for row_to_update in cursor.fetchmany(limiter):
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

    clrprint("GREEN", "\n\n\t[+] [DONE] database [%s] updated with crawl data." % scrape_database)
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
    #   glass_url_destination
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
            print_error()

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
        print_fail()
        log_exception_details(glass_url, err)
        exception_status = "HTTPERROR"
    except requests.Timeout as err:
        print_fail()
        log_exception_details(glass_url, err)
        exception_status = "TIMEOUT"
    except requests.ConnectionError as err:
        print_fail()
        log_exception_details(glass_url, err)
        exception_status = "CONNECTIONERROR"
    except:
        print_fail()
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


def log_exception_details(glass_url, exception_obj):
    '''write exceptions to log file'''

    with open("exceptions.log", "a") as logfile:
        logfile.write("=====================================================================\n")
        logfile.write("url: %s\n\n" % glass_url)
        logfile.write(str(exception_obj))
        logfile.write("\n\n\n")
