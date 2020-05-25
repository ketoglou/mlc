#!/usr/bin/python3

#Usage:
#python3 mlc.py --help                      : Print help information
#python3 mlc.py -save-temps program.min     : Does not delete idermediate,array of symbols,C files
#python3 mlc.py program.min                 : Delete idermediate,array of symbols,C files

import sys
from synt import synt
from errors import *

if __name__ == "__main__":
    error_handler = error_handler()
    if len(sys.argv) > 1 :
        save_temps = False
        file_name = str(sys.argv[1])

        if str(sys.argv[1]) == "--help":
            print("minimal++ compiler")
            print("Usage:")
            print("python3 mlc.py --help                    : Print this information")
            print("python3 mlc.py -save-temps program.min   : Does not delete idermediate,array of symbols,C files")
            print("python3 mlc.py program.min               : Delete idermediate,array of symbols,C files")
            exit()
        if str(sys.argv[1]) == "-save-temps":
            save_temps = True
            file_name = str(sys.argv[2])

        if file_name.split(".")[-1] == "min":
            syn = synt(file_name, save_temps)
        else:
            error_handler.error_handle(error_types.WrongFilePrefix, str(sys.argv[1]).split(".")[-1])
    else:
        error_handler.error_handle(error_types.FileArgument)
