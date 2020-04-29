#!/usr/bin/python3

import sys
from synt import Synt
from errors import *

if __name__ == "__main__":
    error_handler = error_handler()
    #try:
    if str(sys.argv[1]).split(".")[-1] == "min":
        syn = Synt(str(sys.argv[1]))
    else:
        error_handler.error_handle(error_types.WrongFilePrefix, str(sys.argv[1]).split(".")[-1])
    #except IndexError:
        #error_handler.error_handle(error_types.FileArgument)
