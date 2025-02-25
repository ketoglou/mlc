#!/usr/bin/python3

from enum import Enum

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