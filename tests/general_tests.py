import os
import unittest


class GeneralTests(unittest.TestCase):

    def test_renaming(self):
        file = 'testfiles'+os.sep+'subpath'+os.sep+'testfile.txt'
        newname = "Eddie Vedder - Long Nights"
        filename, ext = os.path.splitext(file)
        os.rename(file, os.path.dirname(file)+os.sep+newname+ext)
