import unittest
import vlc
import time

finish = 0

# TODO: this test case needs improvement

def SongFinished(event):
    global finish
    print("FINISHED EVENT")
    finish = 1


class VlcTests(unittest.TestCase):

    samplefile = '../music/krtheme-cut.mp3'

    def setUp(self):
        self.instance = vlc.Instance()

    def test_can_play_sound(self):
        player = self.instance.media_player_new()
        media = self.instance.media_new_path(self.samplefile)  # Your audio file here
        player.set_media(media)
        player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)
        player.play() # actually play the sound
        while finish == 0:
            sec = player.get_time() / 1000
            m, s = divmod(sec, 60)
            print("%02d:%02d" % (m, s))
            time.sleep(1)

    def test_setting_volume(self):
        player = self.instance.media_player_new()
        volume = player.audio_get_volume()
        print("Volume is: "+str(volume))
        media = self.instance.media_new_path(self.samplefile)
        player.set_media(media)
        player.play()
        while player.get_state() != vlc.State.Playing:
            pass
        self.assertEqual(player.audio_set_volume(volume + 5), 0, "Could not set vlc audio!")
        while player.get_state() == vlc.State.Playing:
            if volume < 100:
                volume += 1
            else:
                volume = 10
            # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
            player.audio_set_volume(volume)
            print("Volume set to: "+str(volume))
            time.sleep(0.05)


if __name__ == '__main__':
    unittest.main()
