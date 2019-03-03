#!/usr/bin/env python
# osgav
#

from disco import print_success, print_error, print_redir, print_fail

import requests




def probe_glass(glass_url):
    '''
    request glass URL
    '''

    # request the glass url!
    exception_status = None
    # localtime = time.localtime()
    # last_updated = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)
    try:
        response = requests.get(glass_url)
        # log_response_details(lgid, glass_url, response)

        # progress meter for visual tracking
        if len(response.history):
            print_redir()

            # locations = []
            # for resp in response.history:
            #     locations.append(resp.headers['Location'])

            # # GET PROBE DETAILS
            # probe_details['glass_url_destination'] = locations[-1]

            # check_https_url_dest = re.compile(r'^https:\/\/.*')
            # if len(re.findall(check_https_url_dest, probe_details['glass_url_destination'])) == 1:
            #     probe_details['protocol_destination'] = "HTTPS"
            # else:
            #     probe_details['protocol_destination'] = "HTTP"

        elif response.ok:
            print_success()
        else:
            print_error()

        # GET PROBE DETAILS
        # probe_details['http_status'] = response.status_code
        # if len(response.history):
        #     probe_details['is_redirect'] = "True"
        # else:
        #     probe_details['is_redirect'] = "False"

        # GET PROBE DETAILS
        # header_bytes = 0
        # for header, value in response.headers.iteritems():
        #     hstring = "%s: %s" % (header, value)
        #     header_bytes += len(hstring.encode('utf-8'))
        # probe_details['headers_bytes'] = header_bytes
        # probe_details['headers_count'] = len(response.headers)
        # probe_details['response_bytes'] = len(response.text.encode('utf-8'))

    except requests.HTTPError as err:
        print_fail()
        # log_exception_details(glass_url, err)
        exception_status = "HTTPERROR"
    except requests.Timeout as err:
        print_fail()
        # log_exception_details(glass_url, err)
        exception_status = "TIMEOUT"
    except requests.ConnectionError as err:
        print_fail()
        # log_exception_details(glass_url, err)
        exception_status = "CONNECTIONERROR"
    except:
        print_fail()
        # log_exception_details(glass_url, "something terrible seems to have happened")
        exception_status = "ERROR 666"
    
    finally:
        if exception_status:
            return {"probe_result": "exception", "message": exception_status}
        else:
            return {"probe_result": "response", "message": response}