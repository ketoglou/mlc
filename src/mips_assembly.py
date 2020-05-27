#!/usr/bin/python3

import os

class mips_assembly:

    def __init__(self,file_name,list_of_functions):
        #Create assembly file
        self.file_mips = open(file_name[0:-4] + ".asm","w")
        #Open for read idermediate file
        self.file_int = open(file_name[0:-4] + ".int","r")

        #list_of_functions contain at position 0 the main
        #followed by a child function of main with all its childs and their childs(if have any)
        #followed by a child function of main with all its childs and their childs(if have any)
        #etc
        self.list_of_functions = list_of_functions
        self.main_start_quad = self.list_of_functions[0].starting_quad

        self.translate_int_to_ass()

        self.file_int.close()
        self.file_mips.close()


    
    #Make assembly code and save at $t0 the address(in stack) of the variable that does not belong to the current function
    #return 0 if variable is in main(global), return 1 if is local variable of a parent function
    #return 2 if is "in" argument of a parent function, return 3 if is "inout" argument of a parent function
    def gnvlcode(self,variable,func_pos):
        current_function = self.list_of_functions[func_pos]

        counter = 0
        offset = -1
        in_or_inout = ""
        parent_function = None
        #Check all the parent functions to find the variable
        if current_function.nesting_level > 1:
            nl_parent = current_function.nesting_level #This variable is for check only parents and not their brothers
            for i in range(func_pos-1,0,-1):
                parent_function = self.list_of_functions[i]
                if nl_parent != parent_function.nesting_level:
                    if parent_function.nesting_level < current_function.nesting_level:
                        counter += 1
                        if variable in parent_function.variables:
                            offset = 12 + 4*len(parent_function.arguments) + parent_function.variables.index(variable)
                            break
                        for j in range(0,len(parent_function.arguments)):
                            arg = parent_function.arguments[j]
                            if variable == arg[1]:
                                offset = 12 + 4*j
                                in_or_inout = arg[0]
                                break
                    nl_parent = parent_function.nesting_level
                #Break if we check and the last parent
                if parent_function.nesting_level == 1:
                    break

        if offset != -1:
            counter -= 1
            self.add_command("lw $t0,-4($sp)")
            for i in range(0,counter):
                self.add_command("lw $t0,-4($t0)")
            
            self.add_command("addi $t0,$t0,-"+str(offset))
            if in_or_inout == "":
                return 1
            elif in_or_inout == "in":
                return 2
            elif in_or_inout == "inout":
                return 3
        else:
        #If we get here then the variable is global(in main)
            return 0


    #Move data from variable(in memory) to register
    def loadvr(self,var,reg,func_pos):
        function = self.list_of_functions[func_pos]

        temp_var = -1
        t = var.split("_")
        if len(t) > 1:
            temp_var = int(t[1])

        len_vars = len(function.variables)
        len_args = len(function.arguments)
        len_temp = function.temporary_variables
        is_local = False
        
        #Check local first
        #If constant
        if self.represents_int(var):
            self.add_command("li "+reg+","+var)
            is_local = True
        #elif local temporary variable
        elif temp_var != -1:
            offset = 12 + 4*len_args + 4*len_vars + 4*temp_var
            self.add_command("lw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif local variable
        elif var in function.variables:
            var_pos = function.variables.index(var)
            offset = 12 + 4*len_args + 4*var_pos
            self.add_command("lw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif argument cv or ref
        else:
            for i in range(0,len_args):
                arg = function.arguments[i]
                if var == arg[1]:
                    offset = 12 + 4*i #i = arguments position
                    if arg[0] == "in":
                        self.add_command("lw "+reg+",-"+str(offset)+"($sp)")
                    elif arg[0] == "inout":
                        self.add_command("lw $t0,-"+str(offset)+"($sp)")
                        self.add_command("lw "+reg+",($t0)")
                    is_local = True

        #if it is not local then if from a parent or from main(global)
        if is_local == False:
            where_belongs = self.gnvlcode(var,func_pos)

            #if where_belongs == 0 then it belongs to main(global)
            if where_belongs == 0:
                main = self.list_of_functions[0]
                offset = 12 + 4*main.variables.index(var)
                self.add_command("lw "+reg+",-"+str(offset)+"($s0)")
            #else if where_belongs == 1 then it is a local variable of a parent function
            #or if where_belongs == 2 then it is a "in" argument of a parent function
            elif where_belongs == 1 or where_belongs == 2:
                self.add_command("lw "+reg+",($t0)")
            #else(where_belongs == 3) then it is a "inout" argument of a parent function
            else:
                self.add_command("lw $t0,($t0)")
                self.add_command("lw "+reg+",($t0)")


    #Move data from register to memory
    def storerv(self,reg,var,func_pos):
        function = self.list_of_functions[func_pos]

        temp_var = -1
        t = var.split("_")
        if len(t) > 1:
            temp_var = int(t[1])

        len_vars = len(function.variables)
        len_args = len(function.arguments)
        len_temp = function.temporary_variables
        is_local = False

        #Check local first
        #if local temporary variable
        if temp_var != -1:
            offset = 12 + 4*len_args + 4*len_vars + 4*temp_var
            self.add_command("sw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif local variable
        elif var in function.variables:
            var_pos = function.variables.index(var)
            offset = 12 + 4*len_args + 4*var_pos
            self.add_command("sw "+reg+",-"+str(offset)+"($sp)")
            is_local = True
        #elif argument cv or ref
        else:
            for i in range(0,len_args):
                arg = function.arguments[i]
                if var == arg[1]:
                    offset = 12 + 4*i #i = arguments position
                    if arg[0] == "in":
                        self.add_command("sw "+reg+",-"+str(offset)+"($sp)")
                    elif arg[0] == "inout":
                        self.add_command("lw $t0,-"+str(offset)+"($sp)")
                        self.add_command("sw "+reg+",($t0)")
                    is_local = True

        #if it is not local then if from a parent or from main(global)
        if is_local == False:
            where_belongs = self.gnvlcode(var,func_pos)

            #if where_belongs == 0 then it belongs to main(global)
            if where_belongs == 0:
                main = self.list_of_functions[0]
                offset = 12 + 4*main.variables.index(var)
                self.add_command("sw "+reg+",-"+str(offset)+"($s0)")
            #else if where_belongs == 1 then it is a local variable of a parent function
            #or if where_belongs == 2 then it is a "in" argument of a parent function
            elif where_belongs == 1 or where_belongs == 2:
                self.add_command("sw "+reg+",($t0)")
            #else(where_belongs == 3) then it is a "inout" argument of a parent function
            else:
                self.add_command("lw $t0,($t0)")
                self.add_command("sw "+reg+",($t0)")


    #Translate idermediate language to mips assembly
    def translate_int_to_ass(self):
        #First line is the jump to main line
        line = self.file_int.readline() #Read first line from idermediate language file
        line = line[:-1] #Remove the last character(\n)
        quad = line.split(":",1) #split only in first : (in case of := symbol)
        main_label = quad[1].split(",")[3]
        self.file_mips.write("L0:\n")
        self.add_command("b L"+main_label)

        #current_function,current_function_pos used to have easy access to the inforamation of the current function
        #in the array of symbols
        current_function = None
        current_function_pos = 0

        #This is used to know when the current function is the main
        in_main = False

        #This function_call_offset,function_call_pos,function_call_framelength are used then a function is called
        #Function is called when we see a some "par" in immediate code followed by "call" or a "call" alone.
        #if we have "par" then we find the function that will be called with find_function_pos(function_call_pos) and we add the frame lenght of it
        #(function_call_framelength) the function_call_offset is used to save the arguments in orderdatetime A combination of a date and a time. Attributes: ()
        #if alone "call" is found then function_call_offset no need the function is "procedure" with no arguments
        function_call_offset = 12
        function_call_pos = 0
        function_call_framelength = 0

        line = self.file_int.readline() #Read first line from idermediate language file
        line = line[:-1] #Remove the last character(\n)
        while line:
            quad = line.split(":",1) #split only in first : (in case of := symbol)
            label = quad[0]
            quad = quad[1].split(",")

            self.file_mips.write("L"+label+":\n")

            if label == main_label:
                in_main = True

            #Produce the appropriate MIPS code by intermediate code
            if quad[0] == "begin_block":
                current_function_pos = self.find_function_pos_sq(int(label))
                current_function = self.list_of_functions[current_function_pos]
                if in_main:
                    self.add_command("addi $sp,$sp,"+str(current_function.frame_length+12))
                    self.add_command("move $s0,$sp")
                else:
                    self.add_command("sw $ra,0($sp)")
            elif quad[0] == "end_block":
                if not in_main:
                    self.add_command("lw $ra,0($sp)")
                    self.add_command("jr $ra")
            elif quad[0] == "halt":
                self.add_command("")
            elif quad[0] == "jump":
                self.add_command("b L"+quad[3])
            elif quad[0] == "=" or quad[0] == "<" or quad[0] == ">" or quad[0] == "<=" or quad[0] == ">=" or quad[0] == "<>":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.loadvr(quad[2],"$t2",current_function_pos)
                branch = ""
                if quad[0] == "=":
                    branch = "beq"
                if quad[0] == "<":
                    branch = "blt"
                elif quad[0] == ">":
                    branch = "bgt"
                elif quad[0] == "<=":
                    branch = "ble"
                elif quad[0] == ">=":
                    branch = "bge"
                else:
                    quad[0] == "bne"

                self.add_command(branch+",$t1,$t2,"+"L"+quad[3])
            elif quad[0] == "+" or quad[0] == "-" or quad[0] == "*" or quad[0] == "/":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.loadvr(quad[2],"$t2",current_function_pos)
                op = ""
                if quad[0] == "+":
                    op = "add"
                elif quad[0] == "-":
                    op = "sub"
                elif quad[0] == "*":
                    op = "mul"
                elif quad[0] == "/":
                    op = "div"

                self.add_command(op+" $t1,$t1,$t2")
                self.storerv("$t1",quad[3],current_function_pos)
            elif quad[0] == ":=":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.storerv("$t1",quad[3],current_function_pos)
            elif quad[0] == "out":
                self.add_command("li $v0,1")
                self.loadvr(quad[1],"$a0",current_function_pos)
                self.add_command("syscall")
            elif quad[0] == "inp":
                self.add_command("li $v0,5")
                self.add_command("syscall")
                self.storerv("$v0",quad[1],current_function_pos)
            elif quad[0] == "retv":
                self.loadvr(quad[1],"$t1",current_function_pos)
                self.add_command("lw $t0,-8($sp)")
                self.add_command("sw $t1,($t0)")   
            elif quad[0] == "par":  

                if function_call_offset == 12:
                    temp_pos = self.file_int.tell()
                    function_call_pos = self.find_function_pos(quad,current_function_pos)
                    function_call_framelength = self.list_of_functions[function_call_pos].frame_length
                    self.file_int.seek(temp_pos)
                    self.add_command("addi $fp,$sp,"+str(function_call_framelength + 12))

                if quad[2] == "CV":
                    self.loadvr(quad[1],"$t0",current_function_pos)
                    self.add_command("sw $t0,-"+str(function_call_offset)+"($fp)")
                    function_call_offset += 4
                elif quad[2] == "REF":
                    arg_type,offset = self.find_variable_in_parent(quad[1],current_function_pos)

                    #if var or cv in current function then load its address in $t0
                    if arg_type == 0:
                        self.add_command("addi $t0,$sp,-"+str(offset))
                    #elif ref in current function then load its parent address in $t0
                    elif arg_type == 1:
                        self.add_command("lw $t0,-"+str(offset)+"($sp)")
                    #elif var or cv or ref in parent function
                    elif arg_type == 3:
                        where_belongs = self.gnvlcode(quad[1],current_function_pos) 
                        if where_belongs == 3: #ref in another parent function
                            self.add_command("lw $t0,($t0)")
                        elif where_belongs == 0: #ref in variable in main(main does not have arguments)
                            offset = 12 + 4*self.list_of_functions[0].variables.index(quad[1])
                            self.add_command("addi $t0,$s0,-"+str(offset))
                            
                    self.add_command("sw $t0,-"+str(function_call_offset)+"($fp)")
                    function_call_offset += 4
                elif quad[2] == "RET":
                    arg_type,offset = self.find_variable_in_parent(quad[1],current_function_pos)
                    self.add_command("addi $t0,$sp,-"+str(offset))
                    self.add_command("sw $t0,-8($fp)")
                    function_call_offset += 4          

            elif quad[0] == "call":
                
                #procedure without arguments
                if function_call_offset == 12:
                    function_call_pos = self.find_function_pos(quad,current_function_pos)
                    function_call_framelength = self.list_of_functions[function_call_pos].frame_length
                    self.add_command("addi $fp,$sp,"+str(function_call_framelength + 12))

                #Save the access link
                #If called and calling function have the same nesting level then they have the same parent
                #else calling function is the parent of the called function
                if self.list_of_functions[function_call_pos].nesting_level == self.list_of_functions[current_function_pos]:
                    self.add_command("lw $t0,-4($sp)")
                    self.add_command("sw $t0,-4($fp)")
                else:
                    self.add_command("sw $sp,-4($fp)")
            
                self.add_command("addi $sp,$sp,"+str(function_call_framelength + 12))
                label_jal = "L" + str(self.list_of_functions[function_call_pos].starting_quad)
                self.add_command("jal "+label_jal)
                self.add_command("addi $sp,$sp,-"+str(function_call_framelength + 12))

                #Re-init
                function_call_offset = 12

            line = self.file_int.readline() #Read next line from idermediate language file
            line = line[:-1] #Remove the last character(\n)




#Helping functions

    #Add a command to mips file
    def add_command(self,command):
        self.file_mips.write("\t" + command + "\n")


    #Find the position of current function in array of symbols by starting quad
    def find_function_pos_sq(self,starting_quad):
        for i in range(0,len(self.list_of_functions)):
            function = self.list_of_functions[i]
            if function.starting_quad == starting_quad:
                return i

    #Helping function to see if a str is int
    def represents_int(self,str):
        try: 
            int(str)
            return True
        except ValueError:
            return False

    #Finds the position in list_of_functions of the called function
    #pos : current function position
    #quad : the current quad
    #return function (that called by current function) position in the list_of_functions
    def find_function_pos(self,quad,func_pos):

        name = ""
        type_called = "procedure"
        arguments = []
        quad_ = quad
        if quad_[0] == "call":
            name = quad_[1]
        elif quad_[2] == "RET":
            type_called = "function"
            line = self.file_int.readline() #Read next line from idermediate language file
            line = line[:-1] #Remove the last character(\n)
            quad_ = line.split(":",1) #split only in first : (in case of := symbol)
            quad_ = quad_[1].split(",")
        else:
            while quad_[0] != "call":
                if quad_[0] == "par" and quad_[2] != "RET":
                    arguments.append(quad_[2])
                if quad_[2] == "RET":
                    type_called = "function"
                line = self.file_int.readline() #Read next line from idermediate language file
                line = line[:-1] #Remove the last character(\n)
                quad_ = line.split(":",1) #split only in first : (in case of := symbol)
                quad_ = quad_[1].split(",")
            
        name = quad_[1]
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
        #3)Can can all parent and brother functions(all functions in front of it until nesting level == 1 and after that only the functions in front of it with nesting level == 1)
        else:

            current_function = self.list_of_functions[func_pos]
            #Check all the childrens of the current function(if have any)
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

        return function_pos


    
    #Private function to check if arguments are the same(used between comparison of two functions)(used only in undeclared_fun_or_proc)
    #eg args1=['in','inout'] and args2=[['CV',x],['REF',y]] is same
    def check_same_args(self,args1,args2):
        same_args = True
        for i in range(0,len(args1)):
            if (args1[i] == "in" and args2[i] != "CV") or (args1[i] == "inout" and args2[i] != "REF"):
                same_args = False
                break
        return same_args


    #Find variable in parent function(used for stack)
    #return 0,offset if var is local or CV
    #return 1,offset if var is REF
    #return 2,offset is temporary variable
    #if it belong to a parent of the parent then is return 3,0
    def find_variable_in_parent(self,var,parent_pos):
        current_function = self.list_of_functions[parent_pos]

        offset = 12
        len_args = len(current_function.arguments)
        for i in range(0,len_args):
            par_arg = current_function.arguments[i]
            if par_arg[1] == var:
                offset += 4*i
                if par_arg[0] == "in":
                    return 0,offset
                else: #REF
                    return 1,offset

        len_vars = len(current_function.variables)
        for i in range(0,len_vars):
            par_var = current_function.variables[i]
            if par_var == var:
                offset += 4*len_args + 4*i
                return 0,offset

        if var.split("_")[0] == "T":
            offset += 4*len_args + 4*len_vars + 4*int(var.split("_")[1])
            return 2,offset

        #If here then the variable is belong to a parent of this parent function
        return 3,0
