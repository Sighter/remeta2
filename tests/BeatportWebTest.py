
import BeatportWeb
from Release import Release


#from bs4 import BeautifulSoup
import unittest

class TestBeatportWeb(unittest.TestCase):

    def setUp(self):
        pass

    def test__get_releases(self):
        
        f = open('tests/files/results.html', 'r')
        html = f.read()
        f.close()

        res_page = BeatportWeb.ResultPage('term', True)
        res_list = res_page._get_releases(html)

        self.assertEqual(25, len(res_list))
        self.assertEqual('Cokehead', res_list[0].Name)

    @unittest.skip
    def test__init_and_get_releases(self):
        
        res_page = BeatportWeb.ResultPage('veak')
        
        rels = res_page.GetReleaseList()

    def test__relase_page(self):

        f = open('tests/files/releasePage.html', 'r')
        html = f.read()
        f.close()

        rel = Release()

        rel.Name = 'ON THE EDGE VOL 1'
        rel.InfoPageLink = 'http://www.beatport.com/release/on-the-edge-vol-1/1164510'


        rel_page = BeatportWeb.ReleasePage(rel, True)

        catid = rel_page._get_catalog_id(html)

        self.assertEqual('SYNDROME13015', catid)


        tracks = rel_page._get_tracks(html)

        self.assertEqual(4, len(tracks))

        artwork = rel_page._get_artwork_link(html)

        self.assertEqual('http://geo-media.beatport.com/image_size/500x500/8195874.jpg', artwork)

        for t in tracks:
            print(t)

    def test__get_key(self):
        f = open('tests/files/track.html', 'r')
        html = f.read()
        f.close()

        rel = Release()

        rel.Name = 'ON THE EDGE VOL 1'
        rel.InfoPageLink = 'http://www.beatport.com/release/on-the-edge-vol-1/1164510'


        rel_page = BeatportWeb.ReleasePage(rel, True)

        key = rel_page._get_key(html)

        self.assertEqual('hmoll', key)





