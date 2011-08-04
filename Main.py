#!/usr/bin/python3

# Main.py
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-18.
# @Revision:    0.1

import glob
import os.path
import re

from Release import Release, Track
from Helpers import ePrint
from Helpers import ReplaceChars
import Chemical


# class to manage main functions of the script
#
class Main:

    ##============================= LIFECYCLE ====================================##

    ## constructor
    #
    # @param a settings object
    #
    def __init__(self, settings):
        self.__ClassName = "Main"
        ePrint(2, self.__ClassName, "Entering")
        self.Settings = settings

    ##============================= OPERATIONS ===================================##

    ## main control function of the program
    #
    def Run(self):

        print()

        filled_tracks = []
        unfilled_tracks = []

        #
        # Handle the FileList if existent
        #
        if self.Settings.HasFiles():
            track_list = []
            
            for f in self.Settings.FileList:
                
                #
                # at first try to gather some data from the tags, so
                # create a track object
                #

                new_track = Track()
                
                # associate the track with its file and try to read
                # some info from the tags
                new_track.FileInstance = f
                new_track.FillFromFile()

                ePrint(1, str(new_track.FileInstance.NameBody), "<-- Try to determine info")

                # if a track is fully filled continue with the next
                if (new_track.FilledEnough(self.Settings.Pattern)):
                    ePrint(1, self.__ClassName, "Track is filled enough: " + str(new_track) + "\n")
                    filled_tracks.append(new_track)
                    continue

                #
                # otherwise search Chemical
                #

                # if we have artist and filename availible set this as searchterm
                if new_track.Artist and new_track.Title:
                    search_term = new_track.Artist + " " + new_track.Title
                else:
                    # otherwise create search_term from filename
                    search_term = new_track.FileInstance.NameBody
                    ePrint(2, self.__ClassName, "Setting searchterm: " + search_term)

                # link it up on chemical
                res_page = Chemical.ResultPage(search_term)

                # if we found nothing, we cut the searchterm
                if not res_page.GetReleaseList():
                    # at first remove signs symbols and retry
                    search_term = ReplaceChars("/_()-.:,", " ", search_term)
                    # strip "feat" terms
                    p = re.compile(" feat ", re.IGNORECASE)
                    search_term = p.sub("", search_term)

                    res_page = Chemical.ResultPage(search_term)

                    if not res_page.GetReleaseList():
                        # second remove numbers
                        search_term = ReplaceChars("0123456789", " ", search_term)
                        res_page = Chemical.ResultPage(search_term)
                
                
                # if we finally found nothing, skip
                if not res_page.GetReleaseList():
                    ePrint(1, self.__ClassName, "Could not determine all fields for: " +
                           new_track.FileInstance.Basename + "\n")
                    unfilled_tracks.append(new_track)
                    continue
                
                #
                # now we process the result list
                #
                
                # invoke the user if we have found more than one results
                if len(res_page.GetReleaseList()) > 1:
                    ePrint(1, self.__ClassName,
                           "Multiple possilble releases found for: " + new_track.FileInstance.Basename +
                           "Please type number. 0 to skip.")
                    c = 1
                    for r in res_page.GetReleaseList():
                        print("{:4d} : {!s:.150}".format(c, r))
                        c += 1

                    choice = -1
                    while choice < 0 or choice > len(res_page.GetReleaseList()):
                        choice = int(input(" <-- "))

                    if choice == 0:
                        ePrint(1, self.__ClassName, "Skipping: " + new_track.FileInstance.Basename + "\n")
                        unfilled_tracks.append(new_track)
                        continue

                    # choose result, pay attention on index
                    release_candidate = res_page.GetReleaseList()[choice - 1]
                else:
                    release_candidate = res_page.GetReleaseList()[0]

                # create a ReleasePage, from the release candidate . This determines all relevant 
                # information for the release
                rel_page = Chemical.ReleasePage(release_candidate)

                #
                # identify the track in the release
                #

                # create a search term
                if new_track.Artist and new_track.Title:
                    search_term = new_track.Artist + " " + new_track.Title
                else:
                    search_term = new_track.FileInstance.NameBody
                
                search_term = ReplaceChars("/_()-.:,", " ", search_term)

                cor_track = rel_page.IdentifyTrack(search_term)
                ePrint(2, self.__ClassName, "corresponding track: " + str(cor_track))

                # since we only have a corresponding track copy on demand
                if not new_track.Artist:
                    new_track.Artist = cor_track.Artist
                if not new_track.Title:
                    new_track.Title = cor_track.Title
                if not new_track.Key:
                    new_track.Key = cor_track.Key
                if not new_track.Number:
                    new_track.Number = cor_track.Number

                if new_track.FilledEnough(self.Settings.Pattern):
                    ePrint(1, self.__ClassName, "Track is filled enough: " + str(new_track))
                    filled_tracks.append(new_track)
                else:
                    ePrint(1, self.__ClassName, "Could not determine all fields for: " + new_track.FileInstance.Basename)
                    unfilled_tracks.append(new_track)

                print()

        #
        # Handle Directories (Release Search)
        #
                    
        #
        # Rename files
        #
        for track in filled_tracks:
            dest_name = self.Settings.Pattern.GetResolvedString(artist=track.Artist, title=track.Title,
                                                                number=track.Number, key=track.Key)

            # function only needs the basename without extension
            if self.Settings.MakeCopy:
                #track.FileInstance.Copy(dest_name)
                pass
            else:
                track.FileInstance.RenameQuery(dest_name)

        #
        # handle searchterms
        #
            

                    
