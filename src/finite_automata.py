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
    EQUAL_OR_SEPERATOR = 9
    COMMENT_OR_DIVISION = 10
    COMMENT_ONE_LINE = 11
    COMMENT_MULTIPLE_LINES = 12
    COMMENT_MULTIPLE_LINES_END = 13
    FINAL = 14
    FINAL_BLANK = 15
    FINAL_COMMENT = 16


class Symbols:
    LETTERS = set(string.ascii_letters)
    NUMBERS = set(string.digits)
    OPERATORS = {"+", "-", "*", "/"}
    COMPARATORS = {"<", ">", "="}
    SEPERATORS = {";", ",", ":"}
    GROUPING = {"(", ")", "[", "]", "{", "}"}
    BLANKS = {" ", "\t", "\n"}
    ALL = LETTERS.union(NUMBERS).union(OPERATORS).union(
        COMPARATORS).union(SEPERATORS).union(GROUPING).union(BLANKS)


class Id(Enum):
    OPERATOR = 0
    COMPARATOR = 1
    GROUPING = 2
    SEPERATOR = 3
    IDENTIFIER = 4
    NUMERICAL_CONSTANT = 5
    EQUAL = 6
    COMMENT = 7


automata_states = {
    State.INITIAL: [
        {
            'next_state': State.INITIAL,
            'condition': Symbols.BLANKS,
            'go_back': False
        },
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
            'go_back': False,
            'id': Id.OPERATOR
        },
        {
            'next_state': State.FINAL,
            'condition': "-",
            'go_back': False,
            'id': Id.OPERATOR
        },
        {
            'next_state': State.FINAL,
            'condition': "*",
            'go_back': False,
            'id': Id.OPERATOR
        },
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.FINAL,
            'condition': "(",
            'go_back': False,
            'id': Id.GROUPING
        },
        {
            'next_state': State.FINAL,
            'condition': ")",
            'go_back': False,
            'id': Id.GROUPING
        },
        {
            'next_state': State.FINAL,
            'condition': "[",
            'go_back': False,
            'id': Id.GROUPING

        },
        {
            'next_state': State.FINAL,
            'condition': "]",
            'go_back': False,
            'id': Id.GROUPING
        },
        {
            'next_state': State.FINAL,
            'condition': "{",
            'go_back': False,
            'id': Id.GROUPING
        },
        {
            'next_state': State.FINAL,
            'condition': "}",
            'go_back': False,
            'id': Id.GROUPING
        },
        {
            'next_state': State.LESS_THAN,
            'condition': "<",
            'go_back': False,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.GREATER_THAN,
            'condition': ">",
            'go_back': False,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.EQUAL_OR_SEPERATOR,
            'condition': ":",
            'go_back': False,
            'id': Id.SEPERATOR
        },
        {
            'next_state': State.COMMENT_OR_DIVISION,
            'condition': "/",
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': ",",
            'go_back': False,
            'id': Id.SEPERATOR
        },
        {
            'next_state': State.FINAL,
            'condition': ";",
            'go_back': False,
            'id': Id.SEPERATOR
        }
    ],
    State.IDENTIFIER: [
        {
            'next_state': State.IDENTIFIER,
            'condition': Symbols.LETTERS.union(Symbols.NUMBERS),  # a-z,A-Z,0-9
            'go_back': False
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL-Symbols.BLANKS-Symbols.LETTERS-Symbols.NUMBERS,
            'go_back': True,
            'id': Id.IDENTIFIER
        },
        {
            'next_state': State.FINAL_BLANK,
            'condition': Symbols.BLANKS,
            'go_back': False,
            'id': Id.IDENTIFIER
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
            'condition': Symbols.ALL-Symbols.NUMBERS-Symbols.BLANKS,
            'go_back': True,
            'id': Id.NUMERICAL_CONSTANT
        },
        {
            'next_state': State.FINAL_BLANK,
            'condition': Symbols.BLANKS,
            'go_back': False,
            'id': Id.NUMERICAL_CONSTANT
        }
    ],
    State.LESS_THAN: [
        {
            'next_state': State.FINAL,
            'condition': ">",
            'go_back': False,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL-Symbols.BLANKS-({">", "="}),
            'go_back': True,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.FINAL_BLANK,
            'condition': Symbols.BLANKS,
            'go_back': False,
            'id': Id.COMPARATOR
        }

    ],
    State.GREATER_THAN: [
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL-Symbols.BLANKS-{"="},
            'go_back': True,
            'id': Id.COMPARATOR
        },
        {
            'next_state': State.FINAL_BLANK,
            'condition': Symbols.BLANKS,
            'go_back': False,
            'id': Id.COMPARATOR
        }
    ],
    State.EQUAL_OR_SEPERATOR: [
        {
            'next_state': State.FINAL,
            'condition': "=",
            'go_back': False,
            'id': Id.EQUAL
        },
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL-{"="},
            'go_back': True,
            'id': Id.SEPERATOR
        }
    ],
    State.COMMENT_OR_DIVISION: [
        {
            'next_state': State.FINAL,
            'condition': Symbols.ALL-Symbols.BLANKS-({"/", "*"}),  # DIVISION
            'go_back': True,
            'id': Id.OPERATOR
        },
        {
            'next_state': State.COMMENT_ONE_LINE,
            'condition': "/",  # COMMENT ONE LINE
            'go_back': False
        },
        {
            'next_state': State.COMMENT_MULTIPLE_LINES,
            'condition': "*",  # COMMENT MULTIPLE LINES
            'go_back': False
        },
        {
            'next_state': State.FINAL_BLANK,
            'condition': Symbols.BLANKS,
            'go_back': False,
            'id': Id.OPERATOR
        }
    ],
    State.COMMENT_ONE_LINE: [
        {
            'next_state': State.FINAL_COMMENT,
            'condition': {"\n", ""},
            'go_back': False,
            'id': Id.COMMENT
        },
        {
            'next_state': State.COMMENT_ONE_LINE,
            'condition': Symbols.ALL-({"\n", ""}),
            'go_back': False
        }
    ],
    State.COMMENT_MULTIPLE_LINES: [
        {
            'next_state': State.COMMENT_MULTIPLE_LINES_END,
            'condition': "*",
            'go_back': False
        },
        {
            'next_state': State.COMMENT_MULTIPLE_LINES,
            'condition': Symbols.ALL-{"*"},
            'go_back': False
        }
    ],
    State.COMMENT_MULTIPLE_LINES_END: [
        {
            'next_state': State.FINAL_COMMENT,
            'condition': "/",
            'go_back': False,
            'id': Id.COMMENT
        },
        {
            'next_state': State.COMMENT_MULTIPLE_LINES,
            'condition': Symbols.ALL-{"/"},
            'go_back': False
        }
    ]
}

reserved_words = {"program", "declare", "if", "else", "while", "doublewhile", "loop", "exit", "forcase", "incase",
                 "when", "default", "not", "and", "or", "function", "procedure", "call", "return", "in", "inout", "input", "print"}
