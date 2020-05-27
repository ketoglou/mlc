#!/usr/bin/python3
"""
Minimal++ Compiler 3rd phase

Authors:
Ketoglou Theocharis , AM:2723
Gelias Kwnstantinos , AM:2669

The C file does not support nested functions.It support only program and its functions
in nesting level 1.

Usage:
python3 mlc.py --help
python3 mlc.py -save-temps program.min : Save intermediate language,array of symbols and C file
python3 mlc.py program.min

This project originally maded by
multiple files that compined in this one.
The structure is:

1)Finite Automata
2)Lexical analysis
3)Idermediate Language
4)Array Of Symbols
5)Errors
6)Create C code
7)Assembly MIPS
8)Syntactic analysis
9)MLC - Main

"""

#Imports
import sys
import os
import string
import ast
from enum import Enum
import gc

#Finite Automata
#-----------------------------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------------------------


#Lexical analysis
#-----------------------------------------------------------------------------------------------
class lex:

    def __init__(self, file_name,error_handler):
        self.error_handler = error_handler
        try:
            self.file = open(file_name, "r")
            self.file_index = 0
            self.file_line = 1
            self.previous_pos = 0
        except FileNotFoundError:
            self.error_handler.error_handle(error_types.FileNotFound, file_name)


    def next_char(self):
        c = self.file.read(1)
        if c:
            self.file_index += 1
            if c == "\n":
                self.file_index = 0
                self.file_line += 1
        return c

    def undo_read(self):
        current_pos = self.file.tell() #Current position
        self.file.seek(self.previous_pos) #Go back to the start of the previous word
        find_new_line = self.file.read(current_pos-self.previous_pos) #Read all chars between the start of previous word and the end of the next word
        self.file.seek(self.previous_pos)#Go back to the start of the previous word
        self.file_line -= find_new_line.count("\n") #Count the new lines and subtract


    def start_read(self):
        self.previous_pos = self.file.tell()
        current_state = State.INITIAL
        word = ""
        ID = None
        while current_state != State.FINAL:
            # Get next character
            position = self.file.tell()
            c = self.next_char()

            # Special occasions
            if c == "" and current_state != State.INITIAL:
                self.error_handler.error_handle(error_types.UnexpectedEnd)
            elif c == "" and current_state == State.INITIAL:
                return (None, None)  # RETURN None when EOF
            elif c not in Symbols.ALL:
                self.error_handler.error_handle(error_types.UnexpectedChar,self.file_index)

            # Find the next state in finite automata
            for next_state in automata_states[current_state]:
                if c in next_state["condition"]:
                    # Get the next state
                    current_state = next_state["next_state"]

                    # Get the id if is done
                    if current_state == State.FINAL or current_state == State.FINAL_BLANK or current_state == State.FINAL_COMMENT:
                        ID = next_state["id"]

                    # If must,give back the character the previous state take to make checks.
                    if next_state["go_back"] == True:
                        self.file.seek(position)
                        break

                    # Check if we must append the word or not
                    if current_state != State.INITIAL and current_state != State.FINAL_BLANK and current_state != State.FINAL_COMMENT:
                        word = word+c
                        break
                    # If we have blanks,ignore them and dont append the word
                    elif current_state == State.FINAL_BLANK:
                        current_state = State.FINAL
                        break
                    # If we have comments,ignore the next characters
                    elif current_state == State.FINAL_COMMENT:
                        current_state = State.FINAL
                        word = ""
                        break

        if word != "":
            return (word, ID)
        else:
            return self.start_read()  # We end up here only in COMMENTS case

#-----------------------------------------------------------------------------------------------



#Idermediate Language
#-----------------------------------------------------------------------------------------------
class int_lang:

    def __init__(self, file_name):
        self.fd_name = file_name[0:-4] + ".int"
        self.fd = open(self.fd_name,"w+") #Create the file that we will store the idermediate code
        self.temp_var_value = 0 #Used to calculate temporary values
        #Create a list of lists,every list in this list is a procedure or function.
        #The first list in this list is the function.Every list have the quad of the current function or function or procedure.
        self.functions_list = []
        self.quad_number = 1 #Counts the next quad number
        self.return_statement = -1 #Used to check if a function has one return at least or to make susre that procedure has no return inside.It hold the number of line the return found(or -1 if not found)
        self.exit_statement = False #Used for warning if no exit statement exist in loop statement

    #Get the current position of a quad in array
    def relative_function_pos(self):
        return len(self.functions_list[-1])

    #Gives the next quad number
    def nextquad(self):
        self.quad_number  += 1
        return (self.quad_number - 1)

    #Creates a list for a function or function or procedure with the first quad to be the name
    def make_list(self,block_name):
        quad_start = "begin_block,"+block_name+",_,_"
        quad_end = "end_block,"+block_name+",_,_"
        function = [quad_start,quad_end]
        self.functions_list.append(function)

    #If a function or function or procedure end then we write all of its quads
    #every relop or jump quad may have a relative to their position jump
    #eg jump,_,_,+5 it means that when this quad get its position i will jump to +5 from it
    #so the new quad (lets say it is 110) will be 110:jump,_,_,105
    def write_list(self):
        if len(self.functions_list) > 0:
            li = self.functions_list[-1] #Get the current function or function or procedure list
            begin_block_num = self.nextquad() #Get the quad number
            self.fd.write(str(begin_block_num)+":"+li[0]+"\n") #Write begin_block
            #Write all the quads of this function or function or procedure
            for quad in range(2,len(li)):
                quad_num = self.nextquad()
                squad = li[quad].split(",")
                if list(squad[-1])[0] == "+":
                    squad[-1] = str(quad_num + int(squad[-1].split("+")[1]))
                    li[quad] = ",".join(squad)
                elif list(squad[-1])[0] == "-":
                    squad[-1] = str(quad_num - int(squad[-1].split("-")[1]))
                    li[quad] = ",".join(squad)
                self.fd.write(str(quad_num)+":"+li[quad]+"\n")
            #if we are in the main function then write halt before end_block
            if len(self.functions_list) == 1:
                self.fd.write(str(self.nextquad())+":halt,_,_,_\n")  #write halt
                self.write_first_line("0:jump,_,_,"+str(begin_block_num)+"\n")  #write jump to main
            self.fd.write(str(self.nextquad())+":"+li[1]+"\n")  #write end_block
            del self.functions_list[-1] #remove last list
            return begin_block_num  #return start label of the function(for array of symbols)

    #Creates next quad for the current function(or function or procedure)
    def genquad(self,op,x,y,z):
        quad = op+","+x+","+y+","+z
        self.functions_list[-1].append(quad)

    #Return the full expression code and remove it from main code
    #this function is used only in condition statement because we need lists of expression quads
    def get_condition(self,start_address,end_address):
        Q = self.functions_list[-1][start_address:end_address]
        del self.functions_list[-1][start_address:end_address]
        return Q

    #This function add the condition we get from the above function (get_condition) to the code
    def add_condition(self,expression_list,starting_pos):
        if(starting_pos == len(self.functions_list[-1])):
            self.functions_list[-1] = self.functions_list[-1] + expression_list
        else:
            self.functions_list[-1][starting_pos:starting_pos] = expression_list

    #Find all relop or jump(set mode) quads that are in the form "relop,x,y,old_address" or "jump,_,_,old_address
    #and set the old_address to the new_address.If the new_address == "DISTANCE"
    #then the function set the relop to how positions far is from the end of the expression list.
    #Usually used with old_address = "true","false" and new_address = "true","false","DISTANCE"
    #and mode = "RELOP","JUMP".
    #Anonter mode is the "JUMP-FALSE" which is usually used when we know where in the code is a condition
    #that has unseted the "jump to false" quad so is setted to the rigth address
    #Usage(usually):
    #backpatch(expression list,"true" or "false","true" or "false","JUMP" or "RELOP")
    #backpatch(expression list,"true" or "false","DISTANCE","JUMP" or "RELOP")
    #backpatch(jump to false address,start address in functions_list[-1],end_address in functions_list[-1],"JUMP-FALSE")
    def backpatch(self,expression_or_jumpFalseAddress,old_address,new_address,mode):
        #In this mode we use expression_or_jumpFalseAddress variable as the expression list
        if mode == "RELOP" or mode == "JUMP":
            for i in range(0,len(expression_or_jumpFalseAddress)):
                quad = expression_or_jumpFalseAddress[i].split(",")
                if quad[-1] == old_address:
                    if (mode == "RELOP" and quad[-2] != "_") or (mode == "JUMP" and quad[-2] == "_"):
                        if new_address == "DISTANCE":
                            quad[-1] = "+"+str(len(expression_or_jumpFalseAddress)-i) #this will jump +str(len(expression)-i) from its current position
                        else:
                            quad[-1] = new_address
                expression_or_jumpFalseAddress[i] = ",".join(quad)
        #In this mode we use expression_or_jumpFalseAddress variable as address of jump
        elif mode == "JUMP-FALSE":
            for i in range(old_address,new_address):
                quad = self.functions_list[-1][i].split(",")
                if quad[-1] == "false":
                    quad[-1] = "+" + str(expression_or_jumpFalseAddress)
                    self.functions_list[-1][i] = ",".join(quad)


    #Creates new temporary values
    def newtemp(self):
        self.temp_var_value += 1
        return "T_"+str(self.temp_var_value-1)

    #Reset temporary value number
    def reset_newtemp(self):
        self.temp_var_value = 0

    #Delete the idermediate file(only for errors)
    def delete(self):
        os.remove(self.fd_name)

    #Close the idermediate file(only when everything goes well)
    def close(self):
        self.fd.close()

    #Helping function that write at the beginning of the file
    def write_first_line(self,line):
        self.fd.seek(0,0) #Seek to start
        txt = self.fd.read() #Save file contents
        self.fd.close() #Close file
        self.fd = open(self.fd_name,"w+") #Erase file and reopen
        self.fd.write(line+txt) #Rewrite file with the first line

    #Helping function for not statement,it return the opposite relational operator
    def reverse_relop(self,relop):
        if relop == "=":
            return "<>"
        elif relop == "<=":
            return ">"
        elif relop == ">=":
            return "<"
        elif relop == ">":
            return "<="
        elif relop == "<":
            return ">="
        elif relop == "<>":
            return "="

    #Special function for loop statement finds the exit(s)(if exist(s)) and set them to jump outside loop
    def special_loop(self,start_address,end_address):
        for i in range(start_address,end_address):
            quad = self.functions_list[-1][i].split(",")
            if quad[0] == "exit" :
                self.functions_list[-1][i] = "jump,_,_,+" + str(end_address - i + 1)

    #Special function for doublewhile that set the exit from doublewhile quads
    def special_doublewhile(self,function_address,jump_address):
        quad = self.functions_list[-1][function_address].split(",")
        quad[-1] = "+" + str(jump_address)
        self.functions_list[-1][function_address] = ",".join(quad)

    #Check if w str is int or not
    def isInt(self,num):
        try:
            int(num)
            return True
        except ValueError:
            return False
#-----------------------------------------------------------------------------------------------


#Array Of Symbols
#-----------------------------------------------------------------------------------------------
class array_of_symbols:

    #Initialize a list which hold info about main and all functions,procedures and create a file to show array of symbols
    def __init__(self,file_name):
        self.fd_name = file_name[0:-4] + "_array_of_symbols.txt"
        self.fd = open(self.fd_name,"w")
        self.list_of_functions = []
        self.current_function_pos = -1
        self.current_nesting_level  = -1 #Used for array of symbols
        self.temporary_arguments = []

    #Add a main or a new procedure or function
    def add_function(self,function_name,function_type,arguments):
        #Check if another function(function or procedure) exist in the same nesting level whith the same name,type,arguments
        self.current_nesting_level += 1
        self.current_function_pos += 1
        #If nesting level == 1
        if self.current_nesting_level == 1:
            #Check all functions with nesting level == 1 and see if we redeclared same function
            for i in range(1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                #If they have same nesting level
                if function.nesting_level == 1:
                    #If they have same name and type
                    if function_name == function.name and function_type == function.type and len(arguments) == len(function.arguments):
                        same_args = True
                        for j in range(0,len(arguments)):
                            if arguments[j] != function.arguments[j]:
                                same_args = False
                                break
                        if same_args == True:
                            return False

        else:
            for i in range(len(self.list_of_functions)-1,0,-1):
                function = self.list_of_functions[i]
                #Check all functions with same nesting level,if not same nesting level then no function exist in this nesting level with same characteristics
                if  function.nesting_level == self.current_nesting_level :
                    if function.name == function_name and function.type == function_type and len(arguments) == len(function.arguments):
                        same_args = True
                        for j in range(0,len(arguments)):
                            if arguments[j] != function.arguments[j]:
                                same_args = False
                                break
                        if same_args == False:
                            return False
                elif function.nesting_level <  self.current_nesting_level:
                    break

        pa_record = function_activity_record(function_name,function_type)       #Create an object for this function
        self.list_of_functions.append(pa_record)                              #Add this function to the list of functions
        self.list_of_functions[-1].nesting_level = self.current_nesting_level #Set nesting level for current function
        #Set arguments for current function
        for i in range(0,len(arguments)):
            self.list_of_functions[-1].arguments.append(arguments[i])
        return True

    #Add a declared argument or variable in the current function
    def add_variable(self,var):
        if var not in self.list_of_functions[-1].variables:
            self.list_of_functions[-1].variables.append(var)
            return True
        return False

    #Add type of argument(in or inout) of current function
    def add_temporary_argument(self,arg,var):
        self.temporary_arguments.append([arg,var])

    def get_temporary_arguments(self):
        t = self.temporary_arguments[:]
        self.temporary_arguments.clear()
        return t

    #Go back one nesting level
    def undo_nesting_level(self):
        self.current_nesting_level -= 1

    #Set the number of temporary values eg if is 3 then we have T_0,...,T_2
    def set_temp_variables(self,t_vars,pos):
        self.list_of_functions[pos].temporary_variables = t_vars

    #Set the starting quad number of current function
    def set_starting_quad(self,s_quad,pos):
        self.list_of_functions[pos].starting_quad = s_quad


    #Helping function return current function name
    def current_function_name(self,pos):
        return self.list_of_functions[pos].name


    #Check if a variable is declared in the function
    def undeclared_variable(self,var,pos):
        current_function = self.list_of_functions[pos]
        #Check if it is declared on current function
        if var in current_function.variables:
            return True
        for arg in current_function.arguments:
            if arg[1] == var:
                return True

        #Check all the parent functions to find the variable
        if current_function.nesting_level > 1:
            nl_parent = self.list_of_functions[pos].nesting_level #This variable is for check only parents and not their brothers
            for i in range(pos-1,0,-1):
                function = self.list_of_functions[i]
                if nl_parent != function.nesting_level:
                    if function.nesting_level < current_function.nesting_level:
                        #Check if variable belong to parent function as declared variable or as argument
                        if var in function.variables:
                            return True
                        for arg in function.arguments:
                            if arg[1] == var:
                                return True
                    nl_parent = function.nesting_level
                #Break if we check and the last parent
                if function.nesting_level == 1:
                    break

        #Check if it is declared as global variable(no arguments in main)
        if var in self.list_of_functions[0].variables:
            return True

        return False


    #Check if a function or procedure is declared.
    #name: Used to see if the fun or proc is declared
    #type_called: It is used to see if a proc called with call command and if a function called in expression
    #arguments: Used to see if the arguments are correct
    #pos: The function position in list_of_functions
    def undeclared_fun_or_proc(self,name,type_called,arguments,func_pos):

        function_pos = -1

        #If its main(pos == 0) then main can call all functions with nesting level == 1
        if func_pos == 0:
            for i in range(1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                        #If the arguments is the same then we find which function the main call
                        if self.check_same_args(arguments,function.arguments) == True:
                            function_pos = i
        #If its not main(pos > 0) then this function can call
        #1)Its own childen functions(all functions following it with nesting level of function + 1 until nesting level < nesting level of function)
        #2)Can call it self(recursive)
        #3)Can can all parent and brother functions(all functions in front of it until nesting level == 1 and after that only the function in front of it with nesting level == 1)
        else:

            current_function = self.list_of_functions[func_pos]
            #Check all the childerns of the current function(if have any)
            for i in range(func_pos+1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                if function.nesting_level == (current_function.nesting_level + 1):
                    #If they have same name and type
                    if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                        #Check if the arguments are the same
                        if self.check_same_args(arguments,function.arguments) == True:
                            function_pos = i
                else:
                    #If we are here it means that no other children exist
                    break

            #Check calling itself
            if function_pos == -1:
                #If we are here it means that this function have no children or the children functions checked without find anything
                #Next thing is to check if the function call it self
                if name == current_function.name and type_called == current_function.type and len(arguments) == len(current_function.arguments):
                    if self.check_same_args(arguments,current_function.arguments) == True:
                        function_pos = func_pos

            #Check all the parents of the current function(if have any)
            if function_pos == -1:
                #If we are here it means that this function have no children or the children functions checked without find anything and did not call it self
                #Last thing is to check if the function call a parent function
                nl_1_found = False #This variable is used to check when a parent with nesting level(nl) 1 is found,so only parents with nl=1 can now be called
                for i in range(func_pos-1,0,-1):
                    function = self.list_of_functions[i]
                    if function.nesting_level == 1:
                        nl_1_found = True
                    if ((function.nesting_level <= current_function.nesting_level) and (nl_1_found == False)) or ((function.nesting_level == 1) and (nl_1_found == True)):
                        #If they have same name and type
                        if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                            #Check if the arguments are the same
                            if self.check_same_args(arguments,function.arguments) == True:
                                function_pos = i


        #If function_pos != -1 then we found it(declared),else is undeclared
        if function_pos != -1:
            return 0
        else:
            return 1


    #Private function to check if arguments are the same(used between comparison of two functions)(used only in undeclared_fun_or_proc)
    #eg called_args=['in','inout'] and real_args=[['in','x'],['inout','y']] is same
    def check_same_args(self,called_args,real_args):
        same_args = True
        for i in range(0,len(called_args)):
            if called_args[i] != real_args[i][0]:
                same_args = False
                break
        return same_args

    #Calculates framelength of every function
    def calc_framelength(self):
        for function in self.list_of_functions:
            function.frame_length = 4*function.temporary_variables + 4*len(function.arguments) + 4*len(function.variables)

    #Write to the array of symbols file the info about the current function
    def write_aos(self):
        for function in self.list_of_functions:
            self.fd.writelines("Name:"+function.name+"\n")
            self.fd.write("Type:"+function.type+"\n")
            self.fd.write("Starting Quad:"+str(function.starting_quad)+"\n")
            self.fd.write("Nesting Level:"+str(function.nesting_level)+"\n")
            self.fd.write("Arguments:"+str(function.arguments)+"\n")
            self.fd.write("Variables:"+str(function.variables)+"\n")
            self.fd.write("Temporary Variables:"+str(function.temporary_variables)+"\n")
            self.fd.write("Frame Length:"+str(function.frame_length)+"\n")
            self.fd.write("___\n")


    #Deletes file array of symbol,used when error occur.
    def delete(self):
        os.remove(self.fd_name)

    #Close the file array of symbol(eg successfull compile)
    def close(self):
        self.fd.close()

#We create an object for every function(main,function,procedure) and hold information
class function_activity_record:

    #If the function have arguments then the arguments[0] is the variables[0]....and so on until
    #the arguments list end.After end of the arguments the variables are the declared ones.
    def __init__(self,func_name,func_type):
        self.name = func_name                       #Function name
        self.type = func_type                       #Type of function:"main","function","procedure"
        self.starting_quad = -1                     #Number of starting quad of this function

        self.arguments = []                         #Arguments of this function,leave empty for main(eg [['in','x'],['inout','y']])
        self.variables = []                         #Variables that have beed declared(eg ['x','y'])
        self.temporary_variables = -1               #The number indicates the maximum temporary variable (eg if it is 10 then variables form T_0 to T_10 used,if it is -1 no temporary variables used)
        self.nesting_level = -1                     #Nesting level of this function
        self.frame_length = 0                       #Used for stack in assembly(computed in mips)

#-----------------------------------------------------------------------------------------------


#Errors
#-----------------------------------------------------------------------------------------------
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class error_types(Enum):
    FileArgument = 0            #No file argument,fatal error
    FileNotFound = 1            #File not found,fatal error
    UnexpectedEnd = 2           #Unxpected end,fatal error
    UnexpectedChar = 3          #Unxpected character,fatal error
    UnexpectedCommentEnd = 4    #Unxpected commend end,fatal error
    WrongFilePrefix = 5         #Wrong file prefix,fatal error
    IntegerOutOfRange = 6       #Integer out of range,fatal error if false
    SyntaxCheckWordIdFatal = 7  #Matching words and ids,fatal error if false
    SyntaxCheckWordId = 8       #Matching words and ids,not fatal
    SyntaxIdFatal = 9           #Matching ids,fatal error if false
    SyntaxWordFatal = 10        #Wrong word,fatal error if false
    UndeclaredVariable = 11     #Check for undeclared variable,fatal error if false
    RedeclaredVariable = 12     #Check for redeclared variable,fatal error if false
    UndeclaredFuncOrProc = 13   #Check for undeclared function or procedure,fatal error if false
    RedeclaredFuncOrProc = 14   #Check for redeclared function or procedure,fatal error if false

class warning_types(Enum):
    NoExitLoop = 1              #Used when no exit statement found at loop statement
    ReturnStatementCheck = 2  #Check if we have at least one return(function) or no return(procedure)

class error_handler:

    def __init__(self):
        self.inLan = None #IntLang class is used to to delete the idermediate file in case of error or to take some info from array of symbols
        self.lex = None #Lex class is used to define number of line the error found
        self.aos = None #Array of symbols class

    #This error function to handle error it can return True(no error),False(error) or exit(fatal error)
    #It takes variable number of arguments,every type of error has its own number of arguments.
    #Arguments:
    #FileArgument: No arguments
    #FileNotFound: args[0] = file_name
    #UnexpectedEnd: No arguments
    #UnexpectedChar: args[0] = unexpected_character_index
    #UnexpectedCommentEnd: No arguments
    #WrongFilePrefix: args[0] = wrong_prefix
    #IntegerOutOfRange: args[0] = constant
    #SyntaxCheckWordIdFatal: args[0] = expected_word,args[1] = expected_id,args[2] = word,args[3] = id
    #SyntaxCheckWordId: args[0] = expected_word,args[1] = expected_id,args[2] = word,args[3] = id
    #SyntaxIdFatal: args[0] = expected_id,args[1] = id
    #SyntaxWordFatal: args[0] = expected_word,args[1] = word
    #UndeclaredVariable: args[0] = check(boolean),args[1] = variable,args[2] = function_that_contain_this_variable
    #RedeclaredVariable: args[0] = check(boolean),args[1] = variable,args[2] = function_that_contain_this_variable
    #UndeclaredFuncOrProc: args[0] = number_of_error,args[1] = type(function or procedure),args[2] = name(of function or procedure),args[3] = function_contain_this_func_or_proc
    #RedeclaredFuncOrProc : args[0] = check(boolean), args[1] = type , args[2] = name
    def error_handle(self,error_type, *args):
        if error_type == error_types.FileArgument:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" wrong arguments, use python3 mlc.py --help")
        elif error_type == error_types.FileNotFound:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" file "+str(args[0])+" not found!")
        elif error_type == error_types.UnexpectedEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" unexpected end at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.UnexpectedChar:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" unexpected character at index "+str(args[0])+" in line "+str(self.lex.file_line)+".")
        elif error_type == error_types.UnexpectedCommentEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" unexpected comment end at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.WrongFilePrefix:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" wrong file prefix expected: .min but find:"+str(args[0]))

        elif error_type == error_types.IntegerOutOfRange:
            try:
                x = int(args[0])
                if x > 32767 or x < -32767:
                    print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" integer out of range, at line "+str(self.lex.file_line)+".")
                return True
            except ValueError:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" expected: Integer, and find:"+str(args[0])+", at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.SyntaxCheckWordIdFatal:
            if(args[0] != args[2] or args[1] != args[3]):
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" expected:"+str(args[0])+" but find:"+str(args[2])+" , at line "+str(self.lex.file_line)+".")
            else:
                return True
        elif error_type == error_types.SyntaxCheckWordId:
            if(args[0] != args[2] or args[1] != args[3]):
                return False
            return True
        elif error_type == error_types.SyntaxIdFatal:
            if args[0] != args[1]:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" expected:"+str(args[0])+", and find:"+str(args[1])+", at line "+str(self.lex.file_line)+".")
            else:
                return True
        elif error_type == error_types.SyntaxWordFatal:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" expected:"+str(args[0])+", and find:"+str(args[1])+", at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.UndeclaredVariable:
            if args[0] == True:
                return True
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" undeclared variable: " + args[1] + " ,belong to: "+ args[2] + " ,at line:" + str(self.lex.file_line))
        elif error_type == error_types.RedeclaredVariable:
            if args[0] == True:
                return True
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" redeclared variable: " + args[1] + " ,belong to: "+ args[2] + " ,at line:" + str(self.lex.file_line))
        elif error_type == error_types.UndeclaredFuncOrProc:
            if args[0] == 0:
                return True
            if args[0] == 1:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + " undeclared first use of " + args[1] + " "+ args[2] + " ,at line:" + str(self.lex.file_line))
        elif error_type == error_types.RedeclaredFuncOrProc:
            if args[0] == True:
                return True
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" redeclared " + args[1] + " "+ args[2] + " ,at line:" + str(self.lex.file_line))
        else:
            #Normally we not end up here,except the error_type is not defined
            print(bcolors.FAIL+bcolors.BOLD+bcolors.UNDERLINE+"mlc error:"+bcolors.ENDC +" undefined error!")

        self.exit_program() #If we get here a fatal error occur

    #NoExitLoop: arg[0] = check_if_exist(boolean), args[1] = name_of_function
    #ReturnStatementCheck: args[0] = number_of_line_found_return_or_-1_if_not_found,args[1] = type(function or procedure),args[2] = name(of function or procedure)
    def warning_handle(self,warning_type,*args):
        if warning_type == warning_types.NoExitLoop:
            if args[0] == False:
                print(bcolors.WARNING+"mlc warning:"+bcolors.ENDC +" no exit statement found at loop at "+args[1])
        elif warning_type == warning_types.ReturnStatementCheck:
            if args[0] == -1 and args[1] == "function" :
                print(bcolors.WARNING+"mlc warning:"+bcolors.ENDC +" no return statement found at function "+args[2])
            elif args[0] != -1 and args[1] == "procedure":
                print(bcolors.WARNING+"mlc warning:"+bcolors.ENDC +" return statement found at procedure "+args[2]+ ", at line:" + str(args[0]))
            elif args[0] != -1 and args[1] == "main":
                print(bcolors.WARNING+"mlc warning:"+bcolors.ENDC +" return statement found at main program "+args[2]+ ", at line:" + str(args[0]))
            else:
                return True
        else:
            #Normally we not end up here,except the warning_type is not defined
            print(bcolors.WARNING+"mlc warning:"+bcolors.ENDC +" undefined warning!")


    #This function used when an error occur and the idermediate file exist,so it delete it
    def exit_program(self):
        if self.inLan != None:
            self.inLan.delete()
        if self.aos != None:
            self.aos.delete()
        exit()

    #Error handler need Idermediate Language object to delete the idermediate file if an error occur
    def set_inLan(self,inlan):
        self.inLan = inlan

    #Error handler need Lexer object to define the number of line an error occur
    def set_lex(self,lex):
        self.lex = lex

    def set_aos(self,aos):
        self.aos = aos
#-----------------------------------------------------------------------------------------------


#Create C code
#-----------------------------------------------------------------------------------------------
class create_c_code:

    def __init__(self, file_name, list_of_function):
        name =  file_name[0:-4]
        self.file_int = open((name + ".int"), "r") #open .int file for read
        self.file_c = open((name + ".c"),"w+")
        self.list_of_functions = list_of_function
        self.createC()
        self.file_int.close()
        self.file_c.close()

    def createC(self):
        self.file_c.write("//This code is for testing the idermediate language of minimal++\n\n#include <stdio.h>\n\n")
        relop_list = ["=",">","<","<>",">=","<="]
        oper_list = ["+","-","*","/"]

        #first quad of the idermediate language jumps to main,here we dont need it
        #we need only its label so we know what to call in main
        main_label = "L_"+ str(int(self.read_line().split(",")[3])) +":"

        current_function = None
        current_function_pos = 0

        original_quad = self.read_line()

        #Write the code to file
        while original_quad:
            quad = original_quad.split(":",1)
            label = int(quad[0])
            quad = original_quad.split(",") #remove label from quad
            quad[0] = quad[0][quad[0].index(":")+1:] #remove label from quad
            function_begin = False #used so we know where a function(function or procedure start)
            c_str = ""
            if quad[0] in relop_list:
                if quad[0] == "=" : quad[0] = "==" #change the boolean equality because C using other
                if quad[0] == "<>" : quad[0] = "!=" #change the boolean differrent because C using other
                quad[1] = self.check_inout(quad[1],current_function_pos)
                quad[2] = self.check_inout(quad[2],current_function_pos)
                c_str = "if (" + quad[1] + quad[0] + quad[2] + ") goto " + "L_" + quad[3]
            elif quad[0] in oper_list:
                quad[1] = self.check_inout(quad[1],current_function_pos)
                quad[2] = self.check_inout(quad[2],current_function_pos)
                quad[3] = self.check_inout(quad[3],current_function_pos)
                c_str = quad[3] + " = " + quad[1] + " " + quad[0] + " " + quad[2]
            elif quad[0] == "jump":
                c_str = "goto " + "L_" + quad[3]
            elif  quad[0] == ":=":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                quad[3] = self.check_inout(quad[3],current_function_pos)
                c_str = quad[3] + " = " + quad[1]
            elif quad[0] == "out":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                c_str = 'printf("%d\\n",' + quad[1] + ")"
            elif quad[0] == "inp":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                c_str = 'scanf("%d",&' + quad[1] + ")"
            elif quad[0] == "retv":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                c_str = "return " + quad[1]
            elif quad[0] == "call":
                c_str = quad[1] + "()"
            elif quad[0] == "halt":
                c_str = "return 0"
            elif quad[0] == "par":
                ret = ""
                call_label = "L_"+ str(label) +":"

                while(quad[0] == "par"):
                    quad[1] = self.check_inout(quad[1],current_function_pos)
                    self.file_c.write("\t"+call_label+" asm(\"nop\");\t//"+",".join(quad)+"\n")
                    if quad[2] == "CV":
                        c_str = c_str + quad[1] + ","
                    elif quad[2] == "REF":
                        c_str = c_str + "&" + quad[1] + ","
                    elif quad[2] == "RET":
                        ret = quad[1] + " = "
                    quad = self.read_line().split(",") #remove label from quad
                    call_label = quad[0].split(":")[0] #create label(this will used only when we are outside while in call)
                    quad[0] = quad[0][quad[0].index(":")+1:] #remove label from quad
                #if we outside while the we have the call quad
                label = call_label #update label for call
                original_quad = ",".join(quad)
                if c_str != "": #remove the last comma
                    c_str = c_str[:-1]
                if ret != "":
                    c_str = ret + quad[1] + "(" + c_str + ")"  #function
                else:
                    c_str = quad[1] + "(" + c_str + ")" #procedure
            elif quad[0] == "begin_block":
                current_function_pos = self.find_function_pos_sq(label)
                current_function = self.list_of_functions[current_function_pos]
                function_begin = True

                function_type = "int"
                if current_function.type == "procedure":
                    function_type = "void"
                arguments_l =""

                #Set arguments for function and set void(if function is procedure) or int(if function is function)
                if len(current_function.arguments) > 0:
                    for i in range(0,len(current_function.arguments)):
                        arg0 = ""
                        if current_function.arguments[i][0] == "in":
                            arg0 = "int "
                        elif current_function.arguments[i][0] == "inout":
                            arg0 = "int *"
                        arg0 = arg0 + current_function.arguments[i][1]
                        arguments_l = arguments_l + arg0 + ", "
                    arguments_l = arguments_l[:-2]

                c_str = "\n" + function_type + " " + current_function.name + "(" + arguments_l + "){\n"
                self.file_c.write(c_str + "\tL_"+str(label)+": asm(\"nop\");"+"//" + original_quad + "\n")
                self.create_variables(current_function_pos)
            elif quad[0] == "end_block":
                function_begin = True
                self.file_c.write("\tL_"+str(label)+": asm(\"nop\");"+"\t//" + original_quad + "\n}\n")

            if function_begin == False:
                c_str = "\tL_" + str(label) + ": " + c_str + ";" + "\t//" + original_quad + "\n"
                self.file_c.write(c_str)
            function_begin = False
            original_quad = self.read_line()

        self.file_c.write("\nint main(){\n\t return "+current_function.name+";\n}")


    #Read quad and delete the \n from the end
    def read_line(self):
        line = self.file_int.readline()
        quad = line.split(",")
        quad[-1] = quad[-1].split("\n")[0]
        quad = ",".join(quad)
        return quad

    def create_variables(self,func_pos):
        function = self.list_of_functions[func_pos]
        if len(function.variables) > 0 or function.temporary_variables > 0:
            self.file_c.write("\tint ")
            c_str = ""
            if len(function.variables) > 0:
                for integer_ in function.variables:
                    c_str = c_str + integer_ + ","
            if function.temporary_variables > 0:
                for i in range(0,function.temporary_variables):
                    c_str = c_str + "T_" + str(i) + ","
            c_str = c_str[:-1] #remove the last comma
            self.file_c.write(c_str + ";\n")

    #Find the position of current function in array of symbols by starting quad
    def find_function_pos_sq(self,starting_quad):
        for i in range(0,len(self.list_of_functions)):
            function = self.list_of_functions[i]
            if function.starting_quad == starting_quad:
                return i

    #Check if a variable is inout and add the *
    def check_inout(self,var,func_pos):
        function = self.list_of_functions[func_pos]
        #Convert inout argument
        for i in range(0,len(function.arguments)):
            if var == function.arguments[i][1] and "inout" == function.arguments[i][0]:
                return "*" + var
        return var
#-----------------------------------------------------------------------------------------------


#Assembly MIPS
#-----------------------------------------------------------------------------------------------
class mips_assembly:

    def __init__(self,file_name,list_of_functions):
        #Create assembly file
        self.file_mips = open(file_name[0:-4] + ".asm","w")
        #Open for read idermediate file
        self.file_int = open(file_name[0:-4] + ".int","r")

        #list_of_functions contain at position 0 the main
        #followed by a child function of main with all its childs and their childs(if have any)
        #followed by a child function of main with all its childs and their childs(if have any)
        #etc
        self.list_of_functions = list_of_functions
        self.main_start_quad = self.list_of_functions[0].starting_quad

        self.translate_int_to_ass()

        self.file_int.close()
        self.file_mips.close()



    #Make assembly code and save at $t0 the address(in stack) of the variable that does not belong to the current function
    #return 0 if variable is in main(global), return 1 if is local variable of a parent function
    #return 2 if is "in" argument of a parent function, return 3 if is "inout" argument of a parent function
    def gnvlcode(self,variable,func_pos):
        current_function = self.list_of_functions[func_pos]

        counter = 0
        offset = -1
        in_or_inout = ""
        parent_function = None
        #Check all the parent functions to find the variable
        if current_function.nesting_level > 1:
            nl_parent = current_function.nesting_level #This variable is for check only parents and not their brothers
            for i in range(func_pos-1,0,-1):
                parent_function = self.list_of_functions[i]
                if nl_parent != parent_function.nesting_level:
                    if parent_function.nesting_level < current_function.nesting_level:
                        counter += 1
                        if variable in parent_function.variables:
                            offset = 12 + 4*len(parent_function.arguments) + parent_function.variables.index(variable)
                            break
                        for j in range(0,len(parent_function.arguments)):
                            arg = parent_function.arguments[j]
                            if variable == arg[1]:
                                offset = 12 + 4*j
                                in_or_inout = arg[0]
                                break
                    nl_parent = parent_function.nesting_level
                #Break if we check and the last parent
                if parent_function.nesting_level == 1:
                    break

        if offset != -1:
            counter -= 1
            self.add_command("lw $t0,-4($sp)")
            for i in range(0,counter):
                self.add_command("lw $t0,-4($t0)")

            self.add_command("addi $t0,$t0,-"+str(offset))
            if in_or_inout == "":
                return 1
            elif in_or_inout == "in":
                return 2
            elif in_or_inout == "inout":
                return 3
        else:
        #If we get here then the variable is global(in main)
            return 0


    #Move data from variable(in memory) to register
    def loadvr(self,var,reg,func_pos):
        function = self.list_of_functions[func_pos]

        temp_var = -1
        t = var.split("_")
        if len(t) > 1:
            temp_var = int(t[1])

        len_vars = len(function.variables)
        len_args = len(function.arguments)
        len_temp = function.temporary_variables
        is_local = False

        #Check local first
        #If constant
        if self.represents_int(var):
            self.add_command("li "+reg+","+var)
            is_local = True
        #elif local temporary variable
        elif temp_var != -1:
            offset = 12 + 4*len_args + 4*len_vars + 4*temp_var
            self.add_command("lw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif local variable
        elif var in function.variables:
            var_pos = function.variables.index(var)
            offset = 12 + 4*len_args + 4*var_pos
            self.add_command("lw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif argument cv or ref
        else:
            for i in range(0,len_args):
                arg = function.arguments[i]
                if var == arg[1]:
                    offset = 12 + 4*i #i = arguments position
                    if arg[0] == "in":
                        self.add_command("lw "+reg+",-"+str(offset)+"($sp)")
                    elif arg[0] == "inout":
                        self.add_command("lw $t0,-"+str(offset)+"($sp)")
                        self.add_command("lw "+reg+",($t0)")
                    is_local = True

        #if it is not local then if from a parent or from main(global)
        if is_local == False:
            where_belongs = self.gnvlcode(var,func_pos)

            #if where_belongs == 0 then it belongs to main(global)
            if where_belongs == 0:
                main = self.list_of_functions[0]
                offset = 12 + 4*main.variables.index(var)
                self.add_command("lw "+reg+",-"+str(offset)+"($s0)")
            #else if where_belongs == 1 then it is a local variable of a parent function
            #or if where_belongs == 2 then it is a "in" argument of a parent function
            elif where_belongs == 1 or where_belongs == 2:
                self.add_command("lw "+reg+",($t0)")
            #else(where_belongs == 3) then it is a "inout" argument of a parent function
            else:
                self.add_command("lw $t0,($t0)")
                self.add_command("lw "+reg+",($t0)")


    #Move data from register to memory
    def storerv(self,reg,var,func_pos):
        function = self.list_of_functions[func_pos]

        temp_var = -1
        t = var.split("_")
        if len(t) > 1:
            temp_var = int(t[1])

        len_vars = len(function.variables)
        len_args = len(function.arguments)
        len_temp = function.temporary_variables
        is_local = False

        #Check local first
        #if local temporary variable
        if temp_var != -1:
            offset = 12 + 4*len_args + 4*len_vars + 4*temp_var
            self.add_command("sw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif local variable
        elif var in function.variables:
            var_pos = function.variables.index(var)
            offset = 12 + 4*len_args + 4*var_pos
            self.add_command("sw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif argument cv or ref
        else:
            for i in range(0,len_args):
                arg = function.arguments[i]
                if var == arg[1]:
                    offset = 12 + 4*i #i = arguments position
                    if arg[0] == "in":
                        self.add_command("sw "+reg+",-"+str(offset)+"($sp)")
                    elif arg[0] == "inout":
                        self.add_command("lw $t0,-"+str(offset)+"($sp)")
                        self.add_command("sw "+reg+",($t0)")
                    is_local = True

        #if it is not local then if from a parent or from main(global)
        if is_local == False:
            where_belongs = self.gnvlcode(var,func_pos)

            #if where_belongs == 0 then it belongs to main(global)
            if where_belongs == 0:
                main = self.list_of_functions[0]
                offset = 12 + 4*main.variables.index(var)
                self.add_command("sw "+reg+",-"+str(offset)+"($s0)")
            #else if where_belongs == 1 then it is a local variable of a parent function
            #or if where_belongs == 2 then it is a "in" argument of a parent function
            elif where_belongs == 1 or where_belongs == 2:
                self.add_command("sw "+reg+",($t0)")
            #else(where_belongs == 3) then it is a "inout" argument of a parent function
            else:
                self.add_command("lw $t0,($t0)")
                self.add_command("sw "+reg+",($t0)")


    #Translate idermediate language to mips assembly
    def translate_int_to_ass(self):
        #First line is the jump to main line
        line = self.file_int.readline() #Read first line from idermediate language file
        line = line[:-1] #Remove the last character(\n)
        quad = line.split(":",1) #split only in first : (in case of := symbol)
        main_label = quad[1].split(",")[3]
        self.file_mips.write("L0:\n")
        self.add_command("b L"+main_label)

        #current_function,current_function_pos used to have easy access to the inforamation of the current function
        #in the array of symbols
        current_function = None
        current_function_pos = 0

        #This is used to know when the current function is the main
        in_main = False

        #This function_call_offset,function_call_pos,function_call_framelength are used then a function is called
        #Function is called when we see a some "par" in immediate code followed by "call" or a "call" alone.
        #if we have "par" then we find the function that will be called with find_function_pos(function_call_pos) and we add the frame lenght of it
        #(function_call_framelength) the function_call_offset is used to save the arguments in orderdatetime A combination of a date and a time. Attributes: ()
        #if alone "call" is found then function_call_offset no need the function is "procedure" with no arguments
        function_call_offset = 12
        function_call_pos = 0
        function_call_framelength = 0

        line = self.file_int.readline() #Read first line from idermediate language file
        line = line[:-1] #Remove the last character(\n)
        while line:
            quad = line.split(":",1) #split only in first : (in case of := symbol)
            label = quad[0]
            quad = quad[1].split(",")

            self.file_mips.write("L"+label+":\n")

            if label == main_label:
                in_main = True

            #Produce the appropriate MIPS code by intermediate code
            if quad[0] == "begin_block":
                current_function_pos = self.find_function_pos_sq(int(label))
                current_function = self.list_of_functions[current_function_pos]
                if in_main:
                    self.add_command("addi $sp,$sp,"+str(current_function.frame_length+12))
                    self.add_command("move $s0,$sp")
                else:
                    self.add_command("sw $ra,0($sp)")
            elif quad[0] == "end_block":
                if not in_main:
                    self.add_command("lw $ra,0($sp)")
                    self.add_command("jr $ra")
            elif quad[0] == "halt":
                self.add_command("")
            elif quad[0] == "jump":
                self.add_command("b L"+quad[3])
            elif quad[0] == "=" or quad[0] == "<" or quad[0] == ">" or quad[0] == "<=" or quad[0] == ">=" or quad[0] == "<>":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.loadvr(quad[2],"$t2",current_function_pos)
                branch = ""
                if quad[0] == "=":
                    branch = "beq"
                if quad[0] == "<":
                    branch = "blt"
                elif quad[0] == ">":
                    branch = "bgt"
                elif quad[0] == "<=":
                    branch = "ble"
                elif quad[0] == ">=":
                    branch = "bge"
                else:
                    quad[0] == "bne"

                self.add_command(branch+",$t1,$t2,"+"L"+quad[3])
            elif quad[0] == "+" or quad[0] == "-" or quad[0] == "*" or quad[0] == "/":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.loadvr(quad[2],"$t2",current_function_pos)
                op = ""
                if quad[0] == "+":
                    op = "add"
                elif quad[0] == "-":
                    op = "sub"
                elif quad[0] == "*":
                    op = "mul"
                elif quad[0] == "/":
                    op = "div"

                self.add_command(op+" $t1,$t1,$t2")
                self.storerv("$t1",quad[3],current_function_pos)
            elif quad[0] == ":=":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.storerv("$t1",quad[3],current_function_pos)
            elif quad[0] == "out":
                self.add_command("li $v0,1")
                self.loadvr(quad[1],"$a0",current_function_pos)
                self.add_command("syscall")
            elif quad[0] == "inp":
                self.add_command("li $v0,5")
                self.add_command("syscall")
                self.storerv("$v0",quad[1],current_function_pos)
            elif quad[0] == "retv":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.add_command("lw $t0,-8($sp)")
                self.add_command("sw $t1,($t0)")
            elif quad[0] == "par":

                if function_call_offset == 12:
                    temp_pos = self.file_int.tell()
                    function_call_pos = self.find_function_pos(quad,current_function_pos)
                    function_call_framelength = self.list_of_functions[function_call_pos].frame_length
                    self.file_int.seek(temp_pos)
                    self.add_command("addi $fp,$sp,"+str(function_call_framelength + 12))

                if quad[2] == "CV":
                    self.loadvr(quad[1],"$t0",current_function_pos)
                    self.add_command("sw $t0,-"+str(function_call_offset)+"($fp)")
                    function_call_offset += 4
                elif quad[2] == "REF":
                    arg_type,offset = self.find_variable_in_parent(quad[1],current_function_pos)
                    #if var or cv in current function then load its address in $t0
                    if arg_type == 0:
                        self.add_command("addi $t0,$sp,-"+str(offset))
                    #elif ref in current function then load its parent address in $t0
                    elif arg_type == 1:
                        self.add_command("lw $t0,-"+str(offset)+"($sp)")
                    #elif var or cv or ref in parent function
                    elif arg_type == 3:
                        where_belongs = self.gnvlcode(quad[1],current_function_pos)
                        if where_belongs == 3: #ref in another parent function
                            self.add_command("lw $t0,($t0)")
                        elif where_belongs == 0: #ref in variable in main(main does not have arguments)
                            offset = 12 + 4*self.list_of_functions[0].variables.index(quad[1])
                            self.add_command("addi $t0,$s0,-"+str(offset))

                    self.add_command("sw $t0,-"+str(function_call_offset)+"($fp)")
                    function_call_offset += 4
                elif quad[2] == "RET":
                    arg_type,offset = self.find_variable_in_parent(quad[1],current_function_pos)
                    self.add_command("addi $t0,$sp,-"+str(offset))
                    self.add_command("sw $t0,-8($fp)")
                    function_call_offset += 4

            elif quad[0] == "call":

                #procedure without arguments
                if function_call_offset == 12:
                    function_call_pos = self.find_function_pos(quad,current_function_pos)
                    function_call_framelength = self.list_of_functions[function_call_pos].frame_length
                    self.add_command("addi $fp,$sp,"+str(function_call_framelength + 12))

                #Save the access link
                #If called and calling function have the same nesting level then they have the same parent
                #else calling function is the parent of the called function
                if self.list_of_functions[function_call_pos].nesting_level == self.list_of_functions[current_function_pos]:
                    self.add_command("lw $t0,-4($sp)")
                    self.add_command("sw $t0,-4($fp)")
                else:
                    self.add_command("sw $sp,-4($fp)")

                self.add_command("addi $sp,$sp,"+str(function_call_framelength + 12))
                label_jal = "L" + str(self.list_of_functions[function_call_pos].starting_quad)
                self.add_command("jal "+label_jal)
                self.add_command("addi $sp,$sp,-"+str(function_call_framelength + 12))

                #Re-init
                function_call_offset = 12

            line = self.file_int.readline() #Read next line from idermediate language file
            line = line[:-1] #Remove the last character(\n)




#Helping functions

    #Add a command to mips file
    def add_command(self,command):
        self.file_mips.write("\t" + command + "\n")


    #Find the position of current function in array of symbols by starting quad
    def find_function_pos_sq(self,starting_quad):
        for i in range(0,len(self.list_of_functions)):
            function = self.list_of_functions[i]
            if function.starting_quad == starting_quad:
                return i

    #Helping function to see if a str is int
    def represents_int(self,str):
        try:
            int(str)
            return True
        except ValueError:
            return False

    #Finds the position in list_of_functions of the called function
    #pos : current function position
    #quad : the current quad
    #return function (that called by current function) position in the list_of_functions
    def find_function_pos(self,quad,func_pos):

        name = ""
        type_called = "procedure"
        arguments = []
        quad_ = quad
        if quad_[0] == "call":
            name = quad_[1]
        elif quad_[2] == "RET":
            type_called = "function"
            line = self.file_int.readline() #Read next line from idermediate language file
            line = line[:-1] #Remove the last character(\n)
            quad_ = line.split(":",1) #split only in first : (in case of := symbol)
            quad_ = quad_[1].split(",")
        else:
            while quad_[0] != "call":
                if quad_[0] == "par" and quad_[2] != "RET":
                    arguments.append(quad_[2])
                if quad_[2] == "RET":
                    type_called = "function"
                line = self.file_int.readline() #Read next line from idermediate language file
                line = line[:-1] #Remove the last character(\n)
                quad_ = line.split(":",1) #split only in first : (in case of := symbol)
                quad_ = quad_[1].split(",")

        name = quad_[1]
        function_pos = -1

        #If its main(pos == 0) then main can call all functions with nesting level == 1
        if func_pos == 0:
            for i in range(1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                        #If the arguments is the same then we find which function the main call
                        if self.check_same_args(arguments,function.arguments) == True:
                            function_pos = i
        #If its not main(pos > 0) then this function can call
        #1)Its own childen functions(all functions following it with nesting level of function + 1 until nesting level < nesting level of function)
        #2)Can call it self(recursive)
        #3)Can can all parent and brother functions(all functions in front of it until nesting level == 1 and after that only the functions in front of it with nesting level == 1)
        else:

            current_function = self.list_of_functions[func_pos]
            #Check all the childrens of the current function(if have any)
            for i in range(func_pos+1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                if function.nesting_level == (current_function.nesting_level + 1):
                    #If they have same name and type
                    if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                        #Check if the arguments are the same
                        if self.check_same_args(arguments,function.arguments) == True:
                            function_pos = i
                else:
                    #If we are here it means that no other children exist
                    break

            #Check calling itself
            if function_pos == -1:
                #If we are here it means that this function have no children or the children functions checked without find anything
                #Next thing is to check if the function call it self
                if name == current_function.name and type_called == current_function.type and len(arguments) == len(current_function.arguments):
                    if self.check_same_args(arguments,current_function.arguments) == True:
                        function_pos = func_pos

            #Check all the parents of the current function(if have any)
            if function_pos == -1:
                #If we are here it means that this function have no children or the children functions checked without find anything and did not call it self
                #Last thing is to check if the function call a parent function
                nl_1_found = False #This variable is used to check when a parent with nesting level(nl) 1 is found,so only parents with nl=1 can now be called
                for i in range(func_pos-1,0,-1):
                    function = self.list_of_functions[i]
                    if function.nesting_level == 1:
                        nl_1_found = True
                    if ((function.nesting_level <= current_function.nesting_level) and (nl_1_found == False)) or ((function.nesting_level == 1) and (nl_1_found == True)):
                        #If they have same name and type
                        if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                            #Check if the arguments are the same
                            if self.check_same_args(arguments,function.arguments) == True:
                                function_pos = i

        return function_pos



    #Private function to check if arguments are the same(used between comparison of two functions)(used only in undeclared_fun_or_proc)
    #eg args1=['in','inout'] and args2=[['CV',x],['REF',y]] is same
    def check_same_args(self,args1,args2):
        same_args = True
        for i in range(0,len(args1)):
            if (args1[i] == "in" and args2[i] != "CV") or (args1[i] == "inout" and args2[i] != "REF"):
                same_args = False
                break
        return same_args


    #Find variable in parent function(used for stack)
    #return 0,offset if var is local or CV
    #return 1,offset if var is REF
    #return 2,offset is temporary variable
    #if it belong to a parent of the parent then is return 3,0
    def find_variable_in_parent(self,var,parent_pos):
        current_function = self.list_of_functions[parent_pos]

        offset = 12
        len_args = len(current_function.arguments)
        for i in range(0,len_args):
            par_arg = current_function.arguments[i]
            if par_arg[1] == var:
                offset += 4*i
                if par_arg[0] == "in":
                    return 0,offset
                else: #REF
                    return 1,offset

        len_vars = len(current_function.variables)
        for i in range(0,len_vars):
            par_var = current_function.variables[i]
            if par_var == var:
                offset += 4*len_args + 4*i
                return 0,offset

        if var.split("_")[0] == "T":
            offset += 4*len_args + 4*len_vars + 4*int(var.split("_")[1])
            return 2,offset

        #If here then the variable is belong to a parent of this parent function
        return 3,0

#-----------------------------------------------------------------------------------------------


#Syntactic analysis
#-----------------------------------------------------------------------------------------------
class synt:

    def __init__(self, file_name, save_temps):
        self.error_handler = error_handler
        self.lex = lex(file_name,self.error_handler)
        self.inLan = int_lang(file_name)
        self.ao_symbols = array_of_symbols(file_name)
        self.error_handler.set_inLan(self.inLan)
        self.error_handler.set_lex(self.lex)
        self.error_handler.set_aos(self.ao_symbols)
        self.exit_can_used = False #exit command can be used only inside loop
        self.aos_pos = -1 #Position in array of symbol of this function(used for aos class)
        self.program()

        #Free some memory(no need them anymore)
        del self.lex
        del self.error_handler
        gc.collect() #Force garbage collector to free memory

        #Save array of symbols and idermediate language
        self.ao_symbols.calc_framelength()
        self.ao_symbols.write_aos()
        self.ao_symbols.close()
        self.inLan.close()

        #Create Assembly MIPS
        self.mips_ass = mips_assembly(file_name,self.ao_symbols.list_of_functions)

        #Create C and MIPS code
        if save_temps == False:
            self.inLan.delete()
            self.ao_symbols.delete()
        else:
            self.createC = create_c_code(file_name,self.ao_symbols.list_of_functions)


    def program(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "program", Id.IDENTIFIER,word, ID)
        block_name, ID = self.lex.start_read()  # program name
        self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
        self.ao_symbols.add_function(block_name,"main",[]) #Create a program(main) object for array of symbols
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "{", Id.GROUPING, word, ID)
        self.block(block_name)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "}", Id.GROUPING, word, ID)
        self.error_handler.warning_handle(warning_types.ReturnStatementCheck, self.inLan.return_statement, "main", block_name)
        self.inLan.return_statement = -1

    def block(self,block_name):
        self.inLan.make_list(block_name) #IL:Create a list for all the quads of this function(or procedure or function)
        temp_aos_pos = self.ao_symbols.current_function_pos #Position in array of symbol of this function(used for aos class)
        self.declarations()
        self.subprograms()
        self.aos_pos = temp_aos_pos
        self.statements()
        self.ao_symbols.set_temp_variables(self.inLan.temp_var_value, self.aos_pos)
        self.inLan.reset_newtemp() #Reset temporary values so a new function can use them
        label_start = self.inLan.write_list() #IL:Write the list of quads of this function(or procedure or function)
        self.ao_symbols.set_starting_quad(label_start, self.aos_pos)
        self.ao_symbols.undo_nesting_level()#Set the nesting level of the previous function


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
        ad_var = self.ao_symbols.add_variable(word) #Append the variable list of the current function
        self.error_handler.error_handle(error_types.RedeclaredVariable, ad_var, word, self.ao_symbols.current_function_name(self.aos_pos))
        word, ID = self.lex.start_read()
        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, ",", Id.SEPERATOR, word, ID):
            word, ID = self.lex.start_read()  # variable in varlist
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            ad_var = self.ao_symbols.add_variable(word) #Append the variable list of the current function
            self.error_handler.error_handle(error_types.RedeclaredVariable, ad_var, word, self.ao_symbols.current_function_name(self.aos_pos))
            word, ID = self.lex.start_read()  # expected comma
        self.lex.undo_read()
        self.varlist()

    def subprograms(self):
        while self.subprogram():
            pass

    def subprogram(self):
        function_type, ID = self.lex.start_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "function", Id.IDENTIFIER, function_type, ID) or self.error_handler.error_handle(error_types.SyntaxCheckWordId, "procedure", Id.IDENTIFIER, function_type, ID):
            block_name, ID = self.lex.start_read()  # Name of fuction or procedure
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            self.funcbody(block_name,function_type)
            self.error_handler.warning_handle(warning_types.ReturnStatementCheck, self.inLan.return_statement, function_type, block_name)
            self.inLan.return_statement = -1
            return True
        self.lex.undo_read()
        return False

    def funcbody(self,block_name,function_type):
        self.formalpars()
        function_arguments = self.ao_symbols.get_temporary_arguments()
        error_check = self.ao_symbols.add_function(block_name,function_type,function_arguments)  #Add this function or procedure the array of symbols
        self.error_handler.error_handle(error_types.RedeclaredFuncOrProc, error_check, function_type, block_name) #Check if its redeclared in same nesting level
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
            self.ao_symbols.add_temporary_argument(in_or_inout,word) #Append the arguments list of the current function
        else:
            self.error_handler.error_handle(error_types.SyntaxWordFatal, "in or inout", in_or_inout)  # Error exit

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
        elif word == "exit" and self.exit_can_used == True:
            word, ID = self.lex.start_read()
            self.inLan.exit_statement = True
            self.inLan.genquad("exit","_","_","_")
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
            un_var = self.ao_symbols.undeclared_variable(assign, self.aos_pos) #Check for undeclared variable
            self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,assign,self.ao_symbols.current_function_name(self.aos_pos))
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":=", Id.EQUAL, word, ID)
        x = self.expression()
        self.inLan.genquad(":=",x,"_",assign)

    def if_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "if", Id.IDENTIFIER, word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

        if_cond_start_pos = self.inLan.relative_function_pos() #IL:starting position of if statement
        exp_list = self.condition(False) #IL:get the condition quads
        self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code
        self.inLan.add_condition(exp_list,if_cond_start_pos) #IL:add the condition to the code
        if_cond_end_pos = self.inLan.relative_function_pos() #IL:starting position of if statement

        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "then", Id.IDENTIFIER, word, ID)

        self.statements()

        jump_false = self.inLan.relative_function_pos() - if_cond_end_pos + 1
        if self.elsepart():
            jump_false += 1
        self.inLan.backpatch(jump_false,if_cond_start_pos,if_cond_end_pos,"JUMP-FALSE")

    def elsepart(self):
        word, ID = self.lex.start_read()
        else_begin_pos = self.inLan.relative_function_pos() #IL:Get the begin address outside if statement
        #IL:If we have else outside if then we add a jump quad(for jump outside else if the if is true)
        #add add statements.Either we have else or not we return the position outside if.
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "else", Id.IDENTIFIER, word, ID):
            self.inLan.genquad("jump","_","_","_") #IL:add jump at the end of if
            self.statements() #IL:add new statements inside else
            outside_if = self.inLan.relative_function_pos() - else_begin_pos #IL:calculate the relative position for the jump quad to jump
            self.inLan.functions_list[-1][else_begin_pos] = "jump,_,_,+"+str(outside_if) #IL:edit the jump quad and add the relative position
            return True
        else:
            self.lex.undo_read()
            return False

    def while_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "while", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

        while_cond_start_pos = self.inLan.relative_function_pos() #IL:starting position of while statement
        exp_list = self.condition(False) #IL:get the condition quads
        self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code
        self.inLan.add_condition(exp_list,while_cond_start_pos) #IL:add the condition to the code
        while_cond_end_pos = self.inLan.relative_function_pos() #IL:ending position of while statement

        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)

        self.statements()

        jump_false = self.inLan.relative_function_pos() - while_cond_end_pos + 2 #IL:get the position outside while
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
        temp_val_address = self.inLan.relative_function_pos() #IL:Get position of the quad below
        self.inLan.genquad(":=","0","_",temp_var) #IL:Give value 0 in the temp value

        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

        cond_start_pos = self.inLan.relative_function_pos()
        cond = self.condition(False)
        self.inLan.backpatch(cond,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code
        self.inLan.add_condition(cond,cond_start_pos) #IL:add the condition to the code
        cond_end_pos = self.inLan.relative_function_pos()

        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word, ID)

        #1st statement
        start_stat1 = self.inLan.relative_function_pos()
        self.inLan.genquad("=",temp_var,"2","exitDW") #Create the if for stat1
        self.statements()
        self.inLan.genquad(":=","1","_",temp_var) #Set temp var = 1
        jump_to_cond = self.inLan.relative_function_pos() - cond_start_pos
        self.inLan.genquad("jump","_","_","-"+str(jump_to_cond)) #IL:Jump to condition from stat1


        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "else", Id.IDENTIFIER, word, ID)

        #Set condition jump to false
        jump_false = self.inLan.relative_function_pos() - cond_end_pos + 1
        self.inLan.backpatch(jump_false,cond_start_pos,cond_end_pos,"JUMP-FALSE")

        #2nd statement
        start_stat2 = self.inLan.relative_function_pos()
        self.inLan.genquad("=",temp_var,"1","exitDW") #Create the if for stat2
        self.statements()
        self.inLan.genquad(":=","2","_",temp_var) #Set temp var = 2
        jump_to_cond = self.inLan.relative_function_pos() - cond_start_pos
        self.inLan.genquad("jump","_","_","-"+str(jump_to_cond)) #IL:Jump to condition frpm stat2

        #Set the "exitDW" of quads to this position(outside doublewhile)
        jump_to_cond1 = self.inLan.relative_function_pos() - start_stat1
        jump_to_cond2 = self.inLan.relative_function_pos() - start_stat2
        self.inLan.special_doublewhile(start_stat1,jump_to_cond1)
        self.inLan.special_doublewhile(start_stat2,jump_to_cond2)



    def loop_stat(self):
        self.exit_can_used  = True
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "loop", Id.IDENTIFIER, word,ID)
        self.inLan.exit_statement = False

        loop_start_pos = self.inLan.relative_function_pos()
        self.statements()
        loop_end_pos = self.inLan.relative_function_pos()
        jump_beginning = loop_end_pos - loop_start_pos
        self.inLan.genquad("jump","_","_","-"+str(jump_beginning))
        self.inLan.special_loop(loop_start_pos,loop_end_pos)
        self.error_handler.warning_handle(warning_types.NoExitLoop,self.inLan.exit_statement, self.ao_symbols.current_function_name(self.aos_pos))
        self.inLan.exit_statement = False
        self.exit_can_used  = False

    def forcase_stat(self):
        word, ID = self.lex.start_read()
        self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "forcase", Id.IDENTIFIER,word, ID)
        word, ID = self.lex.start_read()

        forcase_start_pos = self.inLan.relative_function_pos() #IL:Get the starting position of forcase

        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "when", Id.IDENTIFIER, word, ID):

            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

            cond_start_pos = self.inLan.relative_function_pos()
            exp_list = self.condition(False)
            self.inLan.backpatch(exp_list,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code
            self.inLan.add_condition(exp_list,cond_start_pos) #IL:add the condition to the code
            cond_end_pos = self.inLan.relative_function_pos() #IL:ending position of while statement

            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word,ID)
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":", Id.SEPERATOR, word,ID)

            self.statements()

            jump_to_begin = self.inLan.relative_function_pos() - forcase_start_pos #IL:positions from beginning of forcase
            self.inLan.genquad("jump","_","_","-"+str(jump_to_begin))
            jump_false = self.inLan.relative_function_pos() - cond_end_pos + 1
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
        temp_val_address = self.inLan.relative_function_pos() #IL:Get position of the quad below
        self.inLan.genquad(":=","0","_",temp_var) #IL:Give value 0 in the temp value

        while self.error_handler.error_handle(error_types.SyntaxCheckWordId, "when", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, "(", Id.GROUPING, word, ID)

            cond_start_pos = self.inLan.relative_function_pos()
            cond = self.condition(False)
            self.inLan.backpatch(cond,"true","DISTANCE","RELOP") #IL:set the relops of condition quads that jump to true code
            self.inLan.add_condition(cond,cond_start_pos) #IL:add the condition to the code
            cond_end_pos = self.inLan.relative_function_pos()

            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ")", Id.GROUPING, word,ID)
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxCheckWordIdFatal, ":", Id.SEPERATOR, word,ID)

            self.statements()
            self.inLan.genquad(":=","1","_",temp_var) #IL:Set temp var value to 1

            jump_false = self.inLan.relative_function_pos() - cond_end_pos + 1
            self.inLan.backpatch(jump_false,cond_start_pos,cond_end_pos,"JUMP-FALSE")

            word, ID = self.lex.start_read()

        jump_to_begin = self.inLan.relative_function_pos() - temp_val_address #IL:positions from beginning of incase
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
        error_id = self.ao_symbols.undeclared_fun_or_proc(proc_name,"procedure",arguments,self.aos_pos)
        self.error_handler.error_handle(error_types.UndeclaredFuncOrProc, error_id,"procedure",proc_name,self.ao_symbols.current_function_name(self.aos_pos))
        self.inLan.genquad("call",proc_name,"_","_")

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
        un_var = self.ao_symbols.undeclared_variable(word, self.aos_pos) #Check for undeclared variable
        self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,word,self.ao_symbols.current_function_name(self.aos_pos))
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
                un_var = self.ao_symbols.undeclared_variable(w, self.aos_pos) #Check for undeclared variable
                self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,w,self.ao_symbols.current_function_name(self.aos_pos))
            self.inLan.genquad("par",w,"CV","_")
            return "in"
        elif self.error_handler.error_handle(error_types.SyntaxCheckWordId, "inout", Id.IDENTIFIER, word, ID):
            word, ID = self.lex.start_read()
            self.error_handler.error_handle(error_types.SyntaxIdFatal, Id.IDENTIFIER, ID)
            un_var = self.ao_symbols.undeclared_variable(word, self.aos_pos) #Check for undeclared variable
            self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,word,self.ao_symbols.current_function_name(self.aos_pos))
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
            start_address = self.inLan.relative_function_pos()
            x = self.expression()
            relop = self.relational_oper()
            y = self.expression()
            if enable_not :
                self.inLan.genquad(self.inLan.reverse_relop(relop),x,y,"_")
            else:
                self.inLan.genquad(relop,x,y,"_")
            end_address = self.inLan.relative_function_pos()
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
                    un_var = self.ao_symbols.undeclared_variable(word, self.aos_pos) #Check for undeclared variable
                    self.error_handler.error_handle(error_types.UndeclaredVariable, un_var,word,self.ao_symbols.current_function_name(self.aos_pos))
            return word

    def idtail(self,fun_name):
        word, ID = self.lex.start_read()
        self.lex.undo_read()
        if self.error_handler.error_handle(error_types.SyntaxCheckWordId, "(", Id.GROUPING, word, ID):
            arguments = self.actualpars()
            error_id = self.ao_symbols.undeclared_fun_or_proc(fun_name,"function",arguments,self.aos_pos)
            self.error_handler.error_handle(error_types.UndeclaredFuncOrProc, error_id,"function",fun_name,self.ao_symbols.current_function_name(self.aos_pos))
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

#-----------------------------------------------------------------------------------------------



#MLC-main
#-----------------------------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------------------------
