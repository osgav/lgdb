#!/usr/bin/env python
# osgav
#

from disco import clrprint, print_success, print_error, print_redir, print_fail, print_dbf

import re
import time




# --crawl Part II (subroutine)
#
def scrape_parser(glass, crawl_response):
    '''
    collect crawl data for database
    '''

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
    # exception_status = None
    localtime = time.localtime()
    last_updated = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)
    try:
        # response = requests.get(glass_url)
        # log_response_details(lgid, glass_url, response)

        # progress meter for visual tracking
        if len(response.history):
            # print_redir()

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

        # elif response.ok:
            # print_success()
        # else:
            # print_error()

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

    # except requests.HTTPError as err:
    #     print_fail()
    #     log_exception_details(glass_url, err)
    #     exception_status = "HTTPERROR"
    # except requests.Timeout as err:
    #     print_fail()
    #     log_exception_details(glass_url, err)
    #     exception_status = "TIMEOUT"
    # except requests.ConnectionError as err:
    #     print_fail()
    #     log_exception_details(glass_url, err)
    #     exception_status = "CONNECTIONERROR"
    except:
        print_fail()
        # log_exception_details(glass_url, "something terrible seems to have happened")
        exception_status = "ERROR 666"

    if exception_status is not None:
        probe_details['glass_url_destination'] = exception_status
        probe_details['protocol_destination'] = exception_status
        probe_details['http_status'] = exception_status
        probe_details['is_redirect'] = exception_status
        probe_details['headers_bytes'] = exception_status
        probe_details['headers_count'] = exception_status
        probe_details['response_bytes'] = exception_status

    # return probe_details, last_updated