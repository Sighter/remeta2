#!/usr/bin/python3

# Beatport.py -- Handle Beatport API
# @Author:      The Sighter (sighter@resource-dnb.de) & The Füttel (achterin@googlemail.com)
# @License:     GPL
# @Created:     2011-11-30.
# @Revision:    0.1

from Release import Release, Track
from Helpers import ePrint
from copy import deepcopy

from bs4 import BeautifulSoup
import xml.sax.saxutils

import re
import requests



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
    def __init__(self, searchTerm, naked=False):
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

        if naked:
            return

        # maka request
        base = 'http://www.beatport.com/search?facets%5B0%5D=fieldType%3Arelease&facets%5B1%5D=territoryISOName%3ADE&query={0}&perPage=150&sortBy=&returnFacets=fieldType%2CgenreName%2ClabelName%2CartistName%2CreleaseTypeName&countryCode=DE&realtimePrices=true&sourceType=sushi&format=json&appid=Sushi'
        base = base.format(searchTerm)

        r = requests.get(base)

        html = r.text

        # make a socket connection to the beatport api
        #conn = http.client.HTTPConnection("api.beatport.com")
        #conn.request("GET", "/catalog/3/search?query=" + searchTerm + "&facets[]=fieldType:release&perPage=500")
        #r1 = conn.getresponse()
        #print(r1.status, r1.reason)
        
        #mydict = json.loads(r1.read().decode())
        # print(json.dumps(mydict["results"], sort_keys=True, indent=4))

        #for entry in mydict["results"]:
        #    print(entry["name"])

        #print(len(mydict["results"]))
        
        # Check for nothing found
        #if len(mydict["results"]) == 0:
        #   return None



        self.__ReleaseList = self._get_releases(html)
    
    
    
    def _get_releases(self, html):

        soup = BeautifulSoup(html, "lxml")
        items = soup.find_all('div', class_='item-meta')
        rel_list = []
        
        for item in items:

            new_rel = Release()

            name = item.find('a', class_='item-title')
            link = name['href']
            name = name.text
                        
            artists = item.find('span', class_='item-list')
            artists = artists.text.strip()
            artists = re.sub(' +', ' ', artists)
            
            label = item.find('a', attrs={'data-type': 'label'})
            label = label.text.strip()
            label = re.sub(' +', ' ', label)
            

            new_rel.Name = name
            new_rel.LabelName = label
            new_rel.InfoPageLink = link

            rel_list.append(new_rel)

        return rel_list

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
    def __init__(self, rel, naked=False):
        
        # copy inherited object
        super().__init__()
        self.Name = rel.Name
        self.Catid = rel.Catid
        self.LabelName = rel.LabelName
        self.InfoPageLink = rel.InfoPageLink
        self.TrackList = deepcopy(rel.TrackList)

        # own members
        self.__ClassName = "ReleasePage"


        if naked:
            return
        #
        # ask beatport 
        #
        r = requests.get(self.InfoPageLink)
        html = r.text

        self.Catid = self._get_catalog_id(html)
        self.PictureLink = self._get_artwork_link(html)

        # get track info
        t_number = 1

        # we have to get the picture link from the first picture
        #if mydict["results"][0]["images"]["large"]["url"]:
        #    self.PictureLink = mydict["results"][0]["images"]["large"]["url"]
        
        self.TrackList = self._get_tracks(html)

        # get keys
        for t in self.TrackList:

            link = t.SnippetLink
            r = requests.get(link)
            html = r.text

            t.Key = self._get_key(html)

        #print(self.GetLongString())

    def _get_catalog_id(self, html):

        soup = BeautifulSoup(html, 'lxml')
        label_data = soup.find('td', class_='meta-data-label', text='Catalog #')

        cat_id = label_data.find_next_sibling('td')
        cat_id = cat_id.text

        return cat_id

    def _get_artwork_link(self, html):

        soup = BeautifulSoup(html, 'lxml')
        artwork = soup.find_all('span', class_='artwork')[0]

        artwork = artwork.find('img')

        artwork = artwork['src'].lstrip('/')

        link_list = artwork.split('/')
        link_list[2] = '500x500'

        link = ''.join([s + '/' for s in link_list])

        return 'http://' + link.rstrip('/')

        

    def _get_tracks(self, html):

        soup = BeautifulSoup(html, 'lxml')
        tcs = soup.find_all('td', class_='titleColumn')
        count = 1

        tracks = []

        for title_column in tcs:
            new_track = Track()

            title = title_column.find('a', class_='txt-larger')
            track_link = title['href']
            title = title.find_all('span')
            title = title[0].text + ' (' + title[1].text + ')'

            artist_list = title_column.find('span', class_='artistList')
            artist_list = artist_list.text

            track_number = count
            count += 1

            new_track.Artist = artist_list
            new_track.Title = title
            new_track.SnippetLink = track_link
            new_track.Number = track_number

            tracks.append(new_track)

        return tracks

    def _get_key(self, html):
        
        soup = BeautifulSoup(html, 'lxml')
        key = soup.find('span', class_='key')
        key = key.text
        key = key.replace('&#9839;', '#')

        return self.ConvertKey(key)

     
    ##============================= OPERATIONS ===================================##

    def ConvertKey(self, bpKey):
        quint_map = {
                     'G#min' : 'gismoll',
                     'D#min' : 'dismoll',
                     'A#min' : 'bmoll',
                     'Fmin' : 'fmoll',
                     'Cmin' : 'cmoll',
                     'Gmin' : 'gmoll',
                     'Dmin' : 'dmoll',
                     'Amin' : 'amoll',
                     'Emin' : 'emoll',
                     'Bmin' : 'hmoll',
                     'F#min' : 'fismoll',
                     'C#min' : 'cismoll',
                     'Bmaj' : 'hdur',
                     'F#maj' : 'fisdur',
                     'C#maj' : 'desdur',
                     'G#maj' : 'asdur',
                     'D#maj' : 'esdur',
                     'A#maj' : 'bdur',
                     'Fmaj' : 'fdur',
                     'Cmaj' : 'cdur',
                     'Gmaj' : 'gdur',
                     'Dmaj' : 'ddur',
                     'Amaj' : 'adur',
                     'Emaj' : 'edur',
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

