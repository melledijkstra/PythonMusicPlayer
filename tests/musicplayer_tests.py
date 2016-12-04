import unittest
from mpserver.musicplayer import MusicPlayer
from configparser import ConfigParser


class MusicPlayerTests(unittest.TestCase):
    def setUp(self):
        config = ConfigParser()
        config.read_file(open('../config.ini'))
        self.musicplayer = MusicPlayer(config.items('musicplayer'))


if __name__ == '__main__':
    unittest.main()