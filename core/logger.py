#!/usr/bin/env python
# osgav
#

import time



def crawl_logger(glass_record, crawl_response):
    '''
    log raw response details 
    or exception message to a file
    '''
    if crawl_response['probe_result'] == "exception":
        log_exception_details(glass_record[0], glass_record[5], crawl_response)
    elif crawl_response['probe_result'] == "response":
        log_response_details(glass_record[0], glass_record[5], crawl_response)
    else:
        print("crawl_logger: unexpected probe_result: %s" % crawl_response['probe_result'])


def log_response_details(lgid, glass_url, crawl_response):
    '''
    write details to log file outside of database
    '''
    response_obj = crawl_response['message']
    time_string = crawl_response['probe_timestamp']

    with open("headers.log", "a") as logfile:
        logfile.write("=====================================================================\n")
        logfile.write("%s\nlgid: %s\nurl: %s\n" % (time_string, lgid, glass_url))
        logfile.write("status: %s\n\n" % str(response_obj.status_code))
        logfile.write("- - - - - - - - - -\n")
        
        for resp in response_obj.history:
            logfile.write("status code: %s\n" % resp.status_code)
            for header, value in resp.headers.iteritems():
                logfile.write("%s: %s\n" % (header, value))
            logfile.write("- - - - - - - - - -\n")

        logfile.write("status: %s\n" % response_obj.status_code)        
        for header, value in response_obj.headers.iteritems():
            logfile.write("%s: %s\n" % (header, value))
        logfile.write("\n\n")


def log_exception_details(lgid, glass_url, crawl_response):
    '''
    write exceptions to log file
    '''
    exception_obj = crawl_response['message']
    time_string = crawl_response['probe_timestamp']

    with open("exceptions.log", "a") as logfile:
        logfile.write("=====================================================================\n")
        logfile.write("%s\nlgid: %s\nurl: %s\n\n" % (time_string, lgid, glass_url))
        logfile.write("url: %s\n\n" % glass_url)
        logfile.write(str(exception_obj))
        logfile.write("\n\n")
