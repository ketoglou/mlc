#!/usr/bin/python3

from lex import Lex

class Synt:
    
    def __init__(self, file_name):
        self.lex_ = Lex(file_name)
        self.program()

    def program(self):
        