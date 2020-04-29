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
    RedaclaredVariable = 12     #Check for redeclared variable,fatal error if false
    UndeclaredFuncOrProc = 13   #Check for undeclared function or procedure,fatal error if false
    ReturnStatementCheck = 14   #Check if we have at least one return(function) or no return(procedure)

class warning_types(Enum):
    NoExitLoop = 1              #Used when no exit statement found at loop statement

class error_handler:

    def __init__(self):
        self.inLan = None #IntLang class is used to to delete the idermediate file in case of error or to take some info from array of symbols
        self.lex = None #Lex class is used to define number of line the error found

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
    #UndeclaredVariable: args[0] = check(boolean),args[1] = variable,args[2] = program_that_contain_this_variable
    #RedeclaredVariable: args[0] = check(boolean),args[1] = variable,args[2] = program_that_contain_this_variable
    #UndeclaredFuncOrProc: args[0] = number_of_error,args[1] = type(function or procedure),args[2] = name(of function or procedure),args[3] = program_contain_this_func_or_proc
    #ReturnStatementCheck: args[0] = number_of_line_found_return_or_-1_if_not_found,args[1] = type(function or procedure),args[2] = name(of function or procedure)
    def error_handle(self,error_type, *args):
        if error_type == error_types.FileArgument:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " File argument not passed!")
        elif error_type == error_types.FileNotFound:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " File "+str(args[0])+" not found!")
        elif error_type == error_types.UnexpectedEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected end at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.UnexpectedChar:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected character at index "+str(args[0])+" in line "+str(self.lex.file_line)+".")
        elif error_type == error_types.UnexpectedCommentEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected comment end at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.WrongFilePrefix:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Wrong file prefix expected: .min but find:"+str(args[0]))
        
        elif error_type == error_types.IntegerOutOfRange:
            try:
                x = int(args[0])
                if x > 32767 or x < -32767:
                    print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Integer out of range, at line "+str(self.lex.file_line)+".")
                return True 
            except ValueError:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected: Integer, and find:"+str(args[0])+", at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.SyntaxCheckWordIdFatal:
            if(args[0] != args[2] or args[1] != args[3]):
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(args[0])+" but find:"+str(args[2])+" , at line "+str(self.lex.file_line)+".")
            else:
                return True
        elif error_type == error_types.SyntaxCheckWordId:
            if(args[0] != args[2] or args[1] != args[3]):
                return False
            return True
        elif error_type == error_types.SyntaxIdFatal:
            if args[0] != args[1]:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(args[0])+", and find:"+str(args[1])+", at line "+str(self.lex.file_line)+".")
            else:
                return True
        elif error_type == error_types.SyntaxWordFatal:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(args[0])+", and find:"+str(args[1])+", at line "+str(self.lex.file_line)+".")
        elif error_type == error_types.UndeclaredVariable:
            if args[0] == True:
                return True
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Undeclared variable: " + args[1] + " ,belong to: "+ args[2] + " ,at line:" + str(self.lex.file_line))
        elif error_type == error_types.RedaclaredVariable:
            if args[0] == True:
                return True
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Redeclared variable: " + args[1] + " ,belong to: "+ args[2] + " ,at line:" + str(self.lex.file_line))
        elif error_type == error_types.UndeclaredFuncOrProc:
            if args[0] == 0:
                return True
            if args[0] == 1:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + "undeclared first use of " + args[1] + " "+ args[2] + " ,at line:" + str(self.lex.file_line))
            elif args[0] == 2:
                proc_or_fun = "procedure"
                if proc_or_fun == args[1]:
                    proc_or_fun = "function"
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + proc_or_fun +" " + args[2] + " called as " + args[1] + " ,at line:" + str(self.lex.file_line))
            elif args[0] == 3:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + "wrong number of arguments for "+args[1]+" "+args[2]+ " ,at line:" + str(self.lex.file_line))
            elif args[0] == 4:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + args[1] + " " + args[2]+ " wrong type of argument "  + ", at line:" + str(self.lex.file_line))
        elif error_type == error_types.ReturnStatementCheck:
            if args[0] == -1 and args[1] == "function" :
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"no return statement found at function "+args[2])
            elif args[0] != -1 and args[1] == "procedure":
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"return statement found at procedure "+args[2]+ ", at line:" + str(args[0]))
            elif args[0] != -1 and args[1] == "main":
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"return statement found at main program "+args[2]+ ", at line:" + str(args[0]))
            else:
                return True
        else:
            #Normally we not end up here,except the error_type is not defined
            print(bcolors.FAIL+bcolors.BOLD+bcolors.UNDERLINE+"mlc error:"+bcolors.ENDC +"Undefined error!")
            
        self.exit_program() #If we get here a fatal error occur

    #NoExitLoop: arg[0] = check_if_exist(boolean), args[1] = name_of_program
    def warning_handle(self,warning_type,*args):
        if warning_type == warning_types.NoExitLoop:
            if args[0] == False:
                print(bcolors.WARNING+"mlc warning:"+bcolors.ENDC +"no exit statement found at loop at "+args[1])


    #This function used when an error occur and the idermediate file exist,so it delete it
    def exit_program(self):
        if self.inLan != None:
            self.inLan.delete()
        exit()

    #Error handler need Idermediate Language object to delete the idermediate file if an error occur
    def set_inLan(self,inlan):
        self.inLan = inlan

    #Error handler need Lexer object to define the number of line an error occur
    def set_lex(self,lex):
        self.lex = lex