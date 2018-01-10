import unittest

from mutagen import mp3


class MutagenTests(unittest.TestCase):
    samplefile = '../music/krtheme-cut.mp3'

    def test_get_length(self):
        a = mp3.MP3(self.samplefile)
        print("info: " + str(a.mime))


if __name__ == '__main__':
    unittest.main()
