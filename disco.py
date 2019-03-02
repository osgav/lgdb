#!/usr/bin/env python
'''colourprint function'''

# osgav
# 03 March 2018

from __future__ import print_function

# class clr:
#     '''colourzzz'''
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     GREEN = '\033[32m'
#     BBG = '\033[40m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'

# def clrprint(colour, message):
#     '''print colourful words'''
#     print(eval("clr." + colour) + clr.BOLD + message + clr.ENDC)



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



