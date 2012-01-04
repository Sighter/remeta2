#!/usr/bin/python3

# Settings.py
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-18.
# @Revision:    0.1

from optparse import OptionParser
from os import path

from Pattern import Pattern
from Helpers import ePrint
from Release import File
import Helpers


## class for managing all settings
#
# In addition all arguments are parsed
#
class Settings:

    ##============================= LIFECYCLE ====================================##

    ## constructor
    #
    # @param the argument list
    #
    def __init__(self, arguments):
        self.__ClassName = "Settings"

        # 
        # at first parse options
        #
        usage = "usage: %prog [options] filnames or searchpatterns"
        parser = OptionParser(usage = usage)

        parser.add_option("-c", "--copy", action = "store_true",
                          help = "make a copy of original files before copying")
        parser.set_defaults(copy = False)

        parser.add_option("-w", "--cemelot", action = "store_true",
                          help = "use Cemelot format for keys")

        parser.add_option("-a", "--ask", action = "store_true",
                          help = "ask user if files are renamed")

        parser.add_option("-v", "--verb-level", action = "store", type= "int",
                          dest = "verblevel", help = "specify a verbosity level")

        parser.add_option("-p", "--pattern", action = "store", type= "string",
                          help = "specify a verbosity level")

        parser.set_defaults(copy = False)
        parser.set_defaults(cemelot = False)
        parser.set_defaults(verblevel = 1)
        parser.set_defaults(pattern = "")
        parser.set_defaults(ask = False)

        (options, args) = parser.parse_args(arguments)

        #
        # set options 
        #

        # if a pattern was given initialize a Pattern object with
        # given string
        if options.pattern:
            self.Pattern = Pattern(options.pattern)
        else:
            self.Pattern = Pattern()

        # toggle copy mode on or of
        self.MakeCopy = options.copy

        # toggle use of crappy chemelot notation
        self.UseChemelot = options.cemelot

        # ask or not ask user
        self.Ask = options.ask

        # set verbosity level
        # TODO: remove messi global variable
        self.VerbLevel = options.verblevel
        Helpers.G_VerbLevel = self.VerbLevel

        ePrint(2, self.__ClassName, "Pattern used: " + self.Pattern.Entry)
        ePrint(2, self.__ClassName, "Use copy mode: " + str(self.MakeCopy))
        ePrint(2, self.__ClassName, "Use chemelot notation: " + str(self.UseChemelot))


        #
        # create filelist and searchterm list
        #
        self.FileList = []
        self.DirList = []
        self.SearchTermList = []

        for entry in args:
            if path.isdir(entry):
                self.DirList.append(entry)
            elif path.isfile(entry):
                # create a file object
                self.FileList.append(File(entry))
            else:
                self.SearchTermList.append(entry)

        ePrint(3, self.__ClassName, "Search terms given:" + str(self.SearchTermList))
        ePrint(3, self.__ClassName, "Files given:")
        
        for f in self.FileList:
            ePrint(3, self.__ClassName, str(f.GetDict()))

    ##============================= ACESS      ===================================##

    def GetFileList(self):
        return self.FileList

    def GetSearchTermList(self):
        return self.SearchTermList

    ##============================= INQUIRY    ===================================##

    def HasFiles(self):
        if len(self.FileList):
            return True
        else:
            return False

    def HasSearchTerms(self):
        if len(self.SearchTermList):
            return True
        else:
            return False

    def HasDirs(self):
        if len(self.DirList):
            return True
        else:
            return False

        
