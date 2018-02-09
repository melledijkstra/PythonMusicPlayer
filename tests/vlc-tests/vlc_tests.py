import time
import unittest

import vlc

finish = 0


# TODO: this test case needs improvement

def SongFinished(event):
    global finish
    print("FINISHED EVENT")
    finish = 1


class VLCTests(unittest.TestCase):
    samplefile = '../testfiles/krtheme.wav'

    def setUp(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def test_can_play_sound(self):
        media = self.instance.media_new_path(self.samplefile)  # Your audio file here
        self.player.set_media(media)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)
        self.player.play()  # actually play the sound
        while finish == 0:
            sec = self.player.get_time() / 1000
            m, s = divmod(sec, 60)
            print("%02d:%02d" % (m, s))
            time.sleep(1)

    def test_setting_volume(self):
        volume = self.player.audio_get_volume()
        print("Volume is: " + str(volume))
        media = self.instance.media_new_path(self.samplefile)
        self.player.set_media(media)
        self.player.play()
        while self.player.get_state() != vlc.State.Playing:
            pass
        self.assertEqual(self.player.audio_set_volume(volume + 5), 0, "Could not set vlc audio!")
        while self.player.get_state() == vlc.State.Playing:
            if volume < 100:
                volume += 1
            else:
                volume = 10
            # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
            self.player.audio_set_volume(volume)
            print("Volume set to: " + str(volume))
            time.sleep(0.05)

    def test_play_file_when_already_playing(self):
        def play(iteration: int):
            if iteration >= 3: return
            self.player.set_media(self.instance.media_new_path(self.samplefile))
            self.player.play()
            sec = 0
            # wait for vlc to play media
            while self.player.get_state() != vlc.State.Playing:
                pass
            while True:
                m, s = divmod(self.player.get_time() / 1000, 60)
                print("%02d:%02d" % (m, s))
                time.sleep(1)
                sec += 1
                if sec > 3:
                    play(iteration + 1)
                    return
        print("Override already playing media with new media")
        play(0)  # recursive call


if __name__ == '__main__':
    unittest.main()
