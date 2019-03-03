#!/usr/bin/env python
# osgav
#

import time




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