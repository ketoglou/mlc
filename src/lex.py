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

            position = self.file.tell()-1
            c = self.next_char()
            while c == " " or c == "\t" or c == "\n":
                position = self.file.tell()-1
                c = self.next_char()

            if c == "" and current_state != State.INITIAL:
                error_handler(error_types.UnexpectedEnd, self.file_line)
            elif c == "" and current_state == State.INITIAL:
                return None #RETURN None when EOF
            elif c not in Symbols.ALL:
                error_handler(error_types.UnexpectedChar, self.file_line)

            for next_state in automata_states[current_state]:
                if c in next_state["condition"]:
                    current_state  = next_state["next_state"]
                    if next_state["go_back"] == True:
                        self.file.seek(position)
                        break
                    elif current_state  == State.COMMENT_ONE_LINE or current_state  == State.COMMENT_MULTIPLE_LINES:
                        while current_state  != State.FINAL:
                            c = self.next_char()
                            if c == "":
                                error_handler(error_types.UnexpectedCommentEnd, self.file_line)
                            elif c in next_state["condition"]:
                                current_state  = next_state["next_state"]
                        current_state  = State.INITIAL
                    if current_state  != State.INITIAL:
                        word = word+c
                    else:
                        word = ""
                    print(word)

        return word
