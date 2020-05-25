#!/usr/bin/python3

import os

class array_of_symbols:

    #Initialize a list which hold info about main and all functions,procedures and create a file to show array of symbols
    def __init__(self,file_name):
        self.fd_name = file_name[0:-4] + "_array_of_symbols.txt"
        self.fd = open(self.fd_name,"w")
        self.list_of_functions = []
        self.current_function_pos = -1
        self.current_nesting_level  = -1 #Used for array of symbols
        self.temporary_arguments = []

    #Add a main or a new procedure or function
    def add_function(self,function_name,function_type,arguments):
        #Check if another function(function or procedure) exist in the same nesting level whith the same name,type,arguments
        self.current_nesting_level += 1
        self.current_function_pos += 1
        #If nesting level == 1 
        if self.current_nesting_level == 1:
            #Check all functions with nesting level == 1 and see if we redeclared same function
            for i in range(1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                #If they have same nesting level
                if function.nesting_level == 1:
                    #If they have same name and type
                    if function_name == function.name and function_type == function.type and len(arguments) == len(function.arguments):
                        same_args = True
                        for j in range(0,len(arguments)):
                            if arguments[j] != function.arguments[j]:
                                same_args = False
                                break
                        if same_args == True:
                            return False
                        
        else:
            for i in range(len(self.list_of_functions)-1,0,-1):
                function = self.list_of_functions[i]
                #Check all functions with same nesting level,if not same nesting level then no function exist in this nesting level with same characteristics
                if  function.nesting_level == self.current_nesting_level :
                    if function.name == function_name and function.type == function_type and len(arguments) == len(function.arguments):
                        same_args = True
                        for j in range(0,len(arguments)):
                            if arguments[j] != function.arguments[j]:
                                same_args = False
                                break
                        if same_args == False:
                            return False
                elif function.nesting_level <  self.current_nesting_level:
                    break

        pa_record = function_activity_record(function_name,function_type)       #Create an object for this function
        self.list_of_functions.append(pa_record)                              #Add this function to the list of functions
        self.list_of_functions[-1].nesting_level = self.current_nesting_level #Set nesting level for current function
        #Set arguments for current function
        for i in range(0,len(arguments)):
            self.list_of_functions[-1].arguments.append(arguments[i])
        return True

    #Add a declared argument or variable in the current function
    def add_variable(self,var):
        if var not in self.list_of_functions[-1].variables:
            self.list_of_functions[-1].variables.append(var)
            return True
        return False

    #Add type of argument(in or inout) of current function
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
        self.list_of_functions[pos].temporary_variables = t_vars
    
    #Set the starting quad number of current function
    def set_starting_quad(self,s_quad,pos):
        self.list_of_functions[pos].starting_quad = s_quad
    

    #Helping function return current function name
    def current_function_name(self,pos):
        return self.list_of_functions[pos].name


    #Check if a variable is declared in the function
    def undeclared_variable(self,var,pos):
        current_function = self.list_of_functions[pos]
        #Check if it is declared on current function
        if var in current_function.variables:
            return True
        for arg in current_function.arguments:
            if arg[1] == var:
                return True

        #Check all the parent functions to find the variable
        if current_function.nesting_level > 1:
            nl_parent = self.list_of_functions[pos].nesting_level #This variable is for check only parents and not their brothers
            for i in range(pos-1,0,-1):
                function = self.list_of_functions[i]
                if nl_parent != function.nesting_level:
                    if function.nesting_level < current_function.nesting_level:
                        #Check if variable belong to parent function as declared variable or as argument
                        if var in function.variables:
                            return True
                        for arg in function.arguments:
                            if arg[1] == var:
                                return True
                    nl_parent = function.nesting_level
                #Break if we check and the last parent
                if function.nesting_level == 1:
                    break
        
        #Check if it is declared as global variable(no arguments in main)
        if var in self.list_of_functions[0].variables:
            return True

        return False 


    #Check if a function or procedure is declared.
    #name: Used to see if the fun or proc is declared
    #type_called: It is used to see if a proc called with call command and if a function called in expression
    #arguments: Used to see if the arguments are correct
    #pos: The function position in list_of_functions
    def undeclared_fun_or_proc(self,name,type_called,arguments,func_pos):
        
        function_pos = -1
        
        #If its main(pos == 0) then main can call all functions with nesting level == 1
        if func_pos == 0:
            for i in range(1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                        #If the arguments is the same then we find which function the main call
                        if self.check_same_args(arguments,function.arguments) == True:
                            function_pos = i
        #If its not main(pos > 0) then this function can call 
        #1)Its own childen functions(all functions following it with nesting level of function + 1 until nesting level < nesting level of function)
        #2)Can call it self(recursive)
        #3)Can can all parent and brother functions(all functions in front of it until nesting level == 1 and after that only the function in front of it with nesting level == 1)
        else:

            current_function = self.list_of_functions[func_pos]
            #Check all the childerns of the current function(if have any)
            for i in range(func_pos+1,len(self.list_of_functions)):
                function = self.list_of_functions[i]
                if function.nesting_level == (current_function.nesting_level + 1):
                    #If they have same name and type
                    if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                        #Check if the arguments are the same
                        if self.check_same_args(arguments,function.arguments) == True:
                            function_pos = i
                else:
                    #If we are here it means that no other children exist
                    break

            #Check calling itself
            if function_pos == -1:
                #If we are here it means that this function have no children or the children functions checked without find anything
                #Next thing is to check if the function call it self
                if name == current_function.name and type_called == current_function.type and len(arguments) == len(current_function.arguments):
                    if self.check_same_args(arguments,current_function.arguments) == True:
                        function_pos = func_pos

            #Check all the parents of the current function(if have any)
            if function_pos == -1:
                #If we are here it means that this function have no children or the children functions checked without find anything and did not call it self
                #Last thing is to check if the function call a parent function
                nl_1_found = False #This variable is used to check when a parent with nesting level(nl) 1 is found,so only parents with nl=1 can now be called
                for i in range(func_pos-1,0,-1):
                    function = self.list_of_functions[i]
                    if function.nesting_level == 1:
                        nl_1_found = True
                    if ((function.nesting_level <= current_function.nesting_level) and (nl_1_found == False)) or ((function.nesting_level == 1) and (nl_1_found == True)):
                        #If they have same name and type
                        if name == function.name and type_called == function.type and len(arguments) == len(function.arguments):
                            #Check if the arguments are the same
                            if self.check_same_args(arguments,function.arguments) == True:
                                function_pos = i
                    

        #If function_pos != -1 then we found it(declared),else is undeclared
        if function_pos != -1:
            return 0
        else:
            return 1


    #Private function to check if arguments are the same(used between comparison of two functions)(used only in undeclared_fun_or_proc)
    #eg called_args=['in','inout'] and real_args=[['in','x'],['inout','y']] is same
    def check_same_args(self,called_args,real_args):
        same_args = True
        for i in range(0,len(called_args)):
            if called_args[i] != real_args[i][0]:
                same_args = False
                break
        return same_args

    #Calculates framelength of every function
    def calc_framelength(self):
        for function in self.list_of_functions:
            function.frame_length = 4*function.temporary_variables + 4*len(function.arguments) + 4*len(function.variables)

    #Write to the array of symbols file the info about the current function
    def write_aos(self):
        for function in self.list_of_functions:
            self.fd.writelines("Name:"+function.name+"\n")
            self.fd.write("Type:"+function.type+"\n")
            self.fd.write("Starting Quad:"+str(function.starting_quad)+"\n")
            self.fd.write("Nesting Level:"+str(function.nesting_level)+"\n")
            self.fd.write("Arguments:"+str(function.arguments)+"\n")
            self.fd.write("Variables:"+str(function.variables)+"\n")
            self.fd.write("Temporary Variables:"+str(function.temporary_variables)+"\n")
            self.fd.write("Frame Length:"+str(function.frame_length)+"\n")
            self.fd.write("___\n")

    
    #Deletes file array of symbol,used when error occur.
    def delete(self):
        os.remove(self.fd_name)

    #Close the file array of symbol(eg successfull compile)
    def close(self):
        self.fd.close()

#We create an object for every function(main,function,procedure) and hold information
class function_activity_record:

    #If the function have arguments then the arguments[0] is the variables[0]....and so on until
    #the arguments list end.After end of the arguments the variables are the declared ones.
    def __init__(self,func_name,func_type):
        self.name = func_name                       #Function name
        self.type = func_type                       #Type of function:"main","function","procedure"
        self.starting_quad = -1                     #Number of starting quad of this function

        self.arguments = []                         #Arguments of this function,leave empty for main(eg [['in','x'],['inout','y']])
        self.variables = []                         #Variables that have beed declared(eg ['x','y'])
        self.temporary_variables = -1               #The number indicates the maximum temporary variable (eg if it is 10 then variables form T_0 to T_10 used,if it is -1 no temporary variables used)
        self.nesting_level = -1                     #Nesting level of this function
        self.frame_length = 0                       #Used for stack in assembly(computed in mips)
        