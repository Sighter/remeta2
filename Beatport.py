#!/usr/bin/python3

# Beatport.py -- Handle Beatport API
# @Author:      The Sighter (sighter@resource-dnb.de) & The Füttel (achterin@googlemail.com)
# @License:     GPL
# @Created:     2011-11-30.
# @Revision:    0.1

from Release import Release, Track
from Helpers import ePrint
from copy import deepcopy


import http.client
import json


## Class to manage a ResultPage on
#
class ResultPage:

    ##============================= LIFECYCLE ====================================##

    ## The constructor
    #
    # The ResultPage is nearly completely constructed here
    #
    def __init__(self, searchTerm):
        self.__ClassName = "Beatport.ResultPage"
        self.__ReleaseList = []


        # strip whitespaces on the edges
        searchTerm = searchTerm.strip()

        # replace white spaces
        searchTerm = searchTerm.replace(" ", "+")

        # remove ampersand from searchTerm
        searchTerm = searchTerm.replace("&", "")

        #
        # get the web data
        #
        ePrint(2, self.__ClassName, "Searching for term: " + searchTerm)

        # make a socket connection to the beatport api
        conn = http.client.HTTPConnection("api.beatport.com")
        conn.request("GET", "/catalog/3/search?query=" + searchTerm + "&facets[]=fieldType:release&perPage=500")
        r1 = conn.getresponse()
        #print(r1.status, r1.reason)
        
        mydict = json.loads(r1.read().decode())
        # print(json.dumps(mydict["results"], sort_keys=True, indent=4))

        #for entry in mydict["results"]:
        #    print(entry["name"])

        #print(len(mydict["results"]))
        
        # Check for nothing found
        if len(mydict["results"]) == 0:
            return None

        self.__CreateReleaseList__(mydict["results"])



    ##============================= OPERATIONS ===================================##

    ## Main parser Function
    #
    # Here, the release list is created
    #
    def __CreateReleaseList__(self, results):
        for rel in results:
            cur_release = Release()

            if rel["name"]:
                cur_release.Name = rel["name"]

            if rel["catalogNumber"]:
                cur_release.Catid = rel["catalogNumber"]

            if rel["label"]["name"]:
                cur_release.LabelName = rel["label"]["name"]

            if rel["id"]:
                cur_release.InfoPageLink = rel["id"]

            self.__ReleaseList.append(cur_release)



    ##============================= ACESS      ===================================##

    def GetReleaseList(self):
        if len(self.__ReleaseList) == 0:
            return None
        else:
            return self.__ReleaseList



## Class to manage a release page
#
class ReleasePage(Release):

    ##============================= LIFECYCLE ====================================##

    ## The constructor
    #
    # initialize the page and copy contnts of the given
    # release
    #
    def __init__(self, rel):
        
        # copy inherited object
        super().__init__()
        self.Name = rel.Name
        self.Catid = rel.Catid
        self.LabelName = rel.LabelName
        self.InfoPageLink = rel.InfoPageLink
        self.TrackList = deepcopy(rel.TrackList)

        # own members
        self.__ClassName = "ReleasePage"

        #
        # ask beatport api
        #
        conn = http.client.HTTPConnection("api.beatport.com")
        conn.request("GET", "/catalog/2/tracks?perPage=50&releaseId=" + str(self.InfoPageLink))
        r1 = conn.getresponse()
        
        mydict = json.loads(r1.read().decode())

        # No results 
        if len(mydict["results"]) == 0:
            return None
        #print(json.dumps(mydict["results"], sort_keys=True, indent=4))


        # get track info
        t_number = 1

        # we have to get the picture link from the first picture
        if mydict["results"][0]["images"]["large"]["url"]:
            self.PictureLink = mydict["results"][0]["images"]["large"]["url"]
            #print(self.PictureLink)

        for tr in mydict["results"]:
            cur_track = Track()

            #print(tr["artists"])

            if tr["artists"]:
                cur_track.Artist = ""
                for a in tr["artists"]:
                    if a["type"] == "artist":
                        cur_track.Artist += a["name"] + ", "

            cur_track.Artist = cur_track.Artist.rstrip(", ")
            
            if tr["title"]:
                cur_track.Title = tr["title"]

            cur_track.Number = t_number


            t_number += 1

            t_key = ""

            # get key 
            if tr["key"] and tr["key"]["standard"]:
                t_key += tr["key"]["standard"]["letter"]
                if tr["key"]["standard"]["sharp"] == True:
                    t_key += " Sharp"
                if tr["key"]["standard"]["flat"] == True:
                    t_key += " Flat"
                t_key += " " + tr["key"]["standard"]["chord"]

            cur_track.Key = self.ConvertKey(t_key)

            self.TrackList.append(cur_track)
        

        #print(self.GetLongString())
     
    ##============================= OPERATIONS ===================================##

    def ConvertKey(self, bpKey):
        quint_map = {
                     'G Sharp minor' : 'gismoll',
                     'D Sharp minor' : 'dismoll',
                     'A Sharp minor' : 'bmoll',
                     'F minor' : 'fmoll',
                     'C minor' : 'cmoll',
                     'G minor' : 'gmoll',
                     'D minor' : 'dmoll',
                     'A minor' : 'amoll',
                     'E minor' : 'emoll',
                     'B minor' : 'hmoll',
                     'F Sharp minor' : 'fismoll',
                     'C Sharp minor' : 'cismoll',
                     'B major' : 'hdur',
                     'F Sharp major' : 'fisdur',
                     'C Sharp major' : 'desdur',
                     'G Sharp major' : 'asdur',
                     'D Sharp major' : 'esdur',
                     'A Sharp major' : 'bdur',
                     'F major' : 'fdur',
                     'C major' : 'cdur',
                     'G major' : 'gdur',
                     'D major' : 'ddur',
                     'A major' : 'adur',
                     'E major' : 'edur',
                    }
        if bpKey in quint_map:
            return quint_map[bpKey]
        else:
            return bpKey


## Function to test the module
def ModuleTest():
    res_page = ResultPage("fourward blur")
    
    rel_page = ReleasePage(res_page.GetReleaseList()[0])

    res_page = ResultPage("hhhhhhhh")

    


if __name__ == "__main__":
    ModuleTest()

