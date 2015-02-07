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
        base = 'https://pro.beatport.com/search/releases?q={0}'
        base = base.format(searchTerm)

        r = requests.get(base)

        html = r.text

        self.__ReleaseList = self._get_releases(html, base)

    def _get_releases(self, html, query_link):
        # see if we hav multiple pages
        soup = BeautifulSoup(html, "lxml")

        page_numbers = soup.find_all(True, class_='pagination-number')

        if len(page_numbers) == 0:
            return self._get_releases_paginated(html)
        else:
            releases = []
            page_count = len(page_numbers)
            ePrint(1, self.__ClassName, "Found " + str(page_count) + " pages")

            for c in range(1, page_count + 1):
                r = requests.get(query_link + '&page=' + str(c))
                html = r.text

                releases = releases + self._get_releases_paginated(html)

            return releases


    def _get_releases_paginated(self, html):

        soup = BeautifulSoup(html, "lxml")
        items = soup.find_all('li', class_='release')
        rel_list = []

        for item in items:

            new_rel = Release()

            name = item.find('p', class_='release-title')

            link = name.find('a')
            link = link['href']

            name = name.text

            artists = item.find('p', class_='release-artists')
            artists = artists.text.strip()
            artists = re.sub(' +', ' ', artists)
            artists = " ".join(artists.split())

            label = item.find('p', class_="release-label")
            label = label.text.strip()
            label = re.sub(' +', ' ', label)


            new_rel.Name = name
            new_rel.LabelName = label
            new_rel.InfoPageLink = 'http://pro.beatport.com' + link

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

        #print(self.GetLongString())

    def _get_catalog_id(self, html):

        soup = BeautifulSoup(html, 'lxml')
        label_data = soup.find('span', class_='category', text='Catalog')

        cat_id = label_data.find_next_sibling('span')
        cat_id = cat_id.text

        return cat_id

    def _get_artwork_link(self, html):

        soup = BeautifulSoup(html, 'lxml')
        artwork = soup.find('img', class_='interior-release-chart-artwork')

        artwork = artwork['src']
        return artwork

    def _get_tracks(self, html):

        soup = BeautifulSoup(html, 'lxml')
        tcs = soup.find_all('li', class_='track')
        count = 1

        tracks = []

        for item in tcs:
            new_track = Track()

            title = item.find('span', class_='buk-track-primary-title')
            title = title.text

            title_remixed = item.find('span', class_='buk-track-remixed')
            title = title + ' (' + title_remixed.text + ')'
            title = " ".join(title.split())

            artist_list = item.find('p', class_='buk-track-artists')
            artist_list = artist_list.text
            artist_list = artist_list.strip()
            artist_list = " ".join(artist_list.split())

            key = item.find('p', class_='buk-track-key')
            key = key.text
            key = self.ConvertKey(key)


            track_number = count
            count += 1

            new_track.Artist = artist_list
            new_track.Title = title
            new_track.Number = track_number
            new_track.Key = key

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
                     'G♯ min' : 'gismoll',
                     'D♯ min' : 'dismoll',
                     'A♯ min' : 'bmoll',
                     'F min' : 'fmoll',
                     'C min' : 'cmoll',
                     'G min' : 'gmoll',
                     'D min' : 'dmoll',
                     'A min' : 'amoll',
                     'E min' : 'emoll',
                     'B min' : 'hmoll',
                     'F♯ min' : 'fismoll',
                     'C♯ min' : 'cismoll',
                     'B maj' : 'hdur',
                     'F♯ maj' : 'fisdur',
                     'C♯ maj' : 'desdur',
                     'G♯ maj' : 'asdur',
                     'D♯ maj' : 'esdur',
                     'A♯ maj' : 'bdur',
                     'F maj' : 'fdur',
                     'C maj' : 'cdur',
                     'G maj' : 'gdur',
                     'D maj' : 'ddur',
                     'A maj' : 'adur',
                     'E maj' : 'edur',
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

