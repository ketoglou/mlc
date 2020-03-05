#!/usr/bin/python3

import sys
from lex import Lex
from errors import file_lex_error_types,file_lex_error_handler
from finite_automata import State,automata_states
from synt import Synt

if __name__ == "__main__":
    try:
        syn = Synt(str(sys.argv[1]))
        syn.start()      
    except IndexError:
        file_lex_error_handler(file_lex_error_types.FileArgument)