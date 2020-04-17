#!/usr/bin/python3

import sys
import os

class IntLang:
    
    def __init__(self, file_name):
        self.fd_name = file_name[0:-4] + ".int"
        self.fd = open(self.fd_name,"w+") #Create the file that we will store the idermediate code
        self.temp_var_value = 0 #Used to calculate temporary values
        #Create a list of lists,every list in this list is a procedure or function.
        #The first list in this list is the program.Every list have the quad of the current program or function or procedure.
        self.programs_list = [] 
        self.quad_number = 1 #Counts the next quad number

    #Get the current position of a quad in array
    def relative_program_pos(self):
        return len(self.programs_list[-1])

    #Gives the next quad number
    def nextquad(self):
        self.quad_number  += 1
        return (self.quad_number - 1)

    #Creates a list for a program or function or procedure with the first quad to be the name
    def make_list(self,block_name):
        quad_start = "begin_block,"+block_name+",_,_"
        quad_end = "end_block,"+block_name+",_,_"
        program = [quad_start,quad_end]
        self.programs_list.append(program)

    #If a program or function or procedure end then we write all of its quads
    #every relop or jump quad may have a relative to their position jump
    #eg jump,_,_,+5 it means that when this quad get its position i will jump to +5 from it
    #so the new quad (lets say it is 110) will be 110:jump,_,_,105
    def write_list(self):
        if len(self.programs_list) > 0:
            li = self.programs_list[-1] #Get the current program or function or procedure list
            begin_block_num = self.nextquad() #Get the quad number
            self.fd.write(str(begin_block_num)+":"+li[0]+"\n") #Write begin_block
            #Write all the quads of this program or function or procedure
            for quad in range(2,len(li)):
                quad_num = self.nextquad()
                squad = li[quad].split(",")
                if list(squad[-1])[0] == "+":
                    squad[-1] = str(quad_num + int(squad[-1].split("+")[1]))
                    li[quad] = ",".join(squad)
                self.fd.write(str(quad_num)+":"+li[quad]+"\n")
            #if we are in the main program then write halt before end_block
            if len(self.programs_list) == 1:
                self.fd.write(str(self.nextquad())+":halt,_,_,_\n")  #write halt
                self.write_first_line("0:jump,_,_,"+str(begin_block_num+1)+"\n")  #write jump to main
            self.fd.write(str(self.nextquad())+":"+li[1]+"\n")  #write end_block
            del self.programs_list[-1] #remove last list

    #Creates next quad for the current program(or function or procedure)
    def genquad(self,op,x,y,z):
        quad = op+","+x+","+y+","+z
        self.programs_list[-1].append(quad)

    #Return the full expression code and remove it from main code
    #this function is used only in condition statement because we need lists of expression quads
    def get_expression(self,start_address,end_address):
        Q = self.programs_list[-1][start_address:end_address]
        del self.programs_list[-1][start_address:end_address]
        return Q

    #This function add the expression we get from the above function (get_expression) to the code
    def add_expression(self,expression_list,starting_pos):
        if(starting_pos == len(self.programs_list[-1])):
            self.programs_list[-1] = self.programs_list[-1] + expression_list
        else:
            self.programs_list[-1][starting_pos:starting_pos] = expression_list

    #Find all relop quads that are in the form "relop,x,y,old_relop_address" and set
    #the old_jump_address to the new_relop_address.If the new_relop_address == 0
    #then the function set the relop to how positions far is from the end of the expression list.
    def backpatch_relop(self,expression,old_relop_address,new_relop_address):
        for i in range(0,len(expression)):
            quad = expression[i].split(",")
            if quad[-1] == old_relop_address and quad[-2] != "_":
                if isinstance(new_relop_address,int) and new_relop_address == 0:
                    quad[-1] = "+"+str(len(expression)-i) #this relop will jump +str(len(expression)-i) from its current position
                else:
                    quad[-1] = new_relop_address
            expression[i] = ",".join(quad)
                

    #Do the same as the backpatch_relop but for jumps
    def backpatch_jump(self,expression,old_jump_address,new_jump_address):
        for i in range(0,len(expression)):
            quad = expression[i].split(",")
            if quad[-1] == old_jump_address and quad[-2] == "_":
                if isinstance(new_jump_address,int) and new_jump_address == 0:
                    quad[-1] = "+"+str(len(expression)-i) #this relop will jump +str(len(expression)-i) from its current position
                else:
                    quad[-1] = new_jump_address
            expression[i] = ",".join(quad)

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