#!/usr/bin/python3

# release.py -- Class to manage a release
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-16.
# @Revision:    0.1

from File import File
from Helpers import ePrint

class Track():
    """This class manges a track"""

    ##============================= LIFECYCLE ====================================##

    ## The constructor
    #
    def __init__(self,
                 artist = None,
                 title = None,
                 number = None,
                 key = None,
                 snippet_link = None):

        self.Artist = artist
        self.Title = title
        self.Number = number
        self.Key = key
        self.SnippetLink = snippet_link
        self.FileInstance = None
    
    ##============================= OPERATIONS ===================================##

    ## method to fill a track with data from the tag of the corresponding
    #
    def FillFromFile(self):
        if self.FileInstance and self.FileInstance.TagHeader:
            self.Artist = self.FileInstance.TagHeader.GetArtist()
            self.Title = self.FileInstance.TagHeader.GetTitle()
            self.Number = self.FileInstance.TagHeader.GetNumber()
            
        
    ## str convert function
    #
    def __str__(self):
        artist = ""
        title = ""
        key = ""

        if self.Artist:
            artist = self.Artist
        else:
            artist = "Unknown"

        if self.Title:
            title = self.Title
        else:
            title = "Unknown"

        s = artist + " - " + title

        if self.Key:
            s += " - " + self.Key

        return s

    ##============================= ACESS      ===================================##

    ##============================= INQUIRY    ===================================##

    ## method to check if we have completely filled a track object
    #
    # @param the pattern to use
    #
    def FilledEnough(self, pattern):
        # go through all fields and return false if we dont find something wich is
        # needed
        if pattern.NeedArtist and not self.Artist:
            return False
        if pattern.NeedTitle and not self.Title:
            return False
        if pattern.NeedKey and not self.Key:
            return False
        if pattern.NeedNumber and not self.Number:
            return False

        return True




class Release:
    """This class manages a release."""
    
    ##============================= LIFECYCLE ====================================##

    ## The constructor
    #
    def __init__(self,
                 catid = None,
                 name = None,
                 labelName = None,
                 infoPageLink = None):

        self.Catid = catid
        self.Name  = name
        self.LabelName = labelName
        self.InfoPageLink = infoPageLink
        self.TrackList = []

    ##============================= OPERATIONS ===================================##

    ## str converter
    #
    def __str__(self):
        """String creator"""
        name = "Unknown"
        catid = "Unknown"
        label_name = "Unknown"
        info_page_link = ""
        
        if self.Name:
            name = self.Name

        if self.Catid:
            catid = self.Catid

        if self.LabelName:
            label_name = self.LabelName

        s = name + " : " + catid + " : " + label_name

        if self.InfoPageLink:
            s += " : " + self.InfoPageLink

        return s


    ## function to give an detailed string
    #
    def GetLongString(self):
        """Method gives a complete representation of the release"""
        s = self.__str__() + "\n"
        k = 1
        for tune in self.TrackList:
            if k == len(self.TrackList):
                s = s + "      " + str(tune)
            else:
                s = s + "      " + str(tune) + "\n"
            k = k + 1
        return s


    ## insert a track in the release
    #
    def AppendTrack(self, track):
        self.TrackList.append(track)
        

    ## this method trys to find a track in a release
    #
    # @return the found track or None
    #
    def IdentifyTrack(self, term):
        sFktname = "search_track"
        
        # build search term. so connect artist and
        # title, delete some characters and split on
        # white spaces
        search_term_list = term.strip()

        search_term_list = search_term_list.replace("(","").replace(")","")

        search_term_list = search_term_list.split()

        ePrint(2, sFktname, "looking for term: {}".format(search_term_list))

        # to find the track, we constuct a ranking, with the term on the highest rank, wich
        # made the most hits 
        max_hits = 0
    
        match_list = []

        for item in self.TrackList:

            item_hits = 0

            # create target term
            search_target_list = item.Artist.lower() + " " + item.Title.lower()
            search_target_list = search_target_list.split()

            # match
            for s in search_term_list:
                if s in search_target_list:
                    item_hits += 1
            
            # create a matchcount, item tupel
            match_list.append((item_hits, item))

        if len(match_list) == 0:
            return None


        # sort matchlist
        match_list = sorted(match_list, key = lambda tup: tup[0], reverse = True)
        
        
        return match_list[0][1]


    ##============================= ACESS      ===================================##


## Function to test the module
def ModuleTest():
    rel = Release("LOKA001", labelName = "Loca rec ", name = "Blue EP")
    
    t1 = Track("Gemini, Noisia", "Destiny", "4A")

    t2 = Track("Gemini", "Blue")

    rel.AppendTrack(t1)
    rel.AppendTrack(t2)

    print(rel)
    print(rel.GetLongString())

    if not rel.LabelName:
        print("Labelname not defined")
        

    
    


if __name__ == "__main__":
    ModuleTest()

