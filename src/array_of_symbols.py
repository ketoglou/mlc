#!/usr/bin/python3

import os

class array_of_symbols:

    #Initialize a list which hold info about main and all functions,procedures and create a file to show array of symbols
    def __init__(self,file_name):
        self.fd_name = file_name[0:-4] + "_array_of_symbols.txt"
        self.fd = open(self.fd_name,"w")
        self.list_of_programs = []
        self.current_program_pos = -1
        self.current_nesting_level  = -1 #Used for array of symbols
        self.temporary_arguments = []

    #Add a main or a new procedure or function
    def add_program(self,program_name,program_type,arguments):
        #Check if another program(function or procedure) exist in the same nesting level whith the same name,type,arguments
        self.current_nesting_level += 1
        self.current_program_pos += 1
        #If nesting level == 1 
        if self.current_nesting_level == 1:
            #Check all programs with nesting level == 1 and see if we redeclared same program
            for i in range(1,len(self.list_of_programs)):
                program = self.list_of_programs[i]
                #If they have same nesting level
                if program.nesting_level == 1:
                    #If they have same name and type
                    if program_name == program.program_name and program_type == program.program_type and len(arguments) == len(program.arguments):
                        same_args = True
                        for j in range(0,len(arguments)):
                            if arguments[j] != program.arguments[j]:
                                same_args = False
                                break
                        if same_args == True:
                            return False
                        
        else:
            for i in range(len(self.list_of_programs)-1,0,-1):
                program = self.list_of_programs[i]
                #Check all programs with same nesting level,if not same nesting level then no program exist in this nesting level with same characteristics
                if  program.nesting_level == self.current_nesting_level :
                    if program.program_name == program_name and program.program_type == program_type and len(arguments) == len(program.arguments):
                        same_args = True
                        for j in range(0,len(arguments)):
                            if arguments[j] != program.arguments[j]:
                                same_args = False
                                break
                        if same_args == False:
                            return False
                elif program.nesting_level <  self.current_nesting_level:
                    break

        pa_record = program_activity_record(program_name,program_type)       #Create an object for this program
        self.list_of_programs.append(pa_record)                              #Add this program to the list of programs
        self.list_of_programs[-1].nesting_level = self.current_nesting_level #Set nesting level for current program
        #Set arguments for current program
        for i in range(0,len(arguments)):
            self.list_of_programs[-1].arguments.append(arguments[i][0])
            self.list_of_programs[-1].variables.append(arguments[i][1])
        return True

    #Add a declared argument or variable in the current program
    def add_variable(self,var):
        if var not in self.list_of_programs[-1].variables:
            self.list_of_programs[-1].variables.append(var)
            return True
        return False

    #Add type of argument(in or inout) of current program
    def add_temporary_argument(self,arg,var):
        self.temporary_arguments.append([arg,var])

    def get_temporary_arguments(self):
        t = self.temporary_arguments[:]
        self.temporary_arguments.clear()
        return t

    #Go back one nesting level 
    def undo_nesting_level(self):
        self.current_nesting_level -= 1

    #Set the number of temporary values eg if is 3 then we have T_0,...,T_2
    def set_temp_variables(self,t_vars,pos):
        self.list_of_programs[pos].temporary_variables = t_vars
    
    #Set the starting quad number of current program
    def set_starting_quad(self,s_quad,pos):
        self.list_of_programs[pos].starting_quad = s_quad
    

    #Helping function return current program name
    def current_program_name(self,pos):
        return self.list_of_programs[pos].program_name


    #Check if a variable is declared in the program
    def undeclared_variable(self,var,pos):
        current_program = self.list_of_programs[pos]
        #Check if it is declared on current program
        if var in self.list_of_programs[pos].variables:
            return True

        #Check all the parent programs to find the variable
        if current_program.nesting_level > 1:
            for i in range(pos-1,0,-1):
                program = self.list_of_programs[i]
                if program.nesting_level < current_program.nesting_level or program.nesting_level == 1:
                    if var in program.variables:
                        return True
                #Break if we check and the last parent
                if program.nesting_level == 1:
                    break
        
        #Check if it is declared as global variable
        if var in self.list_of_programs[0].variables:
            return True

        return False 


    #Check if a function or procedure is declared.
    #name: Used to see if the fun or proc is declared
    #type_: It is used to see if a proc called with call command and if a function called in expression
    #arguments: Used to see if the arguments are correct
    #pos: The program position in list_of_programs
    def undeclared_fun_or_proc(self,name,type_called,arguments,pos):
        
        function_pos = -1
        
        #If its main(pos == 0) then main can call all programs with nesting level == 1
        if pos == 0:
            for i in range(1,len(self.list_of_programs)):
                program = self.list_of_programs[i]
                if name == program.program_name and type_called == program.program_type and len(arguments) == len(program.arguments):
                        #If the arguments is the same then we find which program the main call
                        if self.check_same_args(arguments,program.arguments) == True:
                            function_pos = i
        #If its not main(pos > 0) then this program can call 
        #1)Its own childen programs(all programs following it with nesting level of program + 1 until nesting level < nesting level of program)
        #2)Can call it self(recursive)
        #3)Can can all parent programs(all programs in front of it until nesting level == 1 and after that only the program in front of it with nesting level == 1)
        else:

            current_program = self.list_of_programs[pos]
            #Check all the childerns of the current program(if have any)
            for i in range(pos+1,len(self.list_of_programs)):
                program = self.list_of_programs[i]
                if program.nesting_level > current_program.nesting_level:
                    #If they have same name and type
                    if name == program.program_name and type_called == program.program_type and len(arguments) == len(program.arguments):
                        #Check if the arguments are the same
                        if self.check_same_args(arguments,program.arguments) == True:
                            function_pos = i
                else:
                    #If we are here it means that no other children exist
                    break

            #Check calling itself
            if function_pos == -1:
                #If we are here it means that this program have no children or the children programs checked without find anything
                #Next thing is to check if the program call it self
                if name == current_program.program_name and type_called == current_program.program_type and len(arguments) == len(current_program.arguments):
                    if self.check_same_args(arguments,current_program.arguments) == True:
                        function_pos = pos

            #Check all the parents of the current program(if have any)
            if function_pos == -1:
                #If we are here it means that this program have no children or the children programs checked without find anything and did not call it self
                #Last thing is to check if the program call a parent function
                nl_1_found = False #This variable is used to check when a parent with nesting level(nl) 1 is found,so only parents with nl=1 can now be called
                for i in range(pos-1,0,-1):
                    program = self.list_of_programs[i]
                    if program.nesting_level == 1:
                        nl_1_found = True
                    if ((program.nesting_level <= current_program.nesting_level) and (nl_1_found == False)) or ((program.nesting_level == 1) and (nl_1_found == True)):
                        #If they have same name and type
                        if name == program.program_name and type_called == program.program_type and len(arguments) == len(program.arguments):
                            #Check if the arguments are the same
                            if self.check_same_args(arguments,program.arguments) == True:
                                function_pos = i
                    

        #If function_pos != -1 then we found it(declared),else is undeclared
        if function_pos != -1:
            return 0
        else:
            return 1


    #Private function to check if arguments are the same(used between comparison of two programs)(used only in undeclared_fun_or_proc)
    def check_same_args(self,args1,args2):
        same_args = True
        for i in range(0,len(args1)):
            if args1[i] != args2[i]:
                same_args = False
                break
        return same_args


    #Write to the array of symbols file the info about the current program
    def write_aos(self):
        for program in self.list_of_programs:
            self.fd.writelines("Name:"+program.program_name+"\n")
            self.fd.write("Type:"+program.program_type+"\n")
            self.fd.write("Starting Quad:"+str(program.starting_quad)+"\n")
            self.fd.write("Nesting Level:"+str(program.nesting_level)+"\n")
            self.fd.write("Arguments:"+str(program.arguments)+"\n")
            self.fd.write("Variables:"+str(program.variables)+"\n")
            self.fd.write("Temporary Variables:"+str(program.temporary_variables)+"\n")
            self.fd.write("___\n")

    
    #Deletes file array of symbol,used when error occur.
    def delete(self):
        os.remove(self.fd_name)

    #Close the file array of symbol(eg successfull compile)
    def close(self):
        self.fd.close()

#We create an object for every program(main,function,procedure) and hold information
class program_activity_record:

    #If the program have arguments then the arguments[0] is the variables[0]....and so on until
    #the arguments list end.After end of the arguments the variables are the declared ones.
    def __init__(self,program_name,program_type):
        self.program_name = program_name            #Program name
        self.program_type = program_type            #Type of program:"main","function","procedure"
        self.starting_quad = -1                     #Number of starting quad of this program

        self.arguments = []                         #Arguments of this program,leave empty for main.
        self.variables = []                         #Variables that have beed declared(including the arguments)
        self.temporary_variables = -1               #The number indicates the maximum temporary variable (eg if it is 10 then variables form T_0 to T_10 used,if it is -1 no temporary variables used)
        self.nesting_level = -1                     #Nesting level of this program
        self.offset = 0                             #Used for stack in assembly
        