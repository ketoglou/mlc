#!/usr/bin/python3

import sys
import os


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
    #Anonther mode is the "JUMP-FALSE" which is usually used when we know where in the code is a condition
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