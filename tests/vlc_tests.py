import unittest
import vlc
import time

global finish
finish = 0

# TODO: this test case needs improvement

def SongFinished(event):
    global finish
    print("Event reports - finished")
    finish = 1


class VlcTests(unittest.TestCase):
    def setUp(self):
        self.vlc = vlc.Instance()

    def test_can_play_sound(self):
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new_path('../music/krtheme.wav')  # Your audio file here
        player.set_media(media)
        player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)
        player.play() # actually play the sound
        while finish == 0:
            sec = player.get_time() / 1000
            m, s = divmod(sec, 60)
            print("%02d:%02d" % (m, s))
            time.sleep(1)

if __name__ == '__main__':
    unittest.main()
