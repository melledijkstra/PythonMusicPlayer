from __future__ import unicode_literals
import youtube_dl
import unittest

class YTDLLogger(object):
    def debug(self, msg):
        # print(msg)
        pass

    def warning(self, msg):
        # print(msg)
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    print(d)
    if d['status'] == 'finished':
        print('Done downloading, now converting...')

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'logger': YTDLLogger(),
    'progress_hooks': [my_hook],
}

class YouttubeDLTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_download_mp3(self):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc', 'https://www.youtube.com/watch?v=bk6Xst6euQk'])

    def test_invalid_url(self):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(['http://invalidauDlnn.com/watch?v=d89a8D89'])
        except youtube_dl.DownloadError as e:
            print("Download Error (which is good :p)")

    def test_destination(self):
        # TODO: create this test
        pass

    def test_soundcloud_download(self):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(['https://soundcloud.com/mattkali/starboy-matt-kali-remix'])
        except youtube_dl.DownloadError as e:
            print(str(e))


if __name__ == '__main__':
    unittest.main()
