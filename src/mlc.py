#!/usr/bin/python3

import sys
from lex import Lex
from errors import file_lex_error_types,file_lex_error_handler
from finite_automata import State,automata_states

if __name__ == "__main__":
    try:
        lex = Lex(str(sys.argv[1]))
        c=lex.start_automata()
        print(c)
        while c != None:
            c=lex.start_automata()
            if c != None:
                print(c)
    except IndexError:
        file_lex_error_handler(file_lex_error_types.FileArgument)