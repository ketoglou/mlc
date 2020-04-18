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

    def __init__(self, intermediate_lan):
        self.inLan = intermediate_lan

    def file_lex_error_handler(self,error_type, *args):
        if error_type == file_lex_error_types.FileArgument:
            print(bcolors.FAIL+bcolors.BOLD+"mlc file error:"+bcolors.ENDC +
                " File argument not passed!")
        elif error_type == file_lex_error_types.FileNotFound:
            print(bcolors.FAIL+bcolors.BOLD+"mlc file error:"+bcolors.ENDC +
                " File "+str(args[0])+" not found!")
        elif error_type == file_lex_error_types.UnexpectedEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected end at line "+str(args[0])+".")
        elif error_type == file_lex_error_types.UnexpectedChar:
            print(bcolors.FAIL+bcolors.BOLD+"mlc lectical error:"+bcolors.ENDC +
                " Unexpected character at index "+str(args[1])+" in line "+str(args[0])+".")
        elif error_type == file_lex_error_types.UnexpectedCommentEnd:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +
                " Unexpected comment end at line "+str(args[0])+".")
        self.exit_program()




    def syntax_error_word_id(self,expected_word, expected_id, word, id, line):
        if(expected_word != word or expected_id != id):
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(expected_word)+" but find:"+str(word)+" , at line "+str(line)+".")
            self.exit_program()
        return True

    def syntax_error_id(self,expected_id,id,line):
        if expected_id != id:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(expected_id)+", and find:"+str(id)+", at line "+str(line)+".")
            self.exit_program()
        return True

    def syntax_error(self,expected_word, expected_id, word, id):
        if(expected_word != word or expected_id != id):
            return False
        return True

    #Check if the constant is integer and if its in range
    def syntax_int_error(self,word,line):
        try:
            x = int(word)
            if x > 32767:
                print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +"Integer out of range, at line "+str(line)+".")
                self.exit_program()
        except ValueError:
            print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected: Integer, and find:"+str(word)+", at line "+str(line)+".")
            self.exit_program()
        return True

    def syntax_general_error(self,expected_word,word,line):
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +" Expected:"+str(expected_word)+", and find:"+str(word)+", at line "+str(line)+".")
        self.exit_program()

    def error_message(self,message):
        print(bcolors.FAIL+bcolors.BOLD+"mlc error:"+bcolors.ENDC +message)
        self.exit_program()

    def exit_program(self):
        self.inLan.delete()
        exit()