#!/usr/bin/python3

import sys
from lex import Lex
from finite_automata import State,automata_states
from synt import Synt
from int_lang import IntLang


if __name__ == "__main__":
    try:
        if str(sys.argv[1]).split(".")[-1] == "min":
            syn = Synt(str(sys.argv[1]))
        else:
            syn.error_handler.error_message("wrong file prefix expected: .min but find:" + str(sys.argv[1]).split(".")[-1])
    except IndexError:
        syn.error_handler.file_lex_error_handler(syn.error_handler.file_lex_error_types.FileArgument)
