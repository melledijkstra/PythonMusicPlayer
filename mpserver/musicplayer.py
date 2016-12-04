import os
from configparser import ConfigParser
import glob
import json
from typing import List

import vlc

from .interfaces import Logger
from .tools import *
from .tools import printcolor as c
from .musicmodels import Album, Song


class MusicPlayer(Logger):
    """ This class can play music with the vlc library
        it keeps track of which file it is playing. This class has play, pause, etc. controls
        It also manages which albums/songs there are
    """
    _section = 'musicplayer'

    def __init__(self, config: ConfigParser):
        super().__init__()
        self.v = vlc.Instance('--novideo')
        self._player = self.v.media_player_new()
        self._config = config
        self.__process_conf__()
        self.log("allowed extensions: "+str(self._allowed_extensions))
        self.log("music directory: "+str(self._musicdir))
        self._albums = self.get_albums_and_songs()
        self.log("Albums found ("+str(len(self._albums))+"): ")
        for album in self._albums:
            self.log(album)
        if os.path.isfile(config.get(self._section+'/events', 'onready', fallback='resources/ready.mp3')):
            self.media = self.v.media_new(config.get(self._section + '/events', 'onready', fallback='resources/ready.mp3'))
            self._player.set_media(self.media)
            self._player.play()

    def get_albums_and_songs(self) -> List[Album]:
        """
        Get albums and song from a specific folder and generates a list with dictionaries from it
        """
        albums = self.album_list_from_folder(self._musicdir)
        for album in albums:
            album.set_song_list(self.music_list_from_folder(album.location))
        return albums

    def album_list_from_folder(self, rootdir) -> List[Album]:
        # TODO: update documentation
        """ Generates a list of albums from specific directory
            every folder in the specified directory counts a an album.
            A list with dictionaries like this will be returned:
            Example:
            [ {'name': "House", 'location': "/music/House", song_count: 13},
            {name': "Rap", 'location': "/music/rap"} ]

        :param rootdir:
        :rtype: List[Album]
        """
        albums = []
        if os.path.isdir(rootdir):
            for selfdir, subdirs, files in os.walk(rootdir):
                name = selfdir.split("\\")[-1]
                location = selfdir
                song_count = 0
                for extension in self._allowed_extensions:
                    song_count += len(glob.glob1(selfdir, "*." + extension))
                albums.append(Album(name, location))

        self._albums = albums
        return albums

    def play(self, song_id):
        song = self.get_song_by_id(song_id)
        print("Trying to play " + c(song['name'], Colors.GREEN) + " with id: " + c(str(song_id), Colors.GREEN))
        self._current_song = self.v.media_new(song['file'].encode('utf-8', 'replace'))
        self._current_song.parse()
        print("\tDuration: " + str(self._current_song.get_duration()))
        self._player.set_media(self._current_song)
        self._player.play()
        pre_info = {"cur_song": song_id, "length": self._current_song.get_duration()}
        print("\tsending pre_info: " + json.dumps(pre_info))
        # conn.sendall(json.dumps(pre_info) + "\n")
        while not self._player.is_playing():
            continue
        # self.updateSongInfoThread = UpdateSongInfoThread(self._player)
        # self.updateSongInfoThread.start()

    def change_vol(self, vol):
        """
        Change the volume of the mpserver
        :param float vol:
        :return:
        """
        # TODO: send confirmation that volume changed
        if type(vol) is int:
            new_vol = constrain(vol, 0, 100)
        elif vol == "down":
            new_vol = constrain(self._player.audio_get_volume() - 3, 0, 100)
        elif vol == "up":
            new_vol = constrain(self._player.audio_get_volume() + 3, 0, 100)
        else:
            print("volume type not accepted (" + str(vol) + ")")
            return
        print("Setting volume to: " + str(new_vol))
        self._player.audio_set_volume(new_vol)

    def change_pos(self, pos):
        # TODO: change position of song and send update
        self._player.set_time(constrain(pos, 0, self._player.get_media().get_duration()))
        if not self._player.is_playing():
            self._player.play()

    def pause(self):
        if self._player.is_playing():
            self._player.pause()
        elif self._player.get_time() < self._player.get_media().get_duration():
            print(str(self._player.get_time()) + " - " + str(self._player.get_media().get_duration()))
            self._player.pause()
            # self.updateSongInfoThread = UpdateSongInfoThread(self._player)
            # self.updateSongInfoThread.start()

    def stop(self):
        self._player.stop()
        self._current_song = None

    def music_list_from_folder(self, rootdir) -> List[Song]:
        """ returns a list with music names in the directory specified.
            see allowed_extensions in config file for allowed extensions

            Returns a list with dictionaries
            like so: [{"name":"Best Music by someone","file":"path/to/file.mp3"}]

            :param rootdir: Folder to search for music files
            :type rootdir: str
            :return: The list with all music names in the specified folder
            :rtype: list
        """
        musiclist = []
        if os.path.isdir(rootdir):
            for musicfile in os.listdir(rootdir):
                if musicfile.endswith(tuple(self._allowed_extensions)):
                    song = Song(os.path.splitext(musicfile)[0],rootdir + "\\" + musicfile)
                    musiclist.append(song)
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")

    def music_list_from_album(self, albumid):
        # TODO create this functionality. A song list from an album should be generated
        if len(self._albums) > albumid >= 0:
            return self.music_list_from_folder(self._albums[albumid].location)
        else:
            raise IndexError('This album doesn\'t exists')

    def get_album_by_id(self, albumid):
        """
        Get an album by ID

        :param int albumid:
        :return:
        :rtype: dict
        """
        for album in self._albums:
            if album.id == albumid:
                return album
        return None

    def shutdown(self):
        """
        shutdown the musicplayer and clean up anything which needs to be cleaned up
        """
        self.log(c("shutting down", Colors.WARNING))
        self._player.stop()

    def playfile(self, file: str) -> bool:
        """
        Play a file without interrupting the original player

        :param file: the file to play
        :return: True if file played and False if file is not found
        :rtype: bool
        """
        if os.path.isfile(file):
            # create new player so it doesn't disturb the original
            player = self.v.media_player_new()
            media = self.v.media_new(file)
            player.set_media(media)
            player.play()
            return True
        else:
            return False

    def __process_conf__(self):
        self._allowed_extensions = set(self._config.get(self._section, 'allowed_extensions', fallback='mp3,wav').split(','))
        self._player.audio_set_volume(self._config.getint(self._section, 'start_volume', fallback=70))
        self._musicdir = self._config.get(self._section, 'musicdir', fallback='music')

    def __get_song_by_id__(self, song_id):
        for album in self._albums:
            for song in album.songlist:
                if song.id == song_id:
                    return song
        return None
