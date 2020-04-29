#!/usr/bin/python3

#IL:Intermediate Language Comment

from lex import Lex
from int_lang import IntLang
from create_c_code import CreateC
from finite_automata import Id,reserved_words
from errors import *
from array_of_symbols import array_of_symbols,program_activity_record

class Synt:

    def __init__(self, file_name):
        self.error_handler = error_handler()
        self.lex = Lex(file_name,self.error_handler)
        self.inLan = IntLang(file_name)
        self.ao_symbols = array_of_symbols(file_name)
        self.error_handler.set_inLan(self.inLan)
        self.error_handler.set_lex(self.lex)

        self.program()

        self.ao_symbols.create_full_activity_record()
        self.inLan.close()
        self.createC = CreateC(file_name)


    def program(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "program", Id.IDENTIFIER,word, ID)
        block_name, ID = self.lex.start_read()  # program name
        self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
        self.ao_symbols.add_program(block_name,"main") #Create a program object for array of symbols
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "{", Id.GROUPING, word, ID)
        self.block(block_name)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "}", Id.GROUPING, word, ID)
        self.error_handler.error_handle(error_types.ReturnStatementCheck, self.inLan.return_statement, "main", block_name)
        self.inLan.return_statement = -1

    def block(self,block_name):
        self.inLan.make_list(block_name) #IL:Create a list for all the quads of this program(or procedure or function)
        self.declarations()
        self.subprograms()
        self.statements()
        self.ao_symbols.set_temp_variables(self.inLan.temp_var_value)
        self.inLan.reset_newtemp() #Reset temporary values so a new program can use them
        label_start = self.inLan.write_list() #IL:Write the list of quads of this program(or procedure or function)
        self.ao_symbols.set_starting_quad(label_start)
        self.ao_symbols.undo_nesting_level()#Set the nesting level of the previous program

    def declarations(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "declare", Id.IDENTIFIER, word, ID):
            self.varlist()
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ";", Id.SEPERATOR, word,ID)
            word, ID = self.lex.start_read()
            self.lex.undo_read()
            if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "declare", Id.IDENTIFIER, word, ID):
                self.declarations()
            else:
                return
        else:
            self.lex.undo_read()

    def varlist(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, ";", Id.SEPERATOR, word, ID):
            self.lex.undo_read()
            return
        self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
        ad_var = self.ao_symbols.add_variable(word) #Append the variable list of the current program
        self.error_handler.error_handle(error_types.RedaclaredVariable, ad_var, word, self.ao_symbols.current_program_name()) 
        word, ID = self.lex.start_read()
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, ",", Id.SEPERATOR, word, ID):
            word, ID = self.lex.start_read()  # variable in varlist
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            ad_var = self.ao_symbols.add_variable(word) #Append the variable list of the current program
            self.error_handler.error_handle(error_types.RedaclaredVariable, ad_var, word, self.ao_symbols.current_program_name()) 
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        self.varlist()

    def subprograms(self):
        while self.subprogram():
            pass

    def subprogram(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "function", Id.IDENTIFIER, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "procedure", Id.IDENTIFIER, word, ID):
            block_name, ID = self.lex.start_read()  # Name of fuction or procedure
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            self.ao_symbols.add_program(block_name,word)
            self.funcbody(block_name)
            self.error_handler.error_handle(error_types.ReturnStatementCheck, self.inLan.return_statement, word, block_name)
            self.inLan.return_statement = -1
            return True
        self.lex.undo_read()
        return False

    def funcbody(self,block_name):
        self.formalpars()
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "{", Id.GROUPING, word, ID)
        self.block(block_name)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "}", Id.GROUPING, word, ID)

    def formalpars(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)
        self.formalparlist()
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)

    def formalparlist(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, ")", Id.GROUPING, word, ID):
            return
        self.formalparitem()
        word, ID = self.lex.start_read()
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, ",", Id.SEPERATOR, word, ID):
            self.formalparitem()
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        self.formalparlist()

    def formalparitem(self):
        in_or_inout, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "in", Id.IDENTIFIER, in_or_inout, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "inout", Id.IDENTIFIER, in_or_inout, ID):
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            self.ao_symbols.add_variable(word) #Append the variables list of the current program
            self.ao_symbols.add_argument(in_or_inout) #Append the arguments list of the current program
        else:
            self.error_handler.error_handle(error_types.SyntaxWordFatal, "in or inout", word)  # Error exit

    def statements(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "{", Id.GROUPING, word, ID):
            self.statement()
            word, ID = self.lex.start_read()
            while self.error_handler.error_handle(error_types.SyntaxCheckWordId, ";", Id.SEPERATOR, word, ID):
                self.statement()
                word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "}", Id.GROUPING, word,ID)
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
            self.inLan.exit_statement = True
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
        self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
        #If the variable is not a temporary maded by the compiler then check if it is declared
        if assign.split("_")[0] != "T":
            un_var = self.ao_symbols.undeclared_variable(assign) #Check for undeclared variable
            self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,assign,self.ao_symbols.current_program_name())
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":=", Id.EQUAL, word, ID)
        x = self.expression()
        self.inLan.genquad(":=",x,"_",assign)

    def if_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "if", Id.IDENTIFIER, word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

        if_cond_start_pos = self.inLan.relative_program_pos() #IL:starting position of if statement
        exp_list = self.condition(False) #IL:get the condition quads
        self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
        self.inLan.add_condition(exp_list,if_cond_start_pos) #IL:add the condition to the code
        if_cond_end_pos = self.inLan.relative_program_pos() #IL:starting position of if statement

        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "then", Id.IDENTIFIER, word, ID)

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
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "else", Id.IDENTIFIER, word, ID):
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
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "while", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

        while_cond_start_pos = self.inLan.relative_program_pos() #IL:starting position of while statement
        exp_list = self.condition(False) #IL:get the condition quads
        self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
        self.inLan.add_condition(exp_list,while_cond_start_pos) #IL:add the condition to the code
        while_cond_end_pos = self.inLan.relative_program_pos() #IL:ending position of while statement 
         
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)

        self.statements()

        jump_false = self.inLan.relative_program_pos() - while_cond_end_pos + 2 #IL:get the position outside while
        self.inLan.genquad("jump","_","_","-"+str(jump_false))
        self.inLan.backpatch(jump_false,while_cond_start_pos,while_cond_end_pos,"JUMP-FALSE")


    def doublewhile_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "doublewhile", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()

        #We create a temp variable (lets say T_0) and set T_0 = 0.After that we set the condition to
        #jump to statement_1 if its true or in statement_2 if it is false.We add this code to statements:
        #if T_0=2 exit doublewhile      if T_0=1 exit doublewhile
        #statement_1                    statement_2
        #T_0 = 1                        T_0 = 2
        #jump to condition              jump to condition
        temp_var = self.inLan.newtemp() #IL:Create new temporary value
        temp_val_address = self.inLan.relative_program_pos() #IL:Get position of the quad below
        self.inLan.genquad(":=","0","_",temp_var) #IL:Give value 0 in the temp value

        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)
        
        cond_start_pos = self.inLan.relative_program_pos()
        cond = self.condition(False)
        self.inLan.backpatch(cond,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
        self.inLan.add_condition(cond,cond_start_pos) #IL:add the condition to the code
        cond_end_pos = self.inLan.relative_program_pos()

        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)

        #1st statement
        start_stat1 = self.inLan.relative_program_pos()
        self.inLan.genquad("=",temp_var,"2","exitDW") #Create the if for stat1
        self.statements()
        self.inLan.genquad(":=","1","_",temp_var) #Set temp var = 1
        jump_to_cond = self.inLan.relative_program_pos() - cond_start_pos 
        self.inLan.genquad("jump","_","_","-"+str(jump_to_cond)) #IL:Jump to condition from stat1

        
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "else", Id.IDENTIFIER, word, ID)

        #Set condition jump to false
        jump_false = self.inLan.relative_program_pos() - cond_end_pos + 1 
        self.inLan.backpatch(jump_false,cond_start_pos,cond_end_pos,"JUMP-FALSE")

        #2nd statement
        start_stat2 = self.inLan.relative_program_pos()
        self.inLan.genquad("=",temp_var,"1","exitDW") #Create the if for stat2
        self.statements()
        self.inLan.genquad(":=","2","_",temp_var) #Set temp var = 2
        jump_to_cond = self.inLan.relative_program_pos() - cond_start_pos 
        self.inLan.genquad("jump","_","_","-"+str(jump_to_cond)) #IL:Jump to condition frpm stat2
       
        #Set the "exitDW" of quads to this position(outside doublewhile)
        jump_to_cond1 = self.inLan.relative_program_pos() - start_stat1
        jump_to_cond2 = self.inLan.relative_program_pos() - start_stat2
        self.inLan.special_doublewhile(start_stat1,jump_to_cond1)
        self.inLan.special_doublewhile(start_stat2,jump_to_cond2)



    def loop_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "loop", Id.IDENTIFIER, word,ID)
        self.inLan.exit_statement = False

        loop_start_pos = self.inLan.relative_program_pos()
        self.statements()
        loop_end_pos = self.inLan.relative_program_pos()
        jump_beginning = loop_end_pos - loop_start_pos
        self.inLan.genquad("jump","_","_","-"+str(jump_beginning))
        self.inLan.special_loop(loop_start_pos,loop_end_pos)
        self.error_handler.warning_handle(warning_types.NoExitLoop,self.inLan.exit_statement, self.ao_symbols.current_program_name())

    def forcase_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "forcase", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()

        forcase_start_pos = self.inLan.relative_program_pos() #IL:Get the starting position of forcase

        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "when", Id.IDENTIFIER, word, ID):
            
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

            cond_start_pos = self.inLan.relative_program_pos()
            exp_list = self.condition(False)
            self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
            self.inLan.add_condition(exp_list,cond_start_pos) #IL:add the condition to the code
            cond_end_pos = self.inLan.relative_program_pos() #IL:ending position of while statement 

            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word,ID)
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":", Id.SEPERATOR, word,ID)

            self.statements()

            jump_to_begin = self.inLan.relative_program_pos() - forcase_start_pos #IL:positions from beginning of forcase
            self.inLan.genquad("jump","_","_","-"+str(jump_to_begin))
            jump_false = self.inLan.relative_program_pos() - cond_end_pos + 1
            self.inLan.backpatch(jump_false,cond_start_pos,cond_end_pos,"JUMP-FALSE")

            word, ID = self.lex.start_read()

        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "default", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()   
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":", Id.SEPERATOR,word, ID)             
        self.statements()

    def incase_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "incase", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()

        #IL:In incase we create a temporary variable and give it the value zero.If one condition
        #is true then the variable gets the value of 1.At the end of incase we check to see
        #if variable is 1 then we jump at the begin of incase,if variable is 0 we continue outside incase.
        temp_var = self.inLan.newtemp() #IL:Create new temporary value
        temp_val_address = self.inLan.relative_program_pos() #IL:Get position of the quad below
        self.inLan.genquad(":=","0","_",temp_var) #IL:Give value 0 in the temp value

        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "when", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

            cond_start_pos = self.inLan.relative_program_pos()
            cond = self.condition(False)
            self.inLan.backpatch(cond,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code 
            self.inLan.add_condition(cond,cond_start_pos) #IL:add the condition to the code
            cond_end_pos = self.inLan.relative_program_pos()

            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word,ID)
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":", Id.SEPERATOR, word,ID)

            self.statements()
            self.inLan.genquad(":=","1","_",temp_var) #IL:Set temp var value to 1
            
            jump_false = self.inLan.relative_program_pos() - cond_end_pos + 1
            self.inLan.backpatch(jump_false,cond_start_pos,cond_end_pos,"JUMP-FALSE")

            word, ID = self.lex.start_read()

        jump_to_begin = self.inLan.relative_program_pos() - temp_val_address #IL:positions from beginning of incase
        self.inLan.genquad("=",temp_var,"1","-"+str(jump_to_begin))
        self.lex.undo_read()


    def return_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "return", Id.IDENTIFIER,word, ID)
        x = self.expression()
        self.inLan.return_statement = self.lex.file_line
        self.inLan.genquad("retv",x,"_","_")

    def call_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "call", Id.IDENTIFIER, word,ID)
        proc_name, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
        arguments = self.actualpars()
        error_id = self.ao_symbols.undeclared_fun_or_proc(proc_name,"procedure",arguments)
        self.error_handler.error_handle(error_types.UndeclaredFuncOrProc, error_id,"procedure",proc_name,self.ao_symbols.current_program_name())
        self.inLan.genquad("call",word,"_","_")
        self.ao_symbols

    def print_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "print", Id.IDENTIFIER,
                             word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)
        x = self.expression()
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)
        self.inLan.genquad("out",x,"_","_")

    def input_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "input", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
        un_var = self.ao_symbols.undeclared_variable(word) #Check for undeclared variable
        self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,word,self.ao_symbols.current_program_name())
        self.inLan.genquad("inp",word,"_","_")
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)

    def actualpars(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)
        arguments = self.actualparlist()
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)
        return arguments

    def actualparlist(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        arguments = []
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, ")", Id.GROUPING, word, ID):
            return arguments
        arguments.append(self.actualparitem())
        word, ID = self.lex.start_read()
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, ",", Id.SEPERATOR, word, ID):
            arguments.append(self.actualparitem())
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        return arguments

    def actualparitem(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "in", Id.IDENTIFIER, word, ID):
            w = self.expression()
            #If the variable is not a temporary maded by the compiler then check if it is declared
            if w.split("_")[0] != "T" and (not self.inLan.isInt(w)):
                un_var = self.ao_symbols.undeclared_variable(w) #Check for undeclared variable
                self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,w,self.ao_symbols.current_program_name())
            self.inLan.genquad("par",w,"CV","_")
            return "in"
        elif self.error_handler.error_handle(error_types.SyntaxCheckWordId, "inout", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            un_var = self.ao_symbols.undeclared_variable(word) #Check for undeclared variable
            self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,word,self.ao_symbols.current_program_name())
            self.inLan.genquad("par",word,"REF","_")
            return "inout"
        else:
            self.error_handler.error_handle(error_types.SyntaxWordFatal, "in or inout", word)  # Error exit

    def condition(self,enable_not):
        Q = self.boolterm(enable_not)
        self.inLan.backpatch(Q,"_","true","RELOP")
        word, ID = self.lex.start_read()
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "or", Id.IDENTIFIER, word, ID):
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
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "and", Id.IDENTIFIER, word, ID):
            R.append("jump,_,_,false")
            self.inLan.backpatch(R,"_","DISTANCE","RELOP")
            R2 = self.boolfactor(enable_not)
            R = R + R2
            word, ID = self.lex.start_read()
        self.lex.undo_read()
        return R

    def boolfactor(self,enable_not):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "not", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "[", Id.GROUPING, word,ID)
            new_expression = self.condition(True)
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "]", Id.GROUPING, word,ID)
            del new_expression[-1] #IL:delete last jump,_,_,false quad
            self.inLan.backpatch(new_expression,"true","_","RELOP") #IL:Change every relop,x,y,true quad to relop,x,y,_ quad
            return new_expression
        elif self.error_handler.error_handle(error_types.SyntaxCheckWordId, "[", Id.GROUPING, word, ID):
            new_expression = self.condition(False)
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "]", Id.GROUPING, word,ID)
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
            expression_list = self.inLan.get_condition(start_address,end_address)
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
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "+", Id.OPERATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "-", Id.OPERATOR, word, ID):
            if w == None:
                w = self.inLan.newtemp()
                self.inLan.genquad(":=",x,"_",w)
            aop = self.add_oper()
            y = self.term()
            self.inLan.genquad(aop,w,y,w)
            word, ID = self.lex.start_read()
            self.lex.undo_read()
        if w is not None:
            return w
        return x

    def term(self):
        x = self.factor()
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        w = None
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "*", Id.OPERATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "/", Id.OPERATOR, word, ID):
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
            self.error_handler.error_handle(error_types.IntegerOutOfRange, word)
            return word
        elif self.error_handler.error_handle(error_types.SyntaxCheckWordId, "(", Id.GROUPING, word, ID):
            x = self.expression()
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word,ID)
            return x
        elif ID == Id.IDENTIFIER:
            if self.idtail(word) == True: #function
                w = self.inLan.newtemp()
                self.inLan.genquad("par",w,"RET","_")
                self.inLan.genquad("call",word,"_","_")
                word = w
            else: #variable
                #If the variable is not a temporary maded by the compiler then check if it is declared
                if word.split("_")[0] != "T":
                    un_var = self.ao_symbols.undeclared_variable(word) #Check for undeclared variable
                    self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,word,self.ao_symbols.current_program_name())
            return word

    def idtail(self,fun_name):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "(", Id.GROUPING, word, ID):
            arguments = self.actualpars()
            error_id = self.ao_symbols.undeclared_fun_or_proc(fun_name,"function",arguments)
            self.error_handler.error_handle(error_types.UndeclaredFuncOrProc, error_id,"function",fun_name,self.ao_symbols.current_program_name())
            return True
        return False

    def relational_oper(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "=", Id.COMPARATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "<=", Id.COMPARATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, ">=", Id.COMPARATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "<", Id.COMPARATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, ">", Id.COMPARATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "<>", Id.COMPARATOR, word, ID):
            return word
        else:
            self.error_handler.error_handle(error_types.SyntaxWordFatal, "= or <= or >= or < or > or <>", word)

    def add_oper(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "+", Id.OPERATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "-", Id.OPERATOR, word, ID):
            return word
        else:
            self.error_handler.error_handle(error_types.SyntaxWordFatal, "+ or -", word)

    def mul_oper(self):
        word, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "*", Id.OPERATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "/", Id.OPERATOR, word, ID):
            return word
        else:
            self.error_handler.error_handle(error_types.SyntaxWordFatal, "* or /", word)

    def optional_sign(self):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "+", Id.OPERATOR, word, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "-", Id.OPERATOR, word, ID):
            return self.add_oper()
        return None
