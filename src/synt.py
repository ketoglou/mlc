#!/usr/bin/python3

#IL:Intermediate Language Comment

from lex import Lex
from int_lang import IntLang
from finite_automata import Id,reserved_words
from errors import *

class Synt:

    def __init__(self, file_name):
        self.inLan = IntLang(file_name)
        self.error_handler = Error_handler(self.inLan)
        self.lex = Lex(file_name,self.error_handler)

    def start(self):
        self.program()
        self.inLan.close()

    def program(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("program", Id.IDENTIFIER,word, ID, self.lex.file_line)
        block_name, ID = self.lex.start_read()  # program name
        self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        self.block(block_name)

    def block(self,block_name):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("{", Id.GROUPING, word, ID, self.lex.file_line)
        self.inLan.make_list(block_name) #IL:Create a list for all the quads of this program(or procedure or function)
        self.declarations()
        self.subprograms()
        self.statements()
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("}", Id.GROUPING, word, ID, self.lex.file_line)
        self.inLan.write_list() #IL:Write the list of quads of this program(or procedure or function)

    def declarations(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("declare", Id.IDENTIFIER, word, ID):
            self.varlist()
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(";", Id.SEPERATOR, word,ID, self.lex.file_line)
            word, ID = self.lex.start_read()
            self.lex.undo_read()
            if self.error_handler.syntax_error("declare", Id.IDENTIFIER, word, ID):
                self.declarations()
            else:
                return
        else:
            self.lex.undo_read()

    def varlist(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error(";", Id.SEPERATOR, word, ID):
            self.lex.undo_read()
            return
        self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        while self.error_handler.syntax_error(",", Id.SEPERATOR, word, ID):
            word, ID = self.lex.start_read()  # variable in varlist
            self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        self.varlist()

    def subprograms(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("function", Id.IDENTIFIER, word, ID) or self.error_handler.syntax_error("procedure", Id.IDENTIFIER, word, ID):
            self.subprogram()
            self.subprograms()
        self.lex.undo_read()

    def subprogram(self):
        block_name, ID = self.lex.start_read()
        # Name of fuction or procedure
        self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        self.funcbody(block_name)

    def funcbody(self,block_name):
        self.formalpars()
        self.block(block_name)

    def formalpars(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)
        self.formalparlist()
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)

    def formalparlist(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.syntax_error(")", Id.GROUPING, word, ID):
            return
        self.formalparitem()
        word, ID = self.lex.start_read()
        while self.error_handler.syntax_error(",", Id.SEPERATOR, word, ID):
            self.formalparitem()
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        self.formalparlist()

    def formalparitem(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("in", Id.IDENTIFIER, word, ID) or self.error_handler.syntax_error("inout", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        else:
            self.error_handler.syntax_general_error("in or inout", word,
                                 self.lex.file_line)  # Error exit

    def statements(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("{", Id.GROUPING, word, ID):
            self.statement()
            word, ID = self.lex.start_read()
            while self.error_handler.syntax_error(";", Id.SEPERATOR, word, ID):
                self.statement()
                word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id("}", Id.GROUPING, word,ID, self.lex.file_line)
        else:
            self.lex.undo_read()
            self.statement()

    def statement(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if ID == Id.IDENTIFIER and word not in reserved_words:
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
            word, ID = self.lex.start_read()
            self.inLan.genquad("exit","_","_","_")
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
        assign, ID = self.lex.start_read()
        self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(":=", Id.EQUAL, word, ID, self.lex.file_line)
        x = self.expression()
        self.inLan.genquad(":=",x,"_",assign)

    def if_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("if", Id.IDENTIFIER, word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)

        if_cond_start_pos = self.inLan.relative_program_pos() #IL:starting position of if statement
        exp_list = self.condition(False) #IL:get the condition quads
        self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
        self.inLan.add_expression(exp_list,if_cond_start_pos) #IL:add the condition to the code
        if_cond_end_pos = self.inLan.relative_program_pos() #IL:starting position of if statement

        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("then", Id.IDENTIFIER, word,
                             ID, self.lex.file_line)

        self.statements()

        jump_false = self.inLan.relative_program_pos() - if_cond_end_pos + 1
        if self.elsepart():
            jump_false += 1
        self.inLan.backpatch(jump_false,if_cond_start_pos,if_cond_end_pos,"JUMP-FALSE")

    def elsepart(self):
        word, ID = self.lex.start_read()
        else_begin_pos = self.inLan.relative_program_pos() #IL:Get the begin address outside if statement
        #IL:If we have else outside if then we add a jump quad(for jump outside else if the if is true)
        #add add statements.Either we have else or not we return the position outside if.
        if self.error_handler.syntax_error("else", Id.IDENTIFIER, word, ID):
            self.inLan.genquad("jump","_","_","_") #IL:add jump at the end of if
            self.statements() #IL:add new statements inside else
            outside_if = self.inLan.relative_program_pos() - else_begin_pos #IL:calculate the relative position for the jump quad to jump
            self.inLan.programs_list[-1][else_begin_pos] = "jump,_,_,+"+str(outside_if) #IL:edit the jump quad and add the relative position
            return True
        else:
            self.lex.undo_read()
            return False

    def while_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("while", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)

        while_cond_start_pos = self.inLan.relative_program_pos() #IL:starting position of while statement
        exp_list = self.condition(False) #IL:get the condition quads
        self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
        self.inLan.add_expression(exp_list,while_cond_start_pos) #IL:add the condition to the code
        while_cond_end_pos = self.inLan.relative_program_pos() #IL:ending position of while statement 
         
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)

        self.statements()

        jump_false = self.inLan.relative_program_pos() - while_cond_end_pos + 2 #IL:get the position outside while
        self.inLan.genquad("jump","_","_","-"+str(jump_false))
        self.inLan.backpatch(jump_false,while_cond_start_pos,while_cond_end_pos,"JUMP-FALSE")


    #IL:doublewhile(condition).If the condition is true jump to the 1st statement else jump to the second.
    #After 1st statement copy the condition and change it so if it is true jump to the begin of 1st statement
    #if it is false jump to the end of 2nd statement.After 2nd statement copy the condition once again and 
    #change it so if it is true continue outside and if is false jump to the begin of 2nd statement.
    def doublewhile_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("doublewhile", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)
        
        start_pos_cond = self.inLan.relative_program_pos()
        cond = self.condition(False)
        end_pos_cond = self.inLan.relative_program_pos()
        first_cond = cond[:] #IL:use another instance because the original will be used again
        
        #Set jump_true for the forcase condition at the beginning and add the condition
        self.inLan.backpatch(first_cond,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
        self.inLan.add_expression(first_cond,start_pos_cond) #IL:add the condition to the code
        del first_cond  

        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)

        #1st statement
        start_pos_first_statement = self.inLan.relative_program_pos()
        self.statements()
        end_pos_first_statement = self.inLan.relative_program_pos()
        
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("else", Id.IDENTIFIER, word, ID, self.lex.file_line)

        #2nd statement
        start_pos_second_statement = self.inLan.relative_program_pos()
        self.statements()
        end_pos_second_statement = self.inLan.relative_program_pos()


    def loop_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("loop", Id.IDENTIFIER, word,
                             ID, self.lex.file_line)

        loop_start_pos = self.inLan.relative_program_pos()
        self.statements()
        loop_end_pos = self.inLan.relative_program_pos()
        jump_beginning = loop_end_pos - loop_start_pos
        self.inLan.genquad("jump","_","_","-"+str(jump_beginning))
        self.inLan.special_loop(loop_start_pos,loop_end_pos)

    def forcase_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("forcase", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()

        forcase_start_pos = self.inLan.relative_program_pos() #IL:Get the starting position of forcase

        while self.error_handler.syntax_error("when", Id.IDENTIFIER, word, ID):
            
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(
                "(", Id.GROUPING, word, ID, self.lex.file_line)

            cond_start_pos = self.inLan.relative_program_pos()
            exp_list = self.condition(False)
            self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
            self.inLan.add_expression(exp_list,cond_start_pos) #IL:add the condition to the code
            cond_end_pos = self.inLan.relative_program_pos() #IL:ending position of while statement 

            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(")", Id.GROUPING, word,
                                 ID, self.lex.file_line)
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(":", Id.SEPERATOR, word,
                                 ID, self.lex.file_line)

            self.statements()

            jump_to_begin = self.inLan.relative_program_pos() - forcase_start_pos #IL:positions from beginning of forcase
            self.inLan.genquad("jump","_","_","-"+str(jump_to_begin))
            jump_false = self.inLan.relative_program_pos() - cond_end_pos + 1
            self.inLan.backpatch(jump_false,cond_start_pos,cond_end_pos,"JUMP-FALSE")

            word, ID = self.lex.start_read()

        self.error_handler.syntax_error_word_id("default", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()   
        self.error_handler.syntax_error_word_id(":", Id.SEPERATOR,
                             word, ID, self.lex.file_line)             
        self.statements()

    def incase_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("incase", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        while self.error_handler.syntax_error("when", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(
                "(", Id.GROUPING, word, ID, self.lex.file_line)
            self.condition(False)
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(")", Id.GROUPING, word,
                                 ID, self.lex.file_line)
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(":", Id.SEPERATOR, word,
                                 ID, self.lex.file_line)
            self.statements()
            word, ID = self.lex.start_read()
        self.lex.undo_read()

    def return_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("return", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        x = self.expression()
        self.inLan.genquad("retv",x,"_","_")

    def call_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("call", Id.IDENTIFIER, word,
                             ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        self.actualpars()
        self.inLan.genquad("call",word,"_","_")

    def print_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("print", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)
        x = self.expression()
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)
        self.inLan.genquad("out",x,"_","_")

    def input_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("input", Id.IDENTIFIER,
                             word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
        self.inLan.genquad("inp",word,"_","_")
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)

    def actualpars(self):
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id("(", Id.GROUPING, word, ID, self.lex.file_line)
        self.actualparlist()
        word, ID = self.lex.start_read()
        self.error_handler.syntax_error_word_id(")", Id.GROUPING, word, ID, self.lex.file_line)

    def actualparlist(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.syntax_error(")", Id.GROUPING, word, ID):
            return
        self.actualparitem()
        word, ID = self.lex.start_read()
        while self.error_handler.syntax_error(",", Id.SEPERATOR, word, ID):
            self.actualparitem()
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        self.actualparlist()

    def actualparitem(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("in", Id.IDENTIFIER, word, ID):
            w = self.expression()
            self.inLan.genquad("par",w,"CV","_")
        elif self.error_handler.syntax_error("inout", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_id(Id.IDENTIFIER, ID, self.lex.file_line)
            self.inLan.genquad("par",word,"REF","_")
        else:
            self.error_handler.syntax_general_error("in or inout", word,
                                 self.lex.file_line)  # Error exit

    def condition(self,enable_not):
        Q = self.boolterm(enable_not)
        self.inLan.backpatch(Q,"_","true","RELOP")
        word, ID = self.lex.start_read()
        while self.error_handler.syntax_error("or", Id.IDENTIFIER, word, ID):
            self.inLan.backpatch(Q,"false","DISTANCE","JUMP")
            Q2 = self.boolterm(enable_not)
            Q = Q + Q2
            self.inLan.backpatch(Q,"_","true","RELOP")
            word, ID = self.lex.start_read()
        self.inLan.backpatch(Q,"false","DISTANCE","JUMP")
        Q.append("jump,_,_,false")
        self.lex.undo_read()
        return Q

    def boolterm(self,enable_not):
        R = self.boolfactor(enable_not)
        word, ID = self.lex.start_read()
        while self.error_handler.syntax_error("and", Id.IDENTIFIER, word, ID):
            R.append("jump,_,_,false")
            self.inLan.backpatch(R,"_","DISTANCE","RELOP")
            R2 = self.boolfactor(enable_not)
            R = R + R2
            word, ID = self.lex.start_read()
        self.lex.undo_read()
        return R

    def boolfactor(self,enable_not):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("not", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id("[", Id.GROUPING, word,
                                 ID, self.lex.file_line)
            new_expression = self.condition(True)
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id("]", Id.GROUPING, word,
                                 ID, self.lex.file_line)
            del new_expression[-1] #IL:delete last jump,_,_,false quad
            self.inLan.backpatch(new_expression,"true","_","RELOP") #IL:Change every relop,x,y,true quad to relop,x,y,_ quad
            return new_expression
        elif self.error_handler.syntax_error("[", Id.GROUPING, word, ID):
            new_expression = self.condition(False)
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id("]", Id.GROUPING, word,
                                 ID, self.lex.file_line)
            del new_expression[-1] #IL:delete last jump,_,_,false quad
            self.inLan.backpatch(new_expression,"true","_","RELOP") #IL:Change every relop,x,y,true quad to relop,x,y,_ quad
            return new_expression
        else:
            self.lex.undo_read()
            start_address = self.inLan.relative_program_pos()
            x = self.expression()
            relop = self.relational_oper()
            y = self.expression()
            if enable_not :
                self.inLan.genquad(self.inLan.reverse_relop(relop),x,y,"_")
            else:
                self.inLan.genquad(relop,x,y,"_")
            end_address = self.inLan.relative_program_pos()
            expression_list = self.inLan.get_expression(start_address,end_address)
            return expression_list

    def expression(self):
        sign = self.optional_sign()
        if sign == "-":
            x = sign + self.term()
        else:
            x = self.term()
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        w = None
        while self.error_handler.syntax_error("+", Id.OPERATOR, word, ID) or self.error_handler.syntax_error("-", Id.OPERATOR, word, ID):
            if w == None:
                w = self.inLan.newtemp()
                self.inLan.genquad(":=",x,"_",w)
            aop = self.add_oper()
            y = self.term()
            self.inLan.genquad(aop,w,y,w)
            word, ID = self.lex.start_read()
            self.lex.undo_read()
        self.inLan.reset_newtemp()
        if w is not None:
            return w
        return x

    def term(self):
        x = self.factor()
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        w = None
        while self.error_handler.syntax_error("*", Id.OPERATOR, word, ID) or self.error_handler.syntax_error("/", Id.OPERATOR, word, ID):
            if w == None:
                w = self.inLan.newtemp()
                self.inLan.genquad(":=",x,"_",w)
            mop = self.mul_oper()
            y = self.factor()
            self.inLan.genquad(mop,w,y,w)
            word, ID = self.lex.start_read()
            self.lex.undo_read()
        if w is not None:
            return w
        return x

    def factor(self):
        word, ID = self.lex.start_read()
        if ID == Id.NUMERICAL_CONSTANT:
            self.error_handler.syntax_int_error(word,self.lex.file_line)
            return word
        elif self.error_handler.syntax_error("(", Id.GROUPING, word, ID):
            x = self.expression()
            word, ID = self.lex.start_read()
            self.error_handler.syntax_error_word_id(")", Id.GROUPING, word,
                                 ID, self.lex.file_line)
            return x
        elif ID == Id.IDENTIFIER:
            if self.idtail() == True:
                w = self.inLan.newtemp()
                self.inLan.genquad("par",w,"RET","_")
                self.inLan.genquad("call",word,"_","_")
                word = w
            return word

    def idtail(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.syntax_error("(", Id.GROUPING, word, ID):
            self.actualpars()
            return True
        return False

    def relational_oper(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("=", Id.COMPARATOR, word, ID) or self.error_handler.syntax_error("<=", Id.COMPARATOR, word, ID) or self.error_handler.syntax_error(">=", Id.COMPARATOR, word, ID) or self.error_handler.syntax_error("<", Id.COMPARATOR, word, ID) or self.error_handler.syntax_error(">", Id.COMPARATOR, word, ID) or self.error_handler.syntax_error("<>", Id.COMPARATOR, word, ID):
            return word
        else:
            self.error_handler.syntax_general_error("= or <= or >= or < or > or <>", word, self.lex.file_line)

    def add_oper(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("+", Id.OPERATOR, word, ID) or self.error_handler.syntax_error("-", Id.OPERATOR, word, ID):
            return word
        else:
            self.error_handler.syntax_general_error("+ or -", word, self.lex.file_line)

    def mul_oper(self):
        word, ID = self.lex.start_read()
        if self.error_handler.syntax_error("*", Id.OPERATOR, word, ID) or self.error_handler.syntax_error("/", Id.OPERATOR, word, ID):
            return word
        else:
            self.error_handler.syntax_general_error("* or /", word, self.lex.file_line)

    def optional_sign(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.syntax_error("+", Id.OPERATOR, word, ID) or self.error_handler.syntax_error("-", Id.OPERATOR, word, ID):
            return self.add_oper()
        return None
