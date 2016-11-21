import unittest
from musicplayer import *
from ConfigParser import SafeConfigParser


class MusicPlayerTests(unittest.TestCase):
    def setUp(self):
        config = SafeConfigParser()
        config.readfp(open('../config.ini'))
        self.musicplayer = MusicServer(config)

    def test_musicplayer(self):
        self.assertTrue(True, "mmm...?")

if __name__ == '__main__':
    unittest.main()