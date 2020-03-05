#!/usr/bin/python3

from errors import file_lex_error_types, file_lex_error_handler
from finite_automata import State, Symbols, automata_states

class Lex:

    def __init__(self, file_name):
        try:
            self.file = open(file_name, "r")
            self.file_index = 0
            self.file_line = 1
            self.previous_pos = 0
        except FileNotFoundError:
            file_lex_error_handler(file_lex_error_types.FileNotFound, file_name)

    def next_char(self):
        c = self.file.read(1)
        if c:
            self.file_index += 1
            if c == "\n":
                self.file_index = 0
                self.file_line += 1
        return c

    def undo_read(self):
        self.file.seek(self.previous_pos)

    def start_read(self):
        self.previous_pos = self.file.tell()
        current_state = State.INITIAL
        word = ""
        ID = None
        while current_state != State.FINAL:
            #Get next character
            position = self.file.tell()
            c = self.next_char()

            #Special occasions
            if c == "" and current_state != State.INITIAL:
                file_lex_error_handler(file_lex_error_types.UnexpectedEnd, self.file_line)
            elif c == "" and current_state == State.INITIAL:
                return (None,None) #RETURN None when EOF
            elif c not in Symbols.ALL:
                file_lex_error_handler(file_lex_error_types.UnexpectedChar, self.file_line,self.file_index)

            #Find the next state in finite automata
            for next_state in automata_states[current_state]:
                if c in next_state["condition"]:
                    #Get the next state
                    current_state  = next_state["next_state"]

                    #Get the id if is done
                    if current_state == State.FINAL or current_state == State.FINAL_BLANK or current_state == State.FINAL_COMMENT:
                        ID = next_state["id"]

                    #If must,give back the character the previous state take to make checks.
                    if next_state["go_back"] == True:
                        self.file.seek(position)
                        break
                    
                    #Check if we must append the word or not
                    if current_state  != State.INITIAL and current_state != State.FINAL_BLANK and current_state != State.FINAL_COMMENT:
                        word = word+c
                        break
                    #If we have blanks,ignore them and dont append the word
                    elif current_state == State.FINAL_BLANK:
                        current_state = State.FINAL
                        break
                    #If we have comments,ignore the next characters
                    elif current_state == State.FINAL_COMMENT:
                        current_state = State.FINAL
                        word = ""
                        break              

        if word != "":
            return (word,ID)
        else:
            return self.start_read() #We end up here only in COMMENTS case
