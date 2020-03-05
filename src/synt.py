#!/usr/bin/python3

from lex import Lex
from finite_automata import Id
from errors import syntax_error_word_id, syntax_error_id, syntax_error,syntax_general_error


class Synt:

    def __init__(self, file_name):
        self.lex = Lex(file_name)

    def start(self):
        self.program()

    def program(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("program",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read() #program name
        syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("{",Id.GROUPING,word,ID,self.lex.file_line)
        self.block()
        word,ID = self.lex.start_read()
        syntax_error_word_id("}",Id.GROUPING,word,ID,self.lex.file_line)

    def block(self):
        self.declarations()
        self.subprograms()
        self.statements()

    def declarations(self):
        word,ID = self.lex.start_read()
        if syntax_error("declare",Id.IDENTIFIER,word,ID):
            self.varlist()
            word,ID = self.lex.start_read()
            syntax_error_word_id(";",Id.SEPERATOR,word,ID,self.lex.file_line)
            word,ID = self.lex.start_read()
            self.lex.undo_read()
            if syntax_error("declare",Id.IDENTIFIER,word,ID):
                self.declarations()
            else:
                return
        else:
            self.lex.undo_read()

    def varlist(self):
        word,ID = self.lex.start_read()
        if syntax_error(";",Id.SEPERATOR,word,ID):
            self.lex.undo_read()
            return
        syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        while syntax_error(",",Id.SEPERATOR,word,ID):
            word,ID = self.lex.start_read() #variable in varlist
            syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
            word,ID = self.lex.start_read() # expected comma
        self.lex.undo_read()
        self.varlist()

    def subprograms(self):
        word,ID = self.lex.start_read()
        if syntax_error("function",Id.IDENTIFIER,word,ID) or syntax_error("procedure",Id.IDENTIFIER,word,ID):
            self.subprogram()
            self.subprograms()
        self.lex.undo_read()

    def subprogram(self):
        word,ID = self.lex.start_read()
        syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line) #Name of fuction or procedure
        self.funcbody()

    def funcbody(self):
        self.formalpars()
        word,ID = self.lex.start_read()
        syntax_error_word_id("{",Id.GROUPING,word,ID,self.lex.file_line)
        self.block()
        word,ID = self.lex.start_read()
        syntax_error_word_id("}",Id.GROUPING,word,ID,self.lex.file_line)

    def formalpars(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        self.formalparlist()
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)

    def formalparlist(self):
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        if syntax_error(")",Id.SEPERATOR,word,ID):
            return
        self.formalparitem()
        word,ID = self.lex.start_read()
        while syntax_error(",",Id.SEPERATOR,word,ID):
            self.formalparitem()
            word,ID = self.lex.start_read() # expected comma
        self.lex.undo_read()
        self.formalparlist()

    def formalparitem(self):
        word,ID = self.lex.start_read()
        if syntax_error("in",Id.IDENTIFIER,word,ID) or syntax_error("inout",Id.IDENTIFIER,word,ID):
            word,ID = self.lex.start_read()
            syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        else:
            syntax_general_error("in or inout",word,self.lex.file_line) #Error exit

    def statements(self):
        word,ID = self.lex.start_read()
        if syntax_error("{",Id.GROUPING,word,ID):
            self.statement()
            word,ID = self.lex.start_read()
            while syntax_error(";",Id.SEPERATOR,word,ID):
                self.statement()
                word,ID = self.lex.start_read()
            syntax_error_word_id("}",Id.GROUPING,word,ID,self.lex.file_line)
        else:
            self.lex.undo_read()
            self.statement()

    def statement(self):
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        if ID == Id.IDENTIFIER:
            self.assignment_stat()
        elif word == "if":
            self.if_stat()
        elif word == "while":
            self.while_stat()
        elif word == "doublewhile":
            self.doublewhile_stat()
        elif word == "loop":
            self.loop_stat()
        elif word == "exit":
            return
        elif word == "forcase":
            self.forcase_stat()
        elif word == "incase":
            self.incase_stat()
        elif word == "call":
            self.call_stat()
        elif word == "return":
            self.return_stat()
        elif word == "input":
            self.input_stat()
        elif word == "print":
            self.print_stat()

    def assignment_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id(":=",Id.EQUAL,word,ID,self.lex.file_line)
        self.expression()

    def if_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("if",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        self.condition()
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("then",Id.IDENTIFIER,word,ID,self.lex.file_line)
        self.statements()
        self.elsepart()

    def elsepart(self):
        word,ID = self.lex.start_read()
        if syntax_error("else",Id.IDENTIFIER,word,ID):
            self.statements()
        else:
            self.lex.undo_read()
    
    def while_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("while",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        self.condition()
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)
        self.statements()

    def doublewhile_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("doublewhile",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        self.condition()
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)
        self.statements()
        word,ID = self.lex.start_read()
        syntax_error_word_id("else",Id.GROUPING,word,ID,self.lex.file_line)
        self.statements()

    def loop_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("loop",Id.IDENTIFIER,word,ID,self.lex.file_line)
        self.statements()

    def forcase_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("forcase",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        while syntax_error("when",Id.IDENTIFIER,word,ID):
            word,ID = self.lex.start_read()
            syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
            self.condition()
            word,ID = self.lex.start_read()
            syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)
            word,ID = self.lex.start_read()
            syntax_error_word_id(":",Id.SEPERATOR,word,ID,self.lex.file_line)
            self.statements()
            word,ID = self.lex.start_read()
        self.lex.undo_read()
        syntax_error_word_id("default:",Id.IDENTIFIER,word,ID,self.lex.file_line)
        self.statements()

    def incase_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("incase",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        while syntax_error("when",Id.IDENTIFIER,word,ID):
            word,ID = self.lex.start_read()
            syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
            self.condition()
            word,ID = self.lex.start_read()
            syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)
            word,ID = self.lex.start_read()
            syntax_error_word_id(":",Id.SEPERATOR,word,ID,self.lex.file_line)
            self.statements()
            word,ID = self.lex.start_read()
        self.lex.undo_read()

    def return_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("return",Id.IDENTIFIER,word,ID,self.lex.file_line)
        self.expression()

    def call_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("call",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        self.actualpars()

    def print_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("print",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        self.expression()
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)

    def input_stat(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("input",Id.IDENTIFIER,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)

    def actualpars(self):
        word,ID = self.lex.start_read()
        syntax_error_word_id("(",Id.GROUPING,word,ID,self.lex.file_line)
        self.actualparlist()
        word,ID = self.lex.start_read()
        syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)

    def actualparlist(self):
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        if syntax_error(")",Id.SEPERATOR,word,ID):
            return
        self.actualparitem()
        word,ID = self.lex.start_read()
        while syntax_error(",",Id.SEPERATOR,word,ID):
            self.actualparitem()
            word,ID = self.lex.start_read() # expected comma
        self.lex.undo_read()
        self.actualparlist()

    def actualparitem(self):
        word,ID = self.lex.start_read()
        if syntax_error("in",Id.IDENTIFIER,word,ID,self.lex.file_line):
            self.expression()
        elif syntax_error("inout",Id.IDENTIFIER,word,ID,self.lex.file_line):
            word,ID = self.lex.start_read()
            syntax_error_id(Id.IDENTIFIER,ID,self.lex.file_line)
        else:
            syntax_general_error("in or inout",word,self.lex.file_line) #Error exit

    def condition(self):
        self.boolterm()
        word,ID = self.lex.start_read()
        while syntax_error("or",Id.IDENTIFIER,word,ID,self.lex.file_line):
            self.boolterm()
            word,ID = self.lex.start_read()
        self.lex.undo_read()

    def boolterm(self):
        self.boolfactor()
        word,ID = self.lex.start_read()
        while syntax_error("and",Id.IDENTIFIER,word,ID,self.lex.file_line):
            self.boolfactor()
            word,ID = self.lex.start_read()
        self.lex.undo_read()

    def boolfactor(self):
        word,ID = self.lex.start_read()
        if syntax_error("not",Id.IDENTIFIER,word,ID,self.lex.file_line):
            word,ID = self.lex.start_read()
            syntax_error_word_id("[",Id.GROUPING,word,ID,self.lex.file_line)
            self.condition()
            word,ID = self.lex.start_read()
            syntax_error_word_id("]",Id.GROUPING,word,ID,self.lex.file_line)
        elif syntax_error("[",Id.GROUPING,word,ID,self.lex.file_line):
            self.condition()
            word,ID = self.lex.start_read()
            syntax_error_word_id("]",Id.GROUPING,word,ID,self.lex.file_line)
        else:
            self.expression()
            self.relational_oper()
            self.expression()

    def expression(self):
        self.optional_sign()
        self.term()
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        while syntax_error("+",Id.OPERATOR,word,ID,self.lex.file_line) or syntax_error("-",Id.OPERATOR,word,ID,self.lex.file_line):
            self.add_oper()
            self.term()
            word,ID = self.lex.start_read()
            self.lex.undo_read()

    def term(self):
        self.factor()
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        while syntax_error("*",Id.OPERATOR,word,ID,self.lex.file_line) or syntax_error("/",Id.OPERATOR,word,ID,self.lex.file_line):
            self.mul_oper()
            self.factor()
            word,ID = self.lex.start_read()
            self.lex.undo_read()

    def factor(self):
        word,ID = self.lex.start_read()
        if ID == Id.NUMERICAL_CONSTANT:
            return
        elif syntax_error("(",Id.GROUPING,word,ID):
            self.expression()
            word,ID = self.lex.start_read()
            syntax_error_word_id(")",Id.GROUPING,word,ID,self.lex.file_line)
        elif ID == Id.IDENTIFIER:
            self.idtail()

    def idtail(self):
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        if syntax_error("(",Id.GROUPING,word,ID):
            self.actualpars()

    def relational_oper(self):
        word,ID = self.lex.start_read()
        if syntax_error("=",Id.GROUPING,word,ID) or syntax_error("<=",Id.GROUPING,word,ID) or syntax_error(">=",Id.GROUPING,word,ID) or syntax_error("<",Id.GROUPING,word,ID) or syntax_error(">",Id.GROUPING,word,ID) or syntax_error("<>",Id.GROUPING,word,ID):
            return
        else:
            syntax_general_error("= or <= or >= or < or > or <>",word,self.lex.file_line)


    def add_oper(self):
        word,ID = self.lex.start_read()
        if syntax_error("+",Id.GROUPING,word,ID) or syntax_error("-",Id.GROUPING,word,ID):
            return
        else:
            syntax_general_error("+ or -",word,self.lex.file_line)

    def mul_oper(self):
        word,ID = self.lex.start_read()
        if syntax_error("*",Id.GROUPING,word,ID) or syntax_error("/",Id.GROUPING,word,ID):
            return
        else:
            syntax_general_error("* or /",word,self.lex.file_line)

    def optional_sign(self):
        word,ID = self.lex.start_read()
        self.lex.undo_read()
        if syntax_error("+",Id.OPERATOR,word,ID) or syntax_error("-",Id.OPERATOR,word,ID):
            self.add_oper()
