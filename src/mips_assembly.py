#!/usr/bin/python3

import os

class mips_assebly:

    def __init__(self,file_name):
        #Create assembly file
        self.file_mips = open(file_name[0:-4] + ".ascii","w")
        #Open for read idermediate file
        self.file_int = open(file_name[0:-4] + ".int","r")

        self.translate_int_to_ass()

        self.file_int.close()
        self.file_mips.close()


    #Translate idermediate language to mips assembly
    def translate_int_to_ass(self):
        pass




    
