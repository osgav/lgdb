#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_success, print_error, print_redir, print_fail, print_dbf
from db import select_one_glass, \
               update_one_glass_detail, \
               update_one_glass_last_changed, \
               update_one_glass_last_checked

import re
import time




def crawl_parser(scrape_database, glass_record, crawl_response):
    '''
    parse "crawl responses" into scrape database
    '''
    if crawl_response['probe_result'] == "exception":
        pass
        # exception = crawl_response['message']
        # exception_name = exception.split(":")[0]
        #
        # hmm probably better to not repeat previous logic and
        # log made up exception name into the subset
        # of columns updated by a crawl...
        #
        # add a column last_check_status ?
        # populate with 'success' or 'exception: <details>' ?
        #

    else:
        crawl = crawl_response['message']
        details_from_crawl = get_crawl_details(glass_record, crawl)
        details_from_db_raw = select_one_glass(scrape_database, glass_record[0])  # magic number for lgid
        details_from_db = mapdbobject(details_from_db_raw)

        # if crawl data differs from data in db, update the db
        for crawl_detail, crawl_value in details_from_crawl.iteritems():

            try:
                data_from_crawl = str(crawl_value).encode('utf-8')
                data_from_db = str(details_from_db[crawl_detail]).encode('utf-8')

                if data_from_crawl != data_from_db:
                    update_one_glass_detail(scrape_database, glass_record, crawl_detail, crawl_value)
                    update_one_glass_last_changed(scrape_database, glass_record, crawl_response['probe_timestamp'])

                update_one_glass_last_checked(scrape_database, glass_record, crawl_response['probe_timestamp'])

            except Exception as err:
                print_dbf()
                print("crawl_parser: error comparing / updating the database: %s" % err)


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
    check_https = re.compile(r'^https:\/\/.*')
    url = glass_record[5]  # magic number for glass_url_source
    if len(re.findall(check_https, url)) == 1:
        crawl_details['protocol_source'] = "HTTPS"
    else:
        crawl_details['protocol_source'] = "HTTP"

    # https_status
    crawl_details['http_status'] = crawl.status_code

    # is_redirects
    if len(crawl.history):
        crawl_details['is_redirect'] = "True"
    else:
        crawl_details['is_redirect'] = "False"

    # glass_url_destination
    if not len(crawl.history):
        crawl_details['glass_url_destination'] = crawl.url
    else:
        locations = []
        for resp in crawl.history:
            locations.append(resp.headers['Location'])
        crawl_details['glass_url_destination'] = locations[-1]

    # protocol_destination
    url = crawl_details['glass_url_destination']
    if len(re.findall(check_https, url)) == 1:
        crawl_details['protocol_destination'] = "HTTPS"
    else:
        crawl_details['protocol_destination'] = "HTTP"

    # headers_count
    crawl_details['headers_count'] = len(crawl.headers)

    # headers_bytes
    header_bytes = 0
    for header, value in crawl.headers.iteritems():
        hstring = "%s: %s" % (header, value)
        header_bytes += len(hstring.encode('utf-8'))
    crawl_details['headers_bytes'] = header_bytes

    # response_bytes
    crawl_details['response_bytes'] = len(crawl.text.encode('utf-8'))

    # done
    return crawl_details
