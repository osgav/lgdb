#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_success, print_error, print_redir, print_fail, print_dbf
from db import select_one_glass

import re
import time




def crawl_parser(scrape_database, glass_record, crawl_response):
    '''
    parse "crawl responses" into scrape database
    '''
    #
    # review contents of crawl_response['probe_result'] to decide on actions...
    #

    # happy path - there is a response to parse
    crawl = crawl_response['message']
    details_from_crawl = get_crawl_details(glass_record, crawl)

    details_from_db_raw = select_one_glass(scrape_database, glass_record[0])  # magic number for lgid
    details_from_db = mapdbobject(details_from_db_raw)

    # compare scrape details with existing data in database
    # only update database if it has changed
    # but always run at least 1 query updating 'last_updated' or 'last_run' field    

    print("details from crawl type: %s" % type(details_from_crawl))
    print("details from db type: %s" % type(details_from_db))
    print("....")
    print(details_from_crawl)
    print("....")
    print(details_from_db)
    print("....")
    print("....")
    for key, value in details_from_crawl.iteritems():
        print("key: %s value: %s" % (key, value))
    print("....")
    print("....")
    for key, value in details_from_db.iteritems():
        print("key: %s value: %s" % (key, value))
    print("....")
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





def mapdbobject(db_list_tuple):
    '''
    take a list that contains a tuple which represents a row in a database
    (as returned from sqlite3) map to and return a dictionary
    '''
    db_row = db_list_tuple[0]

    lgid = db_row[0]
    last_updated = db_row[1]
    last_changed = db_row[2]
    name = db_row[3]
    asn = db_row[4]
    glass_url_source = db_row[5]
    glass_url_destination = db_row[6]
    protocol_source = db_row[7]
    protocol_destination = db_row[8]
    http_status = db_row[9]
    is_redirect = db_row[10]
    headers_count = db_row[11]
    headers_bytes = db_row[12]
    response_bytes = db_row[13]

    db_dict = {}
    db_dict['lgid'] = lgid
    db_dict['last_updated'] = last_updated
    db_dict['last_changed'] = last_changed
    db_dict['name'] = name
    db_dict['asn'] = asn
    db_dict['glass_url_source'] = glass_url_source
    db_dict['glass_url_destination'] = glass_url_destination
    db_dict['protocol_source'] = protocol_source
    db_dict['protocol_destination'] = protocol_destination
    db_dict['http_status'] = http_status
    db_dict['is_redirect'] = is_redirect
    db_dict['headers_count'] = headers_count
    db_dict['headers_bytes'] = headers_bytes
    db_dict['response_bytes'] = response_bytes

    return db_dict



def get_crawl_details(glass_record, crawl):
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
    crawl_details = {}
    
    # protocol_source
    #
    check_https_url_src = re.compile(r'^https:\/\/.*')
    if len(re.findall(check_https_url_src, glass_record[5])) == 1:  # magic number again for glass_url
        crawl_details['protocol_source'] = "HTTPS"
    else:
        crawl_details['protocol_source'] = "HTTP"


    # https_status
    #
    crawl_details['http_status'] = crawl.status_code


    # is_redirects
    #
    if len(crawl.history):
        crawl_details['is_redirect'] = "True"
    else:
        crawl_details['is_redirect'] = "False"


    # glass_url_destination
    #
    locations = []
    for resp in crawl.history:
        locations.append(resp.headers['Location'])
    crawl_details['glass_url_destination'] = locations[-1]


    # protocol_destination
    #
    check_https_url_dest = re.compile(r'^https:\/\/.*')
    if len(re.findall(check_https_url_dest, crawl_details['glass_url_destination'])) == 1:
        crawl_details['protocol_destination'] = "HTTPS"
    else:
        crawl_details['protocol_destination'] = "HTTP"


    # headers_count
    #
    crawl_details['headers_count'] = len(crawl.headers)


    # headers_bytes
    #
    header_bytes = 0
    for header, value in crawl.headers.iteritems():
        hstring = "%s: %s" % (header, value)
        header_bytes += len(hstring.encode('utf-8'))
    crawl_details['headers_bytes'] = header_bytes


    # response_bytes
    #
    crawl_details['response_bytes'] = len(crawl.text.encode('utf-8'))

    # done
    return crawl_details
