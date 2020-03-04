#!/usr/bin/python3

from enum import Enum

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class error_types(Enum):
    FileArgument = 0
    FileNotFound = 1
    UnexpectedEnd = 2
    UnexpectedChar = 3
    UnexpectedCommentEnd = 4

def error_handler(error_type, *args):
    if error_type == error_types.FileArgument:
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
              " File argument not passed!")
    elif error_type == error_types.FileNotFound:
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
              " File "+str(args[0])+" not found!")
    elif error_type == error_types.UnexpectedEnd:
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
              " Unexpected end at line "+str(args[0])+".")
    elif error_type == error_types.UnexpectedChar:
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
              " Unexpected character at line "+str(args[0])+".")
    elif error_type == error_types.UnexpectedCommentEnd:
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
              " Unexpected comment end at line "+str(args[0])+".")
    exit()

