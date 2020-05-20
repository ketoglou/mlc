#!/usr/bin/python3

import string
import ast

class create_c_code:

    def __init__(self, file_name):
        name =  file_name[0:-4]
        self.file_int = open((name + ".int"), "r") #open .int file for read
        self.file_aos = open((name+"_array_of_symbols.txt"),"r")
        self.file_c = open((name + ".c"),"w+")
        self.program_name = ""
        self.program_type = ""
        self.start_quad = -1
        self.nest_level = -1
        self.arguments = []
        self.variables = []
        self.temp_variables = []  
        self.createC()
        self.file_int.close()
        self.file_aos.close()
        self.file_c.close()

    def createC(self):
        self.file_c.write("//This code is for testing the idermediate language of minimal++\n\n#include <stdio.h>\n\n")
        relop_list = ["=",">","<","<>",">=","<="]
        oper_list = ["+","-","*","/"]
        
        #first quad of the idermediate language jumps to main,here we dont need it
        #we need only its label so we know what to call in main
        main_program_label = str(int(self.read_line().split(",")[-1]) - 1) + ":"

        #this will used to determine the name of main function in minimal++ and call it from main in C
        main_name = ""

        original_quad = self.read_line()

        #Write the code to file
        while original_quad:
            quad = original_quad.split(":")
            label = "L_" + quad[0] + ":" #create label for quad
            quad = original_quad.split(",") #remove label from quad
            quad[0] = quad[0][quad[0].index(":")+1:] #remove label from quad
            program_begin = False #used so we know where a program(function or procedure start)
            c_str = ""
            if quad[0] in relop_list:
                if quad[0] == "=" : quad[0] = "==" #change the boolean equality because C using other
                if quad[0] == "<>" : quad[0] = "!=" #change the boolean differrent because C using other
                quad[1] = self.check_inout(quad[1])
                quad[2] = self.check_inout(quad[2])
                c_str = "if (" + quad[1] + quad[0] + quad[2] + ") goto " + "L_" + quad[3]
            elif quad[0] in oper_list:
                quad[1] = self.check_inout(quad[1])
                quad[2] = self.check_inout(quad[2])
                quad[3] = self.check_inout(quad[3])
                c_str = quad[3] + " = " + quad[1] + " " + quad[0] + " " + quad[2]
            elif quad[0] == "jump":
                c_str = "goto " + "L_" + quad[3]
            elif  quad[0] == ":=":
                quad[1] = self.check_inout(quad[1])
                quad[3] = self.check_inout(quad[3])
                c_str = quad[3] + " = " + quad[1]
            elif quad[0] == "out":
                quad[1] = self.check_inout(quad[1])
                c_str = 'printf("%d\\n",' + quad[1] + ")"
            elif quad[0] == "inp":
                quad[1] = self.check_inout(quad[1])
                c_str = 'scanf("%d",&' + quad[1] + ")"
            elif quad[0] == "retv":
                quad[1] = self.check_inout(quad[1])
                c_str = "return " + quad[1]
            elif quad[0] == "call":
                c_str = quad[1] + "()"
            elif quad[0] == "halt":
                c_str = "return 0"
            elif quad[0] == "par":
                ret = ""
                call_label = label

                while(quad[0] == "par"):
                    quad[1] = self.check_inout(quad[1])
                    self.file_c.write("\t"+call_label+" asm(\"nop\");\t//"+",".join(quad)+"\n")
                    if quad[2] == "CV":
                        c_str = c_str + quad[1] + ","
                    elif quad[2] == "REF":
                        c_str = c_str + "&" + quad[1] + ","
                    elif quad[2] == "RET":
                        ret = quad[1] + " = "
                    quad = self.read_line().split(",") #remove label from quad
                    call_label = "L_"+quad[0].split(":")[0]+":" #create label(this will used only when we are outside while in call)
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
                program_begin = True
                self.get_array_of_symbols()
                program_type = "int"
                if self.program_type == "procedure":
                    program_type = "void"
                arguments_l =""

                #Set arguments for program and set void(if program is procedure) or int(if program is function)
                if len(self.arguments) > 0:
                    for i in range(0,len(self.arguments)):
                        arg0 = ""
                        if self.arguments[i] == "in":
                            arg0 = "int "
                        elif self.arguments[i] == "inout":
                            arg0 = "int *"
                        arg0 = arg0 + self.variables[i]
                        arguments_l = arguments_l + arg0 + ", "
                    arguments_l = arguments_l[:-2]
                    
                c_str = "\n" + program_type + " " + self.program_name + "(" + arguments_l + "){\n" 
                self.file_c.write(c_str + "\t"+label+"asm(\"nop\");"+"//" + original_quad + "\n\t")
                self.create_variables()
            elif quad[0] == "end_block":
                program_begin = True
                self.file_c.write("\t"+label+" asm(\"nop\");"+"\t//" + original_quad + "\n}\n")
                
            if program_begin == False: 
                c_str = "\t" + label + " " + c_str + ";" + "\t//" + original_quad + "\n"
                self.file_c.write(c_str)
            program_begin = False
            original_quad = self.read_line()

        self.file_c.write("\n\n" + "int main(){\n\t return " + self.program_name + "();\n}")

    #Read quad and delete the \n from the end
    def read_line(self):
        line = self.file_int.readline()
        quad = line.split(",")
        quad[-1] = quad[-1].split("\n")[0]
        quad = ",".join(quad)
        return quad
    
    def create_variables(self):
        l_args = len(self.arguments)
        if len(self.variables) > l_args or len(self.temp_variables) > 0:
            self.file_c.write("int ")
            c_str = ""
            if len(self.variables) > l_args:
                for integer_ in range(l_args,len(self.variables)):
                    c_str = c_str + self.variables[integer_] + ","
            if len(self.temp_variables) > 0:
                for integer_ in self.temp_variables:
                    c_str = c_str + integer_ + ","
            c_str = c_str[:-1:] #remove the last comma
            self.file_c.write(c_str + ";\n")


    def get_array_of_symbols(self):
        self.arguments.clear()
        self.variables.clear()
        self.temp_variables.clear()
        self.program_name = self.file_aos.readline().split(":")[1][:-1]                    #Name:
        self.program_type = self.file_aos.readline().split(":")[1][:-1]                    #Type:
        self.start_quad = int(self.file_aos.readline().split(":")[1][:-1]  )               #Starting Quad:
        self.nest_level = int(self.file_aos.readline().split(":")[1][:-1]  )               #Nesting Level:
        self.arguments = ast.literal_eval(self.file_aos.readline().split(":")[1][:-1])     #Arguments:
        self.variables = ast.literal_eval(self.file_aos.readline().split(":")[1][:-1])     #Variables:
        temp_v = int(self.file_aos.readline().split(":")[1][:-1])                          #Temporary Variables:
        if temp_v > 0:
            for i in range(0,temp_v):
                self.temp_variables.append("T_"+str(i))
        self.file_aos.readline() #read the ___

    #Check if a variable is inout and add the *
    def check_inout(self,var):
        #Convert inout argument
        for i in range(0,len(self.arguments)):
            if self.variables[i] == var and self.arguments[i] == "inout":
                return "*" + var
        return var