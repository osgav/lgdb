#!/usr/bin/env python
# osgav
#

from disco import print_success, print_error, print_redir, print_fail

import requests
import time



def probe_glass(glass_url):
    '''
    request glass URL
    '''
    exception_status = None
    try:

        localtime = time.localtime()
        probe_timestamp = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)

        response = requests.get(glass_url)

        if len(response.history):
            print_redir()
        elif response.ok:
            print_success()
        else:
            print_error()

    except requests.HTTPError as err:
        print_fail()
        exception_status = "HTTPERROR: %s" % err
    except requests.Timeout as err:
        print_fail()
        exception_status = "TIMEOUT: %s" % err
    except requests.ConnectionError as err:
        print_fail()
        exception_status = "CONNECTIONERROR: %s" % err
    except Exception as err:
        print_fail()
        exception_status = "ERROR 666: %s" % err

    finally:
        if exception_status:
            return {
                "probe_result": "exception",
                "probe_timestamp": probe_timestamp,
                "message": exception_status
            }
        else:
            return {
                "probe_result": "response",
                "probe_timestamp": probe_timestamp,
                "message": response
            }
