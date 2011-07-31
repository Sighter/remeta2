#!/usr/bin/python3

# TagHeader.py
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-21.
# @Revision:    0.1

import stagger
from stagger.id3 import *
from Helpers import ePrint

## class to describe a header of a file which contains tracks
#
class TagHeader:
    
    ## constructor
    #
    def __init__(self, filePath):
        self.__ClassName = "TagHeader"

        ePrint(2, self.__ClassName, "Try to create stagger tag for: " + filePath)

        self.Tag = stagger.read_tag(filePath)

    ## Getter Functions (interface driven)
    #
    def GetArtist(self):
        return self.Tag.artist
        
    def GetTitle(self):
        return self.Tag.title
        
    def GetNumber(self):
        return self.Tag.track
        
        
        
