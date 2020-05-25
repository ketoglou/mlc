#!/usr/bin/python3

import string
import ast

class create_c_code:

    def __init__(self, file_name, list_of_function):
        name =  file_name[0:-4]
        self.file_int = open((name + ".int"), "r") #open .int file for read
        self.file_c = open((name + ".c"),"w+")
        self.list_of_functions = list_of_function  
        self.createC()
        self.file_int.close()
        self.file_c.close()

    def createC(self):
        self.file_c.write("//This code is for testing the idermediate language of minimal++\n\n#include <stdio.h>\n\n")
        relop_list = ["=",">","<","<>",">=","<="]
        oper_list = ["+","-","*","/"]
        
        #first quad of the idermediate language jumps to main,here we dont need it
        #we need only its label so we know what to call in main
        main_label = "L_"+ str(int(self.read_line().split(",")[3])) +":"

        current_function = None
        current_function_pos = 0

        original_quad = self.read_line()

        #Write the code to file
        while original_quad:
            quad = original_quad.split(":",1)
            label = int(quad[0]) 
            quad = original_quad.split(",") #remove label from quad
            quad[0] = quad[0][quad[0].index(":")+1:] #remove label from quad
            function_begin = False #used so we know where a function(function or procedure start)
            c_str = ""
            if quad[0] in relop_list:
                if quad[0] == "=" : quad[0] = "==" #change the boolean equality because C using other
                if quad[0] == "<>" : quad[0] = "!=" #change the boolean differrent because C using other
                quad[1] = self.check_inout(quad[1],current_function_pos)
                quad[2] = self.check_inout(quad[2],current_function_pos)
                c_str = "if (" + quad[1] + quad[0] + quad[2] + ") goto " + "L_" + quad[3]
            elif quad[0] in oper_list:
                quad[1] = self.check_inout(quad[1],current_function_pos)
                quad[2] = self.check_inout(quad[2],current_function_pos)
                quad[3] = self.check_inout(quad[3],current_function_pos)
                c_str = quad[3] + " = " + quad[1] + " " + quad[0] + " " + quad[2]
            elif quad[0] == "jump":
                c_str = "goto " + "L_" + quad[3]
            elif  quad[0] == ":=":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                quad[3] = self.check_inout(quad[3],current_function_pos)
                c_str = quad[3] + " = " + quad[1]
            elif quad[0] == "out":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                c_str = 'printf("%d\\n",' + quad[1] + ")"
            elif quad[0] == "inp":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                c_str = 'scanf("%d",&' + quad[1] + ")"
            elif quad[0] == "retv":
                quad[1] = self.check_inout(quad[1],current_function_pos)
                c_str = "return " + quad[1]
            elif quad[0] == "call":
                c_str = quad[1] + "()"
            elif quad[0] == "halt":
                c_str = "return 0"
            elif quad[0] == "par":
                ret = ""
                call_label = "L_"+ str(label) +":"

                while(quad[0] == "par"):
                    quad[1] = self.check_inout(quad[1],current_function_pos)
                    self.file_c.write("\t"+call_label+" asm(\"nop\");\t//"+",".join(quad)+"\n")
                    if quad[2] == "CV":
                        c_str = c_str + quad[1] + ","
                    elif quad[2] == "REF":
                        c_str = c_str + "&" + quad[1] + ","
                    elif quad[2] == "RET":
                        ret = quad[1] + " = "
                    quad = self.read_line().split(",") #remove label from quad
                    call_label = quad[0].split(":")[0] #create label(this will used only when we are outside while in call)
                    quad[0] = quad[0][quad[0].index(":")+1:] #remove label from quad
                #if we outside while the we have the call quad
                label = call_label #update label for call
                original_quad = ",".join(quad)
                if c_str != "": #remove the last comma
                    c_str = c_str[:-1]
                if ret != "":
                    c_str = ret + quad[1] + "(" + c_str + ")"  #function
                else:
                    c_str = quad[1] + "(" + c_str + ")" #procedure
            elif quad[0] == "begin_block":
                current_function_pos = self.find_function_pos_sq(label)
                current_function = self.list_of_functions[current_function_pos]
                function_begin = True

                function_type = "int"
                if current_function.type == "procedure":
                    function_type = "void"
                arguments_l =""

                #Set arguments for function and set void(if function is procedure) or int(if function is function)
                if len(current_function.arguments) > 0:
                    for i in range(0,len(current_function.arguments)):
                        arg0 = ""
                        if current_function.arguments[i][0] == "in":
                            arg0 = "int "
                        elif current_function.arguments[i][0] == "inout":
                            arg0 = "int *"
                        arg0 = arg0 + current_function.arguments[i][1]
                        arguments_l = arguments_l + arg0 + ", "
                    arguments_l = arguments_l[:-2]
                    
                c_str = "\n" + function_type + " " + current_function.name + "(" + arguments_l + "){\n" 
                self.file_c.write(c_str + "\tL_"+str(label)+": asm(\"nop\");"+"//" + original_quad + "\n")
                self.create_variables(current_function_pos)
            elif quad[0] == "end_block":
                function_begin = True
                self.file_c.write("\tL_"+str(label)+": asm(\"nop\");"+"\t//" + original_quad + "\n}\n")
                
            if function_begin == False: 
                c_str = "\tL_" + str(label) + ": " + c_str + ";" + "\t//" + original_quad + "\n"
                self.file_c.write(c_str)
            function_begin = False
            original_quad = self.read_line()
        
        self.file_c.write("\nint main(){\n\t return "+current_function.name+";\n}")


    #Read quad and delete the \n from the end
    def read_line(self):
        line = self.file_int.readline()
        quad = line.split(",")
        quad[-1] = quad[-1].split("\n")[0]
        quad = ",".join(quad)
        return quad
    
    def create_variables(self,func_pos):
        function = self.list_of_functions[func_pos]
        if len(function.variables) > 0 or function.temporary_variables > 0:
            self.file_c.write("\tint ")
            c_str = ""
            if len(function.variables) > 0:
                for integer_ in function.variables:
                    c_str = c_str + integer_ + ","
            if function.temporary_variables > 0:
                for i in range(0,function.temporary_variables):
                    c_str = c_str + "T_" + str(i) + ","
            c_str = c_str[:-1] #remove the last comma
            self.file_c.write(c_str + ";\n")

    #Find the position of current function in array of symbols by starting quad
    def find_function_pos_sq(self,starting_quad):
        for i in range(0,len(self.list_of_functions)):
            function = self.list_of_functions[i]
            if function.starting_quad == starting_quad:
                return i

    #Check if a variable is inout and add the *
    def check_inout(self,var,func_pos):
        function = self.list_of_functions[func_pos]
        #Convert inout argument
        for i in range(0,len(function.arguments)):
            if var == function.arguments[i][1] and "inout" == function.arguments[i][0]:
                return "*" + var
        return var