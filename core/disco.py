#!/usr/bin/env python
# osgav
#

from __future__ import print_function
import sys
import time




clrz = {}
clrz['HEADER'] = '\033[95m'
clrz['OKBLUE'] = '\033[94m'
clrz['OKGREEN'] = '\033[92m'
clrz['GREEN'] = '\033[32m'
clrz['BBG'] = '\033[40m'
clrz['WARNING'] = '\033[93m'
clrz['FAIL'] = '\033[91m'
clrz['ENDC'] = '\033[0m'
clrz['BOLD'] = '\033[1m'
clrz['UNDERLINE'] = '\033[4m'

def clrprint(colour, message):
    '''print colourful words'''
    print(eval("clrz['" + colour + "']") + clrz['BOLD'] + message + clrz['ENDC'])


# progress meter functions
#
def print_success():
    '''print a green thing'''
    print(clrz['BBG'] + clrz['GREEN'] +"[+]"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_error():
    '''print a red thing'''
    print(clrz['BBG'] + clrz['FAIL'] +"[-]"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_redir():
    '''print a yellow thing'''
    print(clrz['BBG'] + clrz['WARNING'] +"[-]"+ clrz['ENDC'], end="")
    sys.stdout.flush()  

def print_fail():
    '''print fail'''
    print(clrz['BBG'] + clrz['FAIL'] +"fail"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_dbf():
    '''print database fail'''
    print(clrz['BBG'] + clrz['FAIL'] +"database fail"+ clrz['ENDC'], end="")
    sys.stdout.flush()

def print_purple():
    '''print a purple thing'''
    print(clrz['HEADER'] +"*"+ clrz['ENDC'], end="")
    sys.stdout.flush()
    time.sleep(0.01)
