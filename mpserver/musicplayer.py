import os
from configparser import ConfigParser
import glob
import json
from typing import List, Union

import vlc

from mpserver.datastructures import Stack
from mpserver.interfaces import Logger
from mpserver.tools import constrain, Colors
from mpserver.tools import printcolor as c
from mpserver.musicmodels import Album, Song


class MusicPlayer(Logger):
    """ This class can play music with the vlc library
        it keeps track of which file it is playing. This class has play, pause, etc. controls
        It also manages which albums/songs there are
    """
    _section = 'musicplayer'

    def __init__(self, config: ConfigParser):
        super().__init__()
        self.v = vlc.Instance('--novideo')
        self._current_song = None
        self._player = self.v.media_player_new()
        self._config = config
        self.__process_conf__()
        self.log("allowed extensions: " + str(self._allowed_extensions))
        self.log("music directory: " + str(self._musicdir))
        self._albums = self.get_albums_and_songs()
        # store a limit of songs in memory that can be played by pressing previous
        self._songs_history = Stack(20)
        self.log("Albums found (" + str(len(self._albums)) + "): ")
        for album in self._albums:
            self.log(album)
        self._playfile(config.get(self._section + '/events', 'onready', fallback='resources/ready.mp3'));

    def get_albums_and_songs(self) -> List[Album]:
        """
        Get albums and song from a specific folder and generates a list with dictionaries from it
        """
        albums = self.album_list_from_folder(self._musicdir)
        for album in albums:
            album.set_song_list(self.music_list_from_folder(album.location))
        return albums

    def album_list_from_folder(self, rootdir: str) -> List[Album]:
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
                # check if we are walking though same dir as rootdir
                if selfdir == rootdir:
                    # if so then check if it should be an album specified in ini
                    if not self._config.getboolean(self._section, 'musiclocation_is_album', fallback=True):
                        continue
                    name = selfdir.replace('\\', '')
                else:
                    name = selfdir.split('\\')[-1]

                location = selfdir
                song_count = 0
                for extension in self._allowed_extensions:
                    song_count += len(glob.glob1(selfdir, "*." + extension))
                albums.append(Album(name, location))

        self._albums = albums
        return albums

    def play(self, song: Song, add_to_history=True):
        self.log("Trying to play " + c(song.title, Colors.GREEN) + " with id: " + c(str(song.id), Colors.GREEN))
        if add_to_history: self._songs_history.push(song)
        media = self.v.media_new(song.filepath)
        media.parse()
        print("\tDuration: " + str(media.get_duration()))
        self._player.set_media(media)
        self._player.play()
        pre_info = {"cur_song": song.id, "length": media.get_duration()}
        print("\tsending pre_info: " + json.dumps(pre_info))
        # conn.sendall(json.dumps(pre_info) + "\n")
        while not self._player.is_playing():
            continue
            # self.updateSongInfoThread = UpdateSongInfoThread(self._player)
            # self.updateSongInfoThread.start()

    def change_volume(self, volume: Union[str, int]):
        """
        Change the volume of the mpserver
        :param float volume:
        :return:
        """
        max = 100
        # TODO: send confirmation that volume changed
        if type(volume) is int:
            new_vol = constrain(volume, 0, max)
        elif volume == "down":
            new_vol = constrain(self._player.audio_get_volume() - 3, 0, max)
        elif volume == "up":
            new_vol = constrain(self._player.audio_get_volume() + 3, 0, max)
        else:
            self.log("volume type not accepted (" + str(volume) + ")")
            return
        print("Setting volume to: " + str(new_vol))
        self._player.audio_set_volume(new_vol)

    def change_pos(self, pos):
        # TODO: change position of song and send update
        self._player.set_time(constrain(pos, 0, self._player.get_media().get_duration()))
        if not self._player.is_playing():
            self._player.play()

    def play_previous(self):
        song = self._songs_history.pop() # type: Song
        self.play(song, add_to_history=False)

    def pause(self):
        self._player.pause()
        # self.updateSongInfoThread = UpdateSongInfoThread(self._player)
        # self.updateSongInfoThread.start()

    def stop(self):
        self._player.stop()

    def status(self) -> dict:
        # generate status dictionary
        return {
            'state': str(self._player.get_state()),
            'current_song': (self._current_song.id if self._current_song != None else None),
            'time': self._player.get_time(),
            'position': (self._player.get_position() * 100 if self._player.get_position() != -1 else -1),
            'length': self._player.get_length(),
            'volume': self._player.audio_get_volume(),
            'mute': self._player.audio_get_mute(),
        }

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
                    song = Song(os.path.splitext(musicfile)[0], rootdir + "\\" + musicfile)
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

    def _playfile(self, file: str, volume=50) -> bool:
        """
        Play a file without interrupting the original player

        :param file: the file to play
        :return: True if file played and False if file is not found
        :rtype: bool
        """
        if os.path.isfile(file):
            # create new player so it doesn't disturb the original
            player = self.v.media_player_new()
            player.audio_set_volume(constrain(int(volume),0,100))
            media = self.v.media_new(file)
            player.set_media(media)
            player.play()
            return True
        else:
            return False

    def __process_conf__(self):
        self._allowed_extensions = set(
            self._config.get(self._section, 'allowed_extensions', fallback='mp3,wav').split(','))
        self._player.audio_set_volume(self._config.getint(self._section, 'start_volume', fallback=70))
        self._musicdir = self._config.get(self._section, 'musiclocation', fallback='music').replace('/', '\\')

    def __get_song_by_id__(self, song_id):
        for album in self._albums:
            for song in album.songlist:
                if song.id == song_id:
                    return song
        return None

    def process_message__(self, message: dict):
        retdict = {'result': 'ok'} # type: dict
        if 'cmd' in message:
            # STATUS
            if message['cmd'] == 'status':
                retdict['status'] = self.status()
            # PLAY
            if message['cmd'] == 'play':
                if 'songid' in message and isinstance(message['songid'], int):
                    songid = int(message['songid'])
                    song = self.__find_song_by_id(songid)
                    if song != None:
                        self.play(song)
                    else:
                        retdict['result'] = 'error'
                        retdict['message'] = 'song with id ' + str(songid) + ' does not exist'
                else:
                    retdict['result'] = 'error'
                    retdict['message'] = 'songid is not an id or missing "songid"'
            # PAUSE
            elif message['cmd'] == 'pause':
                self.pause()
            # VOLUME UP
            elif message['cmd'] == 'changevol':
                if 'vol'in message:
                    self.change_volume(message['vol'])
                else:
                    retdict['result'] = 'error'
                    retdict['message'] = 'missing "vol"'
            # CHANGE POSITION
            elif message['cmd'] == 'changepos':
                if 'pos' in message:
                    self.set_position(int(message['pos']) / 100)
                else:
                    retdict['result'] = 'error'
                    retdict['message'] = 'vol not defined or not a number between 0-100'
                pass
            # GET SONGLIST
            elif message['cmd'] == 'songlist' and 'albumid' in message:
                album = self.__find_album_by_id(int(message['albumid']))
                if album != None:
                    retdict['albumid'] = album.id
                    retdict['songlist'] = [song.toDict() for song in album.get_songlist()]
                else:
                    retdict['result'] = 'error'
                    retdict['message'] = 'Album does not exist'
            # GET ALBUMLIST
            elif message['cmd'] == 'albumlist':
                retdict['albumlist'] = []
                for album in self._albums:
                    albumdict = album.toDict(False)
                    del albumdict['location']
                    retdict['albumlist'].append(albumdict)
            else:
                retdict['result'] = 'error'
                retdict['message'] = 'invalid command'
        return retdict

    def __find_album_by_id(self, albumid: int) -> Union[Album, None]:
        for album in self._albums:
            if album.id == albumid:
                return album
        return None

    def __find_song_by_id(self, song_id: int) -> Union[Song, None]:
        for album in self._albums:
            for song in album.songlist:
                if song.id == song_id:
                    return song
        return None

    def set_position(self, pos: float):
        pos = constrain(pos, 0, 1)
        self._player.set_position(pos)


if __name__ == '__main__':
    inifile = input("path to ini file: ")
    if os.path.isfile(inifile):
        config = ConfigParser()
        config.read_file(open(inifile))
        musicplayer = MusicPlayer(config)
        cmd = ''
        while cmd != 'quit':
            cmd = input('command for musicplayer: ')
            try:
                message = json.loads(cmd)
                response = musicplayer.process_message__(message)
                print(response)
            except json.JSONDecodeError as e:
                print(e)
    else:
        print("That's a not a file :/")
