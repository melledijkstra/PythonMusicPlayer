import os
from config import *
import pygame
import time

pygame.init()
pygame.mixer.init()


class MusicPlayer:
    """ This class can play music with the pygame library
        it keeps track of which file it is playing and has play, pause, etc. controls
        Also it has a list of files it can play
    """
    # format musiclist[0] = {"name": "Best Music by Someone", "file": "C:/path/to/file.mp3"}
    _musiclist = []
    # This variable keeps status if music is playing or not
    _isPlaying = False

    def __init__(self):
        pass

    def isPlaying(self):
        return self._isPlaying

    def getMusicList(self):
        return self._musiclist

    def process_command(self, cmdlist):
        """ This command processes commands for the music player
            Like:
                play<separator>3 // where 3 is song id
                pause
                stop
            :param: cmd The command for processing
            :type: str
        """
        # Response string
        response = commands.PLAYER + CMD_SEPERATOR
        if cmdlist[1] == "PLAY":
            try:
                songid = int(cmdlist[2])
                song = self._musiclist[songid]
                print("Trying to play '" + song['name'] + "' with id: " + str(songid))
                pygame.mixer.music.load(song['file'])
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    # keep playing music
                    print("PLAYING " + song['name'])
                    time.sleep(1)
                    pass
            except IndexError as e:
                response += str(e)
        elif cmdlist[1] == "PAUSE":
            if pygame.mixer.get_busy():
                pygame.mixer.pause()
                # TODO: Set a constant for "OK" command, so you only have to change it at 1 place if necessary
                response += "OK"
            else:
                pygame.mixer.unpause()
                response += "OK"
        elif cmdlist[1] == "STOP":
            pygame.mixer.stop()
            response += "OK"
        else:
            response += commands.INVALID
        # send the builded response back
        return response

    def musicListFromFolder(self, rootdir):
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


if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    print "settings: ", pygame.mixer.get_init()
    print "channels: ", pygame.mixer.get_num_channels()
    pygame.mixer.music.set_volume(1.0)
    song = pygame.mixer.music.load("music/krtheme.wav")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        print("PLAYING "+"music/krtheme.wav")
        time.sleep(1)
    #
    # try:
    #     musiclistfromfolder("music")
    # except IOError as e:
    #     print(e)
