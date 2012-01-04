#!/usr/bin/python3

# File.py
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-20.
# @Revision:    0.1

from os import path
from shutil import copy
from os import rename

from TagHeader import TagHeader
from stagger.errors import *
from Helpers import ePrint


## class for Managin a file
#
class File:
    ## constructor 
    #
    # this determines the type and basename of the 
    # given path
    def __init__(self, filePath):
        self.__ClassName = "File"
        # set default Type
        self.Type = "mp3"
        self.Path = filePath
        self.Basename = path.basename(filePath)
        t, b = self.GetSuffix()

        self.RelDir = ""
        self.RelDirIdx = 0

        # set type
        if t:
            self.Type = t

        # set namebody, aka basename without extension
        self.NameBody = path.basename(b)

        # check if we find tag header and set the default if not
        self.TagHeader = None
        try:
            self.TagHeader = TagHeader(self.Path)
        except NoTagError:
            ePrint(1, self.__ClassName, "No Tag found in file: " + self.Basename)


    ## string method
    #
    def __str__(self):
        return self.Path

    ## method for debug output
    #
    def GetDict(self):
        return self.__dict__

    ## method to determine the ending of an filename
    #
    def GetSuffix(self):
        (pre, sep, suf) = self.Path.rpartition(".")
        if suf == self.Path:
            return ""
        else:
            return suf, pre

    ## method to rename an file
    #
    def RenameQuery(self, dest):
        dest = path.join(path.dirname(self.Path), dest + "." + self.Type)
        ePrint(1, ":", "Rename: " + self.Path + " --> " + dest, end=" ? ")
        choice = "k"
        while choice != "y" and choice != "n":
            choice = input("(y/n): ")

        if choice == "y":
            rename(self.Path, dest)

    ## method to rename an file without a user query
    #
    def Rename(self, dest):
        dest = path.join(path.dirname(self.Path), dest + "." + self.Type)
        ePrint(1, ":", "Renameing: " + self.Path + " --> " + dest)
        
        rename(self.Path, dest)


## Modul test
#
def ModTest():
    
    f = File("music/gemeni/blue.ogg")

    print(f)
    print(f.Basename)
    print(f.Type)


if __name__ == "__main__":
    ModTest()

        
