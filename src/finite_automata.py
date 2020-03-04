#!/usr/bin/python3

import string
from enum import Enum


class State(Enum):
    INITIAL = 0
    IDENTIFIER = 1
    NUMERICAL_CONSTANT = 2
    OPERATOR = 3
    COMPERATOR = 4
    ASSIGN = 5
    SEPERATOR = 6
    LESS_THAN = 7
    GREATER_THAN = 8
    EQUAL = 9
    COMMENT_OR_DIVISION = 10
    COMMENT_ONE_LINE = 11
    COMMENT_MULTIPLE_LINES = 12
    COMMENT_MULTIPLE_LINES_END = 13
    FINAL = 14
    ERROR = 15


class Symbols:
    LETTERS = set(string.ascii_letters)
    NUMBERS = set(string.digits)
    OPERATORS = {"+", "-", "*", "/"}
    COMPARATORS = {"<", ">", "="}
    ASSIGN = {":"}
    SEPERATORS = {";", ","}
    GROUPING = {"(", ")", "[", "]", "{", "}"}
    ALL = LETTERS.union(NUMBERS).union(OPERATORS).union(
        COMPARATORS).union(ASSIGN).union(SEPERATORS).union(GROUPING)


automata_states = {
    State.INITIAL: [
        {
            'next_state': State.IDENTIFIER,
            'condition': Symbols.LETTERS,  # a-z,A-Z
            'go_back': False
        },
        {
            'next_state': State.NUMERICAL_CONSTANT,
            'condition': Symbols.NUMBERS,  # 0-9
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "+",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "-",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "*",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "(",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': ")",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "[",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "]",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "{",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "}",
            'go_back': False
        },
        {
            'next_state': State.LESS_THAN,
            'condition': "<",
            'go_back': False
        },
        {
            'next_state': State.GREATER_THAN,
            'condition': ">",
            'go_back': False
        },
        {
            'next_state': State.EQUAL,
            'condition': ":",
            'go_back': False
        },
        {
            'next_state': State.COMMENT_OR_DIVISION,
            'condition': "/",
            'go_back': False
        },
    ],
    State.IDENTIFIER: [
        {
            'next_state': State.IDENTIFIER,
            'condition': Symbols.LETTERS.union(Symbols.NUMBERS),  # a-z,A-Z,0-9
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL.intersection(Symbols.LETTERS.union(Symbols.NUMBERS)),
            'go_back': True
        }
    ],
    State.NUMERICAL_CONSTANT: [
        {
            'next_state': State.NUMERICAL_CONSTANT,
            'condition': Symbols.NUMBERS,  # 0-9
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL.intersection(Symbols.NUMBERS),
            'go_back': True
        }
    ],
    State.LESS_THAN: [
        {
            'next_state': State.FINAL,
            'condition': ">",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL.intersection({">","="}),
            'go_back': True
        }

    ],
    State.GREATER_THAN: [
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL.intersection("="),
            'go_back': True
        }
    ],
    State.EQUAL: [
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False
        },
        {
            'next_state': State.ERROR,
            'condition': Symbols.ALL.intersection("="),
            'go_back': True
        }
    ],
    State.COMMENT_OR_DIVISION:[
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL.intersection({"/","*"}), #DIVISION
            'go_back': True
        },
        {
            'next_state': State.COMMENT_ONE_LINE,
            'condition': "/",   #COMMENT ONE LINE
            'go_back': False
        },
        {
            'next_state': State.COMMENT_MULTIPLE_LINES,
            'condition': "*",   #COMMENT MULTIPLE LINES
            'go_back': False
        }
    ],
    State.COMMENT_ONE_LINE:[
        {
            'next_state': State.FINAL,
            'condition': {"/n",""},
            'go_back': False
        }
    ],
    State.COMMENT_MULTIPLE_LINES: [
        {
            'next_state': State.COMMENT_MULTIPLE_LINES_END,
            'condition': "*",
            'go_back': False
        }
    ],
    State.COMMENT_MULTIPLE_LINES_END: [
        {
            'next_state': State.FINAL,
            'condition': "/",
            'go_back': False
        }
    ]
}
