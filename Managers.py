import os
from config import allowed_extensions
import pygame
import time


class MusicManager:
    """ This class can play music with the pygame library
        it keeps track of which file it is playing and has play, pause, etc. controls
    """
    _isPlaying = False

    def __init__(self):
        pass

    def isPlaying(self):
        return self._isPlaying


class FileManager:
    """ This class keeps track of music stored in folders and files
    """
    # format musiclist[0] = {"name": "Best Music by Someone", "file": "C:/path/to/file.mp3"}
    _musiclist = []

    def __init__(self):
        pass

    def musiclistfromfolder(self, rootdir):
        """ Sets internal musiclist of FileManager instance, and returns that list with music names in the directory specified.
            currently searches for ".mp3", ".wav"

            Returns a list with dictionaries
            like so: musiclist[{"name":"Best Music by someone","file":"path/to/file.mp3"}]

            :param rootdir: Folder to search for music files
            :type rootdir: str
            :return: The list with all music names in the specified folder
            :rtype: list
        """
        musiclist = []
        if os.path.isdir(rootdir):
            for subdir, dirs, files in os.walk(rootdir):
                for musicfile in files:
                    if musicfile.endswith(allowed_extensions):
                        musiclist.append({"name": os.path.splitext(musicfile)[0], "file": subdir + "\\" + musicfile})
            # update instance musiclist and also return it
            self._musiclist = musiclist
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")

    def getMusicList(self):
        return self._musiclist


if __name__ == '__main__':
    filemanager = FileManager()
    somelist = filemanager.musiclistfromfolder("music")
    for music in somelist:
        print(music["file"])
    pass
    # pygame.mixer.init()
    # mplayer = pygame.mixer.music
    # mplayer.load("music/krtheme.wav")
    # mplayer.play()
    # p = True
    # while mplayer.get_busy():
    #     print(time.ctime())
    #     time.sleep(1)
    #     if p:
    #         mplayer.pause()
    #         p = False
    #     else:
    #         mplayer.unpause()
    #         p = True
    #
    # try:
    #     musiclistfromfolder("music")
    # except IOError as e:
    #     print(e)
