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
from File import File
from Helpers import ePrint
from Helpers import ReplaceChars
from Helpers import RenameDirQuery
import Chemical
import Beatport


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

        ##
        ## Handle Directories (Release Search)
        ##
        if self.Settings.HasDirs():

            # here we only link the files to specific dirs
            # the next loop then cares about and first makes
            # a search in a release cache

            for folder in self.Settings.DirList:

                #
                # figure out the directory entries
                #
                file_list = glob.glob(os.path.join(folder, "*"))

                if not file_list:
                    ePrint(1, self.__ClassName, "Skipping directory " + folder)
                    continue

                ePrint(2, folder, "<-- Linking files")
                ePrint(2, "Containing: ", str(file_list) + "\n")

                # append them to the FileList
                for file_path in file_list:
                    f = File(file_path)
                    f.RelDir = folder
                    #ePrint(2, "Fileending: ", str(file_list) + "\n")
                    if f.Type in ["mp3", "flac", "wav", "wave", "ogg"]:
                        self.Settings.FileList.append(f)


        ##
        ## Handle the FileList if existent
        ##
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
                # Look in the cache
                #
                rel_page = None

                for t in filled_tracks:
                    if new_track.FileInstance.RelDir != "" and \
                       new_track.FileInstance.RelDir == t.FileInstance.RelDir and \
                       t.Release:
                           ePrint(2, self.__ClassName, "Using cache")
                           rel_page = t.Release
                           break

                if not rel_page:
                    #
                    # look at chemical if nothing is found in tags or cache
                    #

                    # if we have artist and filename availible set this as searchterm
                    if new_track.Artist and new_track.Title:
                        search_term = new_track.Artist + " " + new_track.Title
                    else:
                        # otherwise create search_term from filename
                        search_term = new_track.FileInstance.NameBody
                        ePrint(2, self.__ClassName, "Setting searchterm: " + search_term)

                    # link it up on chemical
                    res_page = Beatport.ResultPage(search_term)

                    # if we found nothing, we cut the searchterm
                    if not res_page.GetReleaseList():
                        # at first remove signs symbols and retry
                        search_term = ReplaceChars("/_()-.:,&?", " ", search_term)
                        # strip "feat" terms
                        p = re.compile(" feat ", re.IGNORECASE)
                        search_term = p.sub("", search_term)

                        res_page = Beatport.ResultPage(search_term)

                        if not res_page.GetReleaseList():
                            # second remove numbers
                            search_term = ReplaceChars("0123456789", " ", search_term)
                            res_page = Beatport.ResultPage(search_term)

                            # now strip words from the term
                            if not res_page.GetReleaseList():
                                search_term_word_list = search_term.split()
                                while len(search_term_word_list) > 1:
                                    search_term_word_list.pop()
                                    search_term = " ".join(search_term_word_list)
                                    res_page = Beatport.ResultPage(search_term)
                                    if res_page.GetReleaseList():
                                        break
                                
                    
                    
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
                    rel_page = Beatport.ReleasePage(release_candidate)


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
                    # link to the found release
                    new_track.Release = rel_page
                    filled_tracks.append(new_track)
                else:
                    ePrint(1, self.__ClassName, "Could not determine all fields for: " + new_track.FileInstance.Basename)
                    unfilled_tracks.append(new_track)

                print()

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
        # handle dir renaming
        #
        handled_dirs = []
        for track in filled_tracks:
            if track.FileInstance.RelDir and track.FileInstance.RelDir not in handled_dirs:
                # build a artist string, maximum 2
                artists = ""
                c = 0
                for t in track.Release.TrackList:
                    artists += t.Artist + " "
                    if c >= 1:
                        break
                    c += 1
                
                # create destination string
                artists = artists.strip()
                artists = ReplaceChars(" ", ".", artists)
                artists = artists.lower()
                
                dest = track.Release.Catid.lower() + ".-." + artists
                ePrint(2, self.__ClassName, track.FileInstance.RelDir)
                ePrint(2, self.__ClassName, dest)

                RenameDirQuery(track.FileInstance.RelDir, dest)

                handled_dirs.append(track.FileInstance.RelDir)

                

                


                
                

        #
        # handle searchterms
        #
            

                    
