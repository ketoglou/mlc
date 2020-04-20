#!/usr/bin/python3

import string

class CreateC:

    def __init__(self, file_name):
        name =  file_name[0:-4]
        self.file_int = open((name + ".int"), "r") #open .int file for read
        self.file_c = open((name + ".c"),"w+")
        self.createC()
        self.file_int.close()
        self.file_c.close()

    def createC(self):
        self.file_c.write("//This code is for testing the idermediate language of minimal++\n\n#include <stdio.h>\n\n")
        relop_list = ["=",">","<","<>",">=","<="]
        oper_list = ["+","-","*","/"]
        #Write integers to file
        if len(self.var_list) > 0:
            self.file_c.write("int ")
            c_str = ""
            for integer_ in self.var_list:
                c_str = c_str + integer_ + ","
            c_str = c_str[:-1:] #remove the last comma
            self.file_c.write(c_str + ";\n")

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
                quad[1] = self.check_reference(quad[1])
                quad[2] = self.check_reference(quad[2])
                c_str = "if (" + quad[1] + quad[0] + quad[2] + ") goto " + "L_" + quad[3]
            elif quad[0] in oper_list:
                quad[1] = self.check_reference(quad[1])
                quad[2] = self.check_reference(quad[2])
                quad[3] = self.check_reference(quad[3])
                c_str = quad[3] + " = " + quad[1] + " " + quad[0] + " " + quad[2]
            elif quad[0] == "jump":
                c_str = "goto " + "L_" + quad[3]
            elif  quad[0] == ":=":
                quad[1] = self.check_reference(quad[1])
                quad[3] = self.check_reference(quad[3])
                c_str = quad[3] + " = " + quad[1]
            elif quad[0] == "out":
                quad[1] = self.check_reference(quad[1])
                c_str = 'printf("%d\\n",' + quad[1] + ")"
            elif quad[0] == "inp":
                quad[1] = self.check_reference(quad[1])
                c_str = 'scanf("%d",&' + quad[1] + ")"
            elif quad[0] == "retv":
                quad[1] = self.check_reference(quad[1])
                c_str = "return " + quad[1]
            elif quad[0] == "call":
                c_str = quad[1] + "()"
            elif quad[0] == "halt":
                c_str = "return 0"
            elif quad[0] == "par":
                ret = ""
                call_label = ""
                original_quad = ",".join(quad)
                while(quad[0] == "par"):
                    quad[1] = self.check_reference(quad[1])
                    if quad[2] == "CV":
                        c_str = c_str + quad[1] + ","
                    elif quad[2] == "REF":
                        c_str = c_str + "&" + quad[1] + ","
                    elif quad[2] == "RET":
                        ret = quad[1] + " = "
                    quad = self.read_line().split(",") #remove label from quad
                    call_label = quad[0].split(":")[0] #create label(this will used only when we are outside while in call)
                    quad[0] = quad[0][quad[0].index(":")+1:] #remove label from quad
                    original_quad = original_quad + "/" + ",".join(quad) #used in comments
                #if we outside while the we have the call quad
                label = "L_" + call_label + ":" #update label for call
                if c_str != "": #remove the last comma
                    c_str = c_str[:-1]
                if ret != "":
                    c_str = ret + quad[1] + "(" + c_str + ")"  #function
                else:
                    c_str = quad[1] + "(" + c_str + ")" #procedure
            elif quad[0] == "begin_block":
                program_type = "int"
                arguments =""
                program_begin = True
                if label.split("_")[1] == main_program_label :
                    main_name = quad[1]

                #Set arguments for program
                if len(self.functions_list) > 0:
                    program_ = self.functions_list[0]
                    if program_[1] == quad[1]:
                        if program_[0] == "procedure":
                            program_type = "void"
                        if len(program_) > 2:
                            for argum in program_[2:]:
                                argum = argum.split(" ")
                                if argum[0] == "in":
                                    arguments = arguments + "int " + argum[1] + ","
                                elif argum[0] == "inout":
                                    arguments = arguments + "int *" + argum[1]  + ","
                            arguments = arguments[:-1]

                c_str = "\n" + program_type + " " + quad[1] + "(" + arguments + "){" 
                self.file_c.write(c_str + "\t//" + original_quad + "\n")
            elif quad[0] == "end_block":
                program_begin = True
                self.file_c.write("}" + "\t//" + original_quad + "\n")
                if len(self.functions_list) > 0:
                    del self.functions_list[0] #delete the program arguments(no needed anymore)
                
            if program_begin == False: 
                c_str = "\t" + label + " " + c_str + ";" + "\t//" + original_quad + "\n"
                self.file_c.write(c_str)
            program_begin = False
            original_quad = self.read_line()

        self.file_c.write("\n\n" + "int main(){\n\t return " + main_name + "();\n}")

    #Read quad and delete the \n from the end
    def read_line(self):
        line = self.file_int.readline()
        quad = line.split(",")
        quad[-1] = quad[-1].split("\n")[0]
        quad = ",".join(quad)
        return quad

    #Check if an arg is reference and set it inside the code with an * in front of it
    def check_reference(self,arg):
        if len(self.functions_list) > 0:
            for arg_ in self.functions_list[0][2:]:
                arg_ = arg_.split(" ")
                if arg_[0] == "inout" and arg == arg_[1]:
                    return  "*" + arg
                    break
        return arg
                