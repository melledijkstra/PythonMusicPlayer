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
        self.instance = vlc.Instance()  # type: vlc.Instance
        self.player = self.instance.media_player_new()  # type: vlc.MediaPlayer

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

    def test_stream_mixcloud(self):
        url = 'http://stream6.mixcloud.com/secure/c/m4a/64/4/e/3/5/b074-a7ef-4da5-a2cf-a390da945cbb.m4a?sig' \
              '=xlsqXNRipncHPvbxNMMnfQ'
        self.player.set_mrl(url)
        self.player.play()
        while self.player.get_state() != vlc.State.Playing:
            pass
        i = 0
        print('length: {}'.format(self.player.get_length()))
        while i < 30:
            print('time: {}'.format(self.player.get_time()))
            if i == 10:
                # test seeking in stream
                self.player.set_position(0.2)
            time.sleep(1)
            i += 1


if __name__ == '__main__':
    unittest.main()
