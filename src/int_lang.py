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
        self.current_list = 0 #Holds the number of the current list
        self.quad_number = 1 #Counts the next quad number

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
        self.current_list += 1

    #If a program or function or procedure end then we write all of its quads
    def write_list(self):
        if self.current_list > 0:
            li = self.programs_list[self.current_list-1] #Get the current program or function or procedure list
            begin_block_num = str(self.nextquad()) #Get the quad number
            self.fd.write(begin_block_num+":"+li[0]+"\n") #Write begin_block
            #Write all the quads of this program or function or procedure
            for quad in range(2,len(li)):
                self.fd.write(str(self.nextquad())+":"+li[quad]+"\n")
            #if we are in the main program then write halt before end_block
            if self.current_list == 1:
                self.fd.write(str(self.nextquad())+":halt,_,_,_\n")  #write halt
                self.write_first_line("0:jump,_,_,"+begin_block_num+"\n")  #write jump to main
            self.fd.write(str(self.nextquad())+":"+li[1]+"\n")  #write end_block
            del self.programs_list[-1] #remove last list
            self.current_list -= 1

    #Creates next quad for the current program(or function or procedure)
    def genquad(self,op,x,y,z):
        quad = op+","+x+","+y+","+z
        self.programs_list[self.current_list-1].append(quad)

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