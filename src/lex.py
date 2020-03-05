#!/usr/bin/python3

from errors import error_types, error_handler
from finite_automata import State, Symbols, automata_states

class Lex:

    def __init__(self, file_name):
        try:
            self.file = open(file_name, "r")
            self.file_index = 0
            self.file_line = 1
        except FileNotFoundError:
            error_handler(error_types.FileNotFound, file_name)

    def next_char(self):
        c = self.file.read(1)
        if c:
            self.file_index += 1
            if c == "/n":
                self.file_line += 1
        return c

    def start_automata(self):
        current_state = State.INITIAL
        word = ""
        while current_state != State.FINAL:
            #Get next character
            position = self.file.tell()
            c = self.next_char()

            #Special occasions
            if c == "" and current_state != State.INITIAL:
                error_handler(error_types.UnexpectedEnd, self.file_line)
            elif c == "" and current_state == State.INITIAL:
                return None #RETURN None when EOF
            elif c not in Symbols.ALL:
                error_handler(error_types.UnexpectedChar, self.file_line)

            #Find the next state in finite automata
            for next_state in automata_states[current_state]:
                if c in next_state["condition"]:
                    #Get the next state
                    current_state  = next_state["next_state"]

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
            return word
        else:
            return self.start_automata() #We end up here only in COMMENTS case
