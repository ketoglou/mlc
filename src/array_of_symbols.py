#!/usr/bin/python3

class array_of_symbols:
    def __init__(self,file_name):
        self.file_name = file_name[0:-4] + "_array_of_symbols.txt"
        self.list_of_programs = []
        self.current_nesting_level  = -1 #Used for array of symbols

    def add_program(self,program_name,program_type):
        pa_record = program_activity_record(program_name,program_type)
        self.list_of_programs.append(pa_record)
        self.current_nesting_level += 1
        self.list_of_programs[self.current_nesting_level].nesting_level = self.current_nesting_level
    
    def add_variable(self,var):
        if var not in self.list_of_programs[self.current_nesting_level].variables:
            self.list_of_programs[self.current_nesting_level].variables.append(var)
            return True
        return False

    def set_temp_variables(self,t_vars):
        self.list_of_programs[self.current_nesting_level].temporary_variables = t_vars
    
    def set_starting_quad(self,s_quad):
        self.list_of_programs[self.current_nesting_level].starting_quad = s_quad

    def add_argument(self,arg):
        self.list_of_programs[self.current_nesting_level].arguments.append(arg)
    
    def undo_nesting_level(self):
        self.current_nesting_level -= 1

    def current_program_name(self):
        return self.list_of_programs[self.current_nesting_level].program_name

    #Check if a variable is declared is the program
    def undeclared_variable(self,var):
        if var not in self.list_of_programs[self.current_nesting_level].variables:
            return False
        return True #error undeclared variable

    #Check if a function or procedure is declared.
    #name: Used to see if the fun or proc is declared
    #type_: It is used to see if a proc called with call command and if a function called in expression
    #arguments: Used to see if the arguments are correct
    def undeclared_fun_or_proc(self,name,type_called,arguments):
        #Find program
        program_id = -1
        for i in range(0,len(self.list_of_programs)):
            if self.list_of_programs[i].program_name == name and self.list_of_programs[i].nesting_level == (self.current_nesting_level+1):
                program_id = i
                break
        
        if program_id != -1:
            pr = self.list_of_programs[program_id]
            if pr.program_type == type_called:
                if len(arguments) != len(pr.arguments):
                    #error length of arguments not enough
                    return 3
                if len(arguments) == 0 and len(pr.arguments) == 0:
                    return 0 #no arguments
                for arg in range(0,len(arguments)):
                    if arguments[arg] != pr.arguments[arg]:
                        #error expected argument self.arguments[name][arg] but find arguments[arg]
                        return 4
            else:
                #error function called as proc or proc called as function
                return 2
        else:
            #error undeclared first use of proc or fun name
            return 1
        return 0

    #Dimiourgoume to activity record kai vazoume offset sta panta wste na kseroume poso apexoun
    def create_full_activity_record(self):
        fd = open(self.file_name,"w")
        for i in range((len(self.list_of_programs)-1),-1,-1):
            pr = self.list_of_programs[i]
            fd.writelines("Name:"+pr.program_name+"\n")
            fd.write("Type:"+pr.program_type+"\n")
            fd.write("Starting Quad:"+str(pr.starting_quad)+"\n")
            fd.write("Nesting Level:"+str(pr.nesting_level)+"\n")
            fd.write("Arguments:"+str(pr.arguments)+"\n")
            fd.write("Variables:"+str(pr.variables)+"\n")
            fd.write("Temporary Variables:"+str(pr.temporary_variables)+"\n")
            fd.write("___\n")
        fd.close()


class program_activity_record:

    #If the program have arguments then the arguments[0] is the variables[0]....and so on until
    #the arguments list end.After end of the arguments the variables are the declared ones.
    def __init__(self,program_name,program_type):
        self.program_name = program_name            #Program name
        self.program_type = program_type            #Type of program:"main","function","procedure"
        self.starting_quad = -1                     #Number of starting quad of this program
        self.arguments = []                         #Arguments of this program,leave empty for main.
        self.variables = []                         #Variables that have beed declared
        self.temporary_variables = -1               #The number indicates the maximum temporary variable (eg if it is 10 then variables form T_0 to T_10 used,if it is -1 no temporary variables used)
        self.nesting_level = -1                     #Nesting level of this program
        