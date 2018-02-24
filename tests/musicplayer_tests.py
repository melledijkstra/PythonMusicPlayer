import unittest
from configparser import RawConfigParser

from mpserver.datastructures import MusicQueue
from mpserver.models import SongModel
from mpserver.musicplayer import MusicPlayer


class MusicPlayerTests(unittest.TestCase):
    def setUp(self):
        config = RawConfigParser()
        config.read_file(open('../config.ini'))
        self.musicplayer = MusicPlayer(config, False)

    def playlist_test(self):
        queue = MusicQueue()
        print("next song: " + str(queue.next()))
        print("current song: " + str(queue.current()))
        print("previous song: " + str(queue.previous()))
        song1 = SongModel('First Song', '../music/krtheme.wav')
        print("adding " + str(song1) + " to queue")
        queue.add(song1)
        print("queue size: " + str(queue.size()))
        print("current song: " + str(queue.current()))
        print("check if calling current again changed pointer: " + str(queue.current()))
        print("next song: " + str(queue.next()))
        print("check if pointer changed after next: " + str(queue.current()))
        print("previous song: " + str(queue.previous()))
        song2 = SongModel('Second Song', '../music/krtheme-cut.mp3')
        print("adding song2 " + str(song2))
        queue.add(song2)
        print("queue size: " + str(queue.size()))
        print("current song: " + str(queue.current()))
        print("next song: " + str(queue.next()))
        print("next song: " + str(queue.next()))
        print("previous song: " + str(queue.previous()))
        print("previous song: " + str(queue.previous()))
        print("current song" + str(queue.current()))
        song3 = SongModel('Third Song', '../music/Classic/dummy.wav')
        queue.add_next(song3)
        print(queue)
        print("play this song next: " + str(song3))
        print("next song: " + str(queue.next()))
        print("next song: " + str(queue.next()))
        print("test what happens when adding 100 songs")
        for i in range(100):
            queue.add(song3)
        print("size is: " + str(queue.size()))


if __name__ == '__main__':
    unittest.main()
