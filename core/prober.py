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

        probe_result = "success"
        probe_message = response

    except requests.HTTPError as err:
        print_fail()
        probe_result = "exception"
        probe_message = "HTTPERROR: %s" % err

    except requests.Timeout as err:
        print_fail()
        probe_result = "exception"
        probe_message = "TIMEOUT: %s" % err

    except requests.ConnectionError as err:
        print_fail()
        probe_result = "exception"
        probe_message = "CONNECTIONERROR: %s" % err

    except Exception as err:
        print_fail()
        probe_result = "exception"
        probe_message = "ERROR666: %s" % err

    finally:
        return crawl_response(probe_result, probe_timestamp, probe_message)


def crawl_response(status, timestamp, message):
    return {
        "probe_result": status,
        "probe_timestamp": timestamp,
        "probe_message": message
    }
