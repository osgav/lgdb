#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_success, print_error, print_redir, print_fail, print_dbf
from db import select_one_glass

import re
import time




def scrape_parser(scrape_database, glass_record, crawl_response):
    '''
    parse crawl data into scrape database
    '''
    #
    # review contents of crawl_response['probe_result'] to decide on actions...
    #

    # happy path - there is a response to parse
    scrape = crawl_response['message']
    scrape_details_from_scrape = collect_details(glass_record, scrape)
    scrape_details_from_db = select_one_glass(scrape_database, glass_record[0])  # magic number for lgid

    # compare scrape details with existing data in database
    # only update database if it has changed
    # but always run at least 1 query updating 'last_updated' or 'last_run' field    

    print("details from scrape type: %s" % type(scrape_details_from_scrape))
    print("details from db type: %s" % type(scrape_details_from_db))
    print("....")
    print(scrape_details_from_scrape)
    print("....")
    print(scrape_details_from_db)
    print("....")


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





def collect_details(glass_record, scrape):
    '''
    take a requests 'response' object and parse details out of it
    return details in a dict
    '''
    # details to collect:
    #
    #   protocol_source
    #   http_status
    #   is_redirect
    #   glass_url_destination
    #   protocol_destination
    #   headers_count
    #   headers_bytes
    #   response_bytes
    #
    scrape_details = {}
    
    # protocol_source
    #
    check_https_url_src = re.compile(r'^https:\/\/.*')
    if len(re.findall(check_https_url_src, glass_record[5])) == 1:  # magic number again for glass_url
        scrape_details['protocol_source'] = "HTTPS"
    else:
        scrape_details['protocol_source'] = "HTTP"


    # https_status
    #
    scrape_details['http_status'] = scrape.status_code


    # is_redirects
    #
    if len(scrape.history):
        scrape_details['is_redirect'] = "True"
    else:
        scrape_details['is_redirect'] = "False"


    # glass_url_destination
    #
    locations = []
    for resp in scrape.history:
        locations.append(resp.headers['Location'])
    scrape_details['glass_url_destination'] = locations[-1]


    # protocol_destination
    #
    check_https_url_dest = re.compile(r'^https:\/\/.*')
    if len(re.findall(check_https_url_dest, scrape_details['glass_url_destination'])) == 1:
        scrape_details['protocol_destination'] = "HTTPS"
    else:
        scrape_details['protocol_destination'] = "HTTP"


    # headers_count
    #
    scrape_details['headers_count'] = len(scrape.headers)


    # headers_bytes
    #
    header_bytes = 0
    for header, value in scrape.headers.iteritems():
        hstring = "%s: %s" % (header, value)
        header_bytes += len(hstring.encode('utf-8'))
    scrape_details['headers_bytes'] = header_bytes


    # response_bytes
    #
    scrape_details['response_bytes'] = len(scrape.text.encode('utf-8'))

    # done
    return scrape_details
