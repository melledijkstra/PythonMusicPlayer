import configparser
import time
import unittest

from tinytag import TinyTag

from mpserver.musicplayer import MusicPlayer
from mpserver.tools import Colors, colorstring


class TinyTagTests(unittest.TestCase):
    samplefiles = [
        '../music/krtheme.wav',
        '../music/Eric Clapton - Tears in Heaven live Crossroads 2013.mp3',
        '../music/Eddie Vedder - Into The Wild/Eddie Vedder - No Ceiling.mp3',
    ]

    def setUp(self):
        # Get configuration for the application
        self.config = configparser.RawConfigParser()
        self.config.read_file(open('../config.ini'))

    def test_get_length(self):
        taginfo = TinyTag.get(self.samplefiles[0], False, True)
        print("artist         " + str(taginfo.artist))  # artist name as string
        print("album          " + str(taginfo.album))  # album as string
        print("albumartist    " + str(taginfo.albumartist))  # album artist as string
        print("audio_offset   " + str(taginfo.audio_offset))  # number of bytes before audio data begins
        print("bitrate        " + str(taginfo.bitrate))  # bitrate in kBits/s
        print("disc           " + str(taginfo.disc))  # disc number
        print("disc_total     " + str(taginfo.disc_total))  # the total number of discs
        print("duration (sec) " + str(taginfo.duration))  # duration of the song in seconds
        print("filesize       " + str(taginfo.filesize))  # file size in bytes
        print("genre          " + str(taginfo.genre))  # genre as string
        print("samplerate     " + str(taginfo.samplerate))  # samples per second
        print("title          " + str(taginfo.title))  # title of the song
        print("track          " + str(taginfo.track))  # track number as string
        print("track_total    " + str(taginfo.track_total))  # total number of tracks as string
        print("year           " + str(taginfo.year))  # year or data as string

    def test_duration_with_vlc(self):
        import vlc
        v = vlc.Instance()
        mp = MusicPlayer(self.config)
        albums = mp.get_albums_and_songs()
        # VLC Start
        start_time = time.time()
        for album in albums:
            print(colorstring("Album: " + album.title, Colors.GREEN))
            for song in album.getsonglist():
                print(colorstring("\t" + str(song.title), Colors.BLUE))
                media = v.media_new(song.filepath)
                media.parse()
                print("\tsong duration: " + str(media.get_duration()))
        print(colorstring("--- VLC took %s seconds ---" % round((time.time() - start_time), 5), Colors.RED))
        # VLC End
        # TinyTag Start
        start_time = time.time()
        for album in albums:
            print(colorstring("Album: " + album.title, Colors.GREEN))
            for song in album.getsonglist():
                print(colorstring("\t" + str(song.title), Colors.BLUE))
                tinytag = TinyTag.get(song.filepath, False, True)
                print("\tsong duration: " + str(round(tinytag.duration * 1000)))
        print(colorstring("--- TinyTag took %s seconds ---" % round((time.time() - start_time), 5), Colors.RED))
        # TinyTag End


if __name__ == '__main__':
    unittest.main()
