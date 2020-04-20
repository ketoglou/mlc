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


class file_lex_error_types(Enum):
    FileArgument = 0
    FileNotFound = 1
    UnexpectedEnd = 2
    UnexpectedChar = 3
    UnexpectedCommentEnd = 4

class Error_handler:

    def __init__(self):
        self.inLan = None #IntLang class is used to to delete the idermediate file in case of error or to take some info from array of symbols
        self.lex = None #Lex class is used to define number of line the error found

    #This error function used for simple file errors in file
    def file_lex_error_handler(self,error_type, *args):
        if error_type == file_lex_error_types.FileArgument:
            print(bcolors.FAIL+bcolors.BOLD+"mlc file error:"+bcolors.ENDC +
                " File argument not passed!")
        elif error_type == file_lex_error_types.FileNotFound:
            print(bcolors.FAIL+bcolors.BOLD+"mlc file error:"+bcolors.ENDC +
                " File "+str(args[0])+" not found!")
        elif error_type == file_lex_error_types.UnexpectedEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected end at line "+str(self.lex.file_line)+".")
        elif error_type == file_lex_error_types.UnexpectedChar:
            print(bcolors.FAIL+bcolors.BOLD+"mlc lectical error:"+bcolors.ENDC +
                " Unexpected character at index "+str(args[0])+" in line "+str(self.lex.file_line)+".")
        elif error_type == file_lex_error_types.UnexpectedCommentEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected comment end at line "+str(self.lex.file_line)+".")
        self.exit_program()



    #This error function used  to check word and ID matching ,used if we want exact match
    def syntax_error_word_id(self,expected_word, expected_id, word, id):
        if(expected_word != word or expected_id != id):
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(expected_word)+" but find:"+str(word)+" , at line "+str(self.lex.file_line)+".")
            self.exit_program()
        return True

    #This error function used  only ID matching,used in case of other IDs can exist
    def syntax_error_id(self,expected_id,id):
        if expected_id != id:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(expected_id)+", and find:"+str(id)+", at line "+str(self.lex.file_line)+".")
            self.exit_program()
        return True

    #This error function used to check word and ID matching,used in case of other word,IDs can exist
    def syntax_error(self,expected_word, expected_id, word, id):
        if(expected_word != word or expected_id != id):
            return False
        return True

    #This error function used to check if the constant is integer and if its in range of minimal++
    def syntax_int_error(self,word):
        try:
            x = int(word)
            if x > 32767:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Integer out of range, at line "+str(self.lex.file_line)+".")
                self.exit_program()
        except ValueError:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected: Integer, and find:"+str(word)+", at line "+str(self.lex.file_line)+".")
            self.exit_program()
        return True

    #This error function used to throw error message about what it was expected
    def syntax_general_error(self,expected_word,word):
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(expected_word)+", and find:"+str(word)+", at line "+str(self.lex.file_line)+".")
        self.exit_program()

    #This error function used to throw message about undeclared variable
    def undeclared_variable_error(self,check,var,prog):
        if check == False:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Undeclared variable: " + var + " ,belong to: "+ prog + " ,at line:" + str(self.lex.file_line))
            self.exit_program()

    #This error function used to throw message about undeclared or problimatic function or procedure
    def undeclared_fun_or_proc(self,num_of_error,type_,name,current_pr):
        if num_of_error == 0:
            return
        if num_of_error == 1:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + "undeclared first use of " + type_ + " "+ name + " ,at line:" + str(self.lex.file_line))
        elif num_of_error == 2:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + "undeclared " + type_ + " " + name +" in "+ current_pr +" but declared in " + self.inLan.belong_to[name] + ", at line:" + str(self.lex.file_line))
        elif num_of_error == 3:
            proc_or_fun = "procedure"
            if proc_or_fun == type_:
                proc_or_fun = "function"
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + proc_or_fun +" " + name + " called as " + type_ + " ,at line:" + str(self.lex.file_line))
        elif num_of_error == 4:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + "wrong number of arguments for "+type_+" "+name+ " ,at line:" + str(self.lex.file_line))
        elif num_of_error == 5:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC + type_ + " " + name+ " wrong type of argument "  + ", at line:" + str(self.lex.file_line))
        self.exit_program()

    ##This error function used to throw generla error messages
    def error_message(self,message):
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +message)
        self.exit_program()

    ##This function used when an error occur and the idermediate file exist,so it delete it
    def exit_program(self):
        if self.inLan != None:
            self.inLan.delete()
        exit()

    def set_inLan(self,inlan):
        self.inLan = inlan

    def set_lex(self,lex):
        self.lex = lex