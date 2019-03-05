#!/usr/bin/env python
# osgav
#

from disco import print_success, print_error, print_redir, print_fail

import requests
import time



def probe_glass(glass_url):
    '''
    request glass URL
    return a "crawl response"
    '''
    exception_status = None
    localtime = time.localtime()
    probe_timestamp = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)
    try:

        response = requests.get(glass_url)

        if len(response.history):
            print_redir()
        elif response.ok:
            print_success()
        else:
            print_error()

        return crawl_response("success", probe_timestamp, response)

    except requests.HTTPError as err:
        print_fail()
        exception_status = "HTTPERROR: %s" % err
        return crawl_response("exception", probe_timestamp, exception_status)
    except requests.Timeout as err:
        print_fail()
        exception_status = "TIMEOUT: %s" % err
        return crawl_response("exception", probe_timestamp, exception_status)
    except requests.ConnectionError as err:
        print_fail()
        exception_status = "CONNECTIONERROR: %s" % err
        return crawl_response("exception", probe_timestamp, exception_status)
    except Exception as err:
        print_fail()
        exception_status = "ERROR666: %s" % err
        return crawl_response("exception", probe_timestamp, exception_status)

def crawl_response(status, timestamp, message):
    return {
        "probe_result": status,
        "probe_timestamp": timestamp,
        "probe_message": message
    }
