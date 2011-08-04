#!/usr/bin/python3

# Chemical.py -- class for managing a result page on chemical
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-17.
# @Revision:    0.1

from Release import Release, Track
from Helpers import ePrint
from html5lib import treebuilders, treewalkers, serializer
from copy import deepcopy


import urllib.request
import html5lib

## Class to manage a ResultPage on
#
class ResultPage:

    ##============================= LIFECYCLE ====================================##

    ## The constructor
    #
    # The ResultPage is nearly completely constructed here
    #
    def __init__(self, searchTerm):
        self.__ClassName = "ResultPage"
        self.__ReleaseList = []

        # set the base link for searching
        self.__BaseLink = r'http://www.chemical-records.co.uk/sc/search?SRI=true&inandout=true&ND=-1&Type=Music&must='

        # strip whitespaces on the edges
        searchTerm = searchTerm.strip()

        # replace white spaces
        searchTerm = searchTerm.replace(" ", "+")

        # remove ampersand from searchTerm
        searchTerm = searchTerm.replace("&", "")

        #
        # get the web page source
        #
        ePrint(2, self.__ClassName, "Searching for term: " + searchTerm)
        response = urllib.request.urlopen(self.__BaseLink + searchTerm)

        # get page-source to str
        page = response.read()
        
        # return None if we have no source
        if len(page) == 0:
            return None

        # convert the string to a raw-string
        page = page.decode('Latin1')


        #
        # build the parser stream, we use minidom, after that parse the source
        #
        ePrint(2, self.__ClassName, "Parsing web source")
        p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom_tree = p.parse(page)
        walker = treewalkers.getTreeWalker("dom")
        stream = walker(dom_tree)

        self.__CreateReleaseList__(stream)

        #c = 1
        #for r in self.__ReleaseList:
        #    print("{:4d} : {!s:.100}".format(c, r))
        #    c += 1


    ##============================= OPERATIONS ===================================##

    ## Main parser Function
    #
    # Here, the release list is created, this is done by iterating
    # over the minidom stream and doing some flag or state style fetching
    #
    def __CreateReleaseList__(self, stream):
        found_item = False
        found_artist = False
        found_title = False
        found_label = False
        found_catnum = False

        cur_artist = ""
        cur_title = ""
        cur_label = ""
        cur_catnum = ""

        for item in stream:
            # check for item found
            if ("name" in item) and (item["name"] == "div"):
                for attTupel in item["data"]:
                    if ("class" in attTupel) and ("item" in attTupel):
                        found_item = True

                        # create a new release object
                        cur_release = Release()
                        

            # check if artist field ends
            if found_artist == True:
                if ("name" in item) and (item["name"] == "h4") and (item["type"] == "EndTag"):
                    found_artist = False

            # check if artist field ends
            if found_label == True:
                if ("name" in item) and (item["name"] == "span") and (item["type"] == "EndTag"):
                    found_label = False
                    cur_release.LabelName = cur_label.strip()

            # check if title field ends
            if found_title == True:
                if ("name" in item) and (item["name"] == "p") and (item["type"] == "EndTag"):
                    found_title = False

                    # add name to Release instance
                    cur_release.Name = cur_artist.strip() + " " + cur_title.strip()

            # check if catnum field ends
            if found_catnum == True:
                if ("name" in item) and (item["name"] == "span") and (item["type"] == "EndTag"):
                    found_catnum = False
                    
                    # add catnum to release
                    cur_release.Catid = cur_catnum.strip()

                    # because here is the item end, reset all data, and
                    # append the current release to the __ReleaseList
                    self.__ReleaseList.append(cur_release)
                    cur_artist =  ""
                    cur_title =  ""
                    cur_label = ""
                    cur_catnum = ""
                    found_item = False

            # check if label found
            if found_item == True:
                if ("name" in item) and (item["name"] == "span"):
                    for attTupel in item["data"]:
                        if ("class" in attTupel) and ("label" in attTupel):
                            found_label = True

            # check if artist found
            if found_item == True:
                if ("name" in item) and (item["name"] == "h4"):
                    for attTupel in item["data"]:
                        if ("class" in attTupel) and ("artist" in attTupel):
                            found_artist = True

            # check if title found
            if found_item == True:
                if ("name" in item) and (item["name"] == "p"):
                    for attTupel in item["data"]:
                        if ("class" in attTupel) and ("title" in attTupel):
                            found_title = True

            # find the infoPageLink
            if found_item == True and found_title:
                if ("name" in item) and (item["name"] == "a"):
                    for attTupel in item["data"]:
                        if attTupel[0] == "href":
                            cur_release.InfoPageLink = attTupel[1]

            # check if catnum found
            if found_item == True:
                if ("name" in item) and (item["name"] == "span"):
                    for attTupel in item["data"]:
                        if ("class" in attTupel) and ("catnum" in attTupel):
                            found_catnum = True

            # fetch artists
            if found_artist == True:
                if item["type"] == "SpaceCharacters":
                    cur_artist += " "
                if item["type"] == "Characters":
                    cur_artist += item["data"]

            # fetch artists
            if found_label == True:
                if item["type"] == "SpaceCharacters":
                    cur_label += " "
                if item["type"] == "Characters":
                    cur_label += item["data"]

            # fetch title
            if found_title == True:
                if item["type"] == "SpaceCharacters":
                    cur_title += " "
                if item["type"] == "Characters":
                    cur_title += item["data"]

            # fetch catnum
            if found_catnum == True:
                if item["type"] == "SpaceCharacters":
                    cur_catnum += " "
                if item["type"] == "Characters":
                    cur_catnum += item["data"]

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
        # get the web page source
        #
        response = urllib.request.urlopen(self.InfoPageLink)

        # get page-source to str
        page = response.read()
        
        # return None if we have no source
        if len(page) == 0:
            return None

        # convert the string to a raw-string
        page = page.decode('Latin1')


        #
        # build the parser stream, we use minidom, after that parse the source
        #
        ePrint(2, self.__ClassName, "Parsing web source")
        p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom_tree = p.parse(page)
        walker = treewalkers.getTreeWalker("dom")
        stream = walker(dom_tree)

        self.Parse(stream)
     
    ##============================= OPERATIONS ===================================##

    ## fetches release information
    def Parse(self, stream):
        l_itemFound = False
        l_tdCount = 0
        l_tuneList = []
        l_linkList = []
        l_artistList = []
        l_titleList = []
        l_keyList = []
        l_curArtist = ""
        l_curTitle = ""
        l_curKey = ""
        l_artistFound = False
        l_titleFound = False
        l_linkFound = False
        l_keyFound = False

        for item in stream:
            # check for item end
            if l_itemFound == True and ("name" in item) and (item["name"] == "tr") and (item["type"] == "EndTag"):
                l_itemFound = False

            # check for item found
            if ("name" in item) and (item["name"] == "tr"):
                for attTupel in item["data"]:
                    if ("class" in attTupel) and (("odd" in attTupel) or ("even" in attTupel)):
                        l_itemFound = True
                        l_tdCount = 0

            # artist section end
            if (l_artistFound == True) and ("name" in item) and (item["name"] == "td") and (item["type"] == "EndTag"):
                l_artistFound = False
                l_artistList.append(l_curArtist.strip())
                l_curArtist = ""

            # title section end
            if (l_titleFound == True) and ("name" in item) and (item["name"] == "td") and (item["type"] == "EndTag"):
                l_titleFound = False
                l_titleList.append(l_curTitle.strip())
                l_curTitle = ""

            # key section end
            if (l_keyFound == True) and ("name" in item) and (item["name"] == "td") and (item["type"] == "EndTag"):
                l_keyFound = False
                l_keyList.append(l_curKey.strip())
                l_curKey = ""

            # Higher td count
            if (l_itemFound == True) and ("name" in item) and (item["name"] == "td") and (item["type"] == "StartTag"):
                l_tdCount += 1

            # artist section starts
            if (l_itemFound == True) and (l_tdCount == 2) and ("name" in item) and (item["name"] == "td") and (item["type"] == "StartTag"):
                l_artistFound = True

            # title section starts
            if (l_itemFound == True) and (l_tdCount == 3) and ("name" in item) and (item["name"] == "td") and (item["type"] == "StartTag"):
                l_titleFound = True

            # key section starts
            if (l_itemFound == True) and (l_tdCount == 4) and ("name" in item) and (item["name"] == "td") and (item["type"] == "StartTag"):
                l_keyFound = True

            # grab artist
            if (l_artistFound == True):
                if (item["type"] == "SpaceCharacters"):
                    l_curArtist += " "
                if (item["type"] == "Characters"):
                    l_curArtist += item["data"]

            # grab title
            if (l_titleFound == True):
                if (item["type"] == "SpaceCharacters"):
                    l_curTitle += " "
                if (item["type"] == "Characters"):
                    l_curTitle += item["data"]

            # grab key
            if (l_keyFound == True):
                if (item["type"] == "SpaceCharacters"):
                    l_curKey += " "
                if (item["type"] == "Characters"):
                    l_curKey += item["data"]

            # grab link
            if (l_itemFound == True) and ("name" in item) and (item["name"] == "a"):
                for attTupel in item["data"]:
                    if ("class" in attTupel) and ("pbutton playmp3button" in attTupel):
                        l_linkFound = True
                for attTupel in item["data"]:
                    if ("href" in attTupel) and (l_linkFound == True):
                        l_linkList.append(attTupel[1])
                        l_linkFound = False

        # create tunelist
        # for link, artist, title, key in zip(l_linkList, l_artistList,l_titleList, l_keyList):
        #    l_tuneList.append([link, artist, title, key]) 

        # create track list
        c = 1
        for link, artist, title, key in zip(l_linkList, l_artistList,l_titleList, l_keyList):
            key = self.ConvertKey(key)
            self.TrackList.append( Track(artist = artist,
                                         title = title,
                                         key = key,
                                         number = c,
                                         snippet_link = link))
            c += 1
            
        

    def ConvertKey(self, chemKey):
        quint_map = {
                     '1A' : 'gismoll',
                     '2A' : 'dismoll',
                     '3A' : 'bmoll',
                     '4A' : 'fmoll',
                     '5A' : 'cmoll',
                     '6A' : 'gmoll',
                     '7A' : 'dmoll',
                     '8A' : 'amoll',
                     '9A' : 'emoll',
                     '10A' : 'hmoll',
                     '11A' : 'fismoll',
                     '12A' : 'cismoll',
                     '1B' : 'hdur',
                     '2B' : 'fisdur',
                     '3B' : 'desdur',
                     '4B' : 'asdur',
                     '5B' : 'esdur',
                     '6B' : 'bdur',
                     '7B' : 'fdur',
                     '8B' : 'cdur',
                     '9B' : 'gdur',
                     '10B' : 'ddur',
                     '11B' : 'adur',
                     '12B' : 'edur',
                    }
        if chemKey in quint_map:
            return quint_map[chemKey]
        else:
            return chemKey


## Function to test the module
def ModuleTest():
    res_page = ResultPage("Geminidsadsfdf")

    


if __name__ == "__main__":
    ModuleTest()

