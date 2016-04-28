import os
from config import *
import pygame.mixer as mixer
import time
import json

# for some reason if you initialize pygame and then the mixer, there is no sound on windows (weird?)
# pygame.init()
mixer.init()


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
        self.musicListFromFolder('music')

    def isplaying(self):
        return self._isPlaying

    def getmusiclist(self):
        return self._musiclist

    def process_command(self, data, conn):
        """ This command processes commands for the music player
            Like:
                play<separator>3 // where 3 is song id
                pause
                stop
            :param: cmd The command for processing
            :type: str
        """
        # Response string
        # TODO: Clean up this function
        return_dict = {}
        if data["MPLAYER"]["cmd"] == "play":
            try:
                songid = int(data["MPLAYER"]["song_id"])
                song = self._musiclist[songid]
                print("Trying to play '" + song['name'] + "' with id: " + str(songid))
                mixer.music.load(song["file"].replace("\\", "/"))
                mixer.music.play()
                self._isPlaying = True
                while mixer.music.get_busy():
                    print("playing: "+song["name"]+" pos: "+mixer.music.get_pos())
                    return_dict["pos"] = mixer.music.get_pos()
                    return_dict["vol"] = mixer.music.get_volume()
                    conn.sendall(json.dumps(return_dict))
                self._isPlaying = False
                print("playing song: " + song["name"])
            except IndexError as e:
                response = str(e)
            except Exception as e:
                print(str(e))
                response = str(e)
        # elif cmdlist[1] == "PAUSE":
        #     if self._isPlaying:
        #         print("pausing song")
        #         mixer.music.pause()
        #         self._isPlaying = False
        #         response += "OK"
        #     else:
        #         print("unpausing song")
        #         mixer.music.unpause()
        #         self._isPlaying = True
        #         response += "OK"
        # elif cmdlist[1] == "STOP":
        #     print("stopping song")
        #     mixer.music.stop()
        #     self._isPlaying = False
        #     response += "OK"
        # else:
        #     response += commands.INVALID
        # send the builded response back
        # return response

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
    # if this file is run instead of imported this will run
    # a test to check if sound is playing (the music/krtheme.wav has to be present, duh!)
    print "settings: ", mixer.get_init()
    print "channels: ", mixer.get_num_channels()
    mixer.music.set_volume(1.0)
    mixer.music.load("music/krtheme.wav")
    mixer.music.play()
    while mixer.music.get_busy():
        print("PLAYING " + "music/krtheme.wav - " + str(mixer.music.get_pos()))
        time.sleep(0.5)
