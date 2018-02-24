import glob
import os
import time
from configparser import RawConfigParser
from typing import List, Union, Tuple

import vlc

from mpserver.config import LOG
from .datastructures import MusicQueue
from .grpc import mmp_pb2
from .grpc import mmp_pb2_grpc as rpc
from .interfaces import Logger, EventFiring
from .models import AlbumModel, SongModel
from .tools import colorstring as c
from .tools import constrain, Colors


class MusicPlayer(rpc.MusicPlayerServicer, Logger, EventFiring):
    """ This class can play music with the vlc library
        it keeps track of which file it is playing. This class has play, pause, etc. controls
        It also manages which albums/songs there are
    """
    _section = 'musicplayer'

    def __init__(self, config: RawConfigParser, logging=True):
        super(MusicPlayer, self).__init__()
        self.close_streams = False
        self.last_update_time = 0
        self.set_logging(logging)
        self.v = vlc.Instance('--novideo')  # type: vlc.Instance
        self._music_queue = MusicQueue()
        self._player = self.v.media_player_new()  # type: vlc.MediaPlayer
        self._player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.__song_finished)
        self._config = config
        self.__process_conf__()
        self.log("allowed extensions: " + str(self._allowed_extensions))
        self.log("music directory: " + str(self._musicdir))
        # load all albums on initialization
        self._albums = self.get_albums_and_songs()
        self.log("Albums found (" + str(len(self._albums)) + ")")
        self.playfile(
            config.get(self._section + '/events', 'onready', fallback='resources/ready.mp3').replace('\\', '/'))

    def get_albums_and_songs(self) -> List[AlbumModel]:
        """
        Get albums and song from a specific folder and generates a list with dictionaries from it
        """
        albums = self.album_list_from_folder(self._musicdir)
        for album in albums:
            album.set_song_list(self.music_list_from_folder(album.location))
        return albums

    def album_list_from_folder(self, rootdir: str) -> List[AlbumModel]:
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
                    name = os.path.basename(os.path.normpath(selfdir))
                else:
                    name = os.path.basename(os.path.normpath(selfdir))

                location = selfdir
                song_count = 0
                # check if album is empty
                for extension in self._allowed_extensions:
                    song_count += len(glob.glob1(selfdir, "*." + extension))
                if song_count > 0 or self._allow_empty_albums:
                    albums.append(AlbumModel(name, location))
        self._albums = albums
        return albums

    def play(self, song: SongModel, add_to_queue=True):
        """
        Plays a song

        :param song: The song object to play
        :param add_to_queue: Whether to add the song to the history queue
        :return:
        """
        self.log("Trying to play " + c(song.title, Colors.GREEN) + " with id: " + c(str(song.id), Colors.GREEN))
        # This can go wrong if another program is using the file
        try:
            if add_to_queue:
                self._music_queue.latest(song)
            self._player.set_mrl(song.filepath)
            self._player.play()
            # wait for song to actual playing
            while self._player.get_state() != vlc.State.Playing:
                pass
            self._fire_event(self.Events.PLAYING)
        except vlc.VLCException as e:
            print(e)

    def play_previous(self):
        """
        Play previous song from queue

        :return:
        """
        prev_song = self._music_queue.previous()
        if prev_song is not None:
            self._fire_event(self.Events.PLAY_PREV)
            self.play(prev_song, False)

    def play_next(self):
        """
        Play next song in queue

        :return:
        """
        next_song = self._music_queue.next()
        if next_song is not None:
            self._fire_event(self.Events.PLAY_NEXT)
            self.play(next_song, False)

    def __song_finished(self, event):
        """
        Song finished listener
        This fires when song is finished

        :param event:
        :return:
        """
        self.log("Song finished")
        # when song is finished play next song in the queue
        if self._music_queue.has_next():
            self.play_next()
        else:
            self._player.set_position(1)
            self._fire_event(self.Events.FINISHED)
            self.__update_clients()

    def change_volume(self, volume: int):
        """
        Change the volume

        :param float volume:
        :return:
        """
        # TODO: send confirmation that volume changed
        if type(volume) is int:
            new_vol = constrain(volume, 0, 100)
        else:
            self.log(c("volume type not accepted (" + str(volume) + ")", Colors.WARNING))
            return
        self.log("Setting volume to: " + str(new_vol))
        self._player.audio_set_volume(new_vol)
        self._fire_event(self.Events.VOLUME_CHANGE)

    def change_pos(self, pos):
        """
        Seek to location of current playing song

        :param pos:
        :return:
        """
        self._player.set_time(constrain(pos, 0, self._player.get_media().get_duration()))
        if not self._player.is_playing():
            self._player.play()

    def pause(self):
        """
        Pause the music

        :return:
        """
        self._player.pause()
        self._fire_event(self.Events.PAUSING)

    def stop(self):
        """
        Completely stop the music

        :return:
        """
        self._player.stop()
        self._fire_event(self.Events.STOPPING)

    def music_list_from_folder(self, rootdir) -> List[SongModel]:
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
            allow = tuple(self._allowed_extensions)
            for musicfile in os.listdir(rootdir):
                if musicfile.endswith(allow):
                    musiclist.append(SongModel(os.path.splitext(musicfile)[0], rootdir + os.sep + musicfile))
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")

    def song_list_from_album(self, albumid) -> List[SongModel]:
        """
        Creates a song list from an album id

        :param albumid: The album ID
        :return: The song list of this album
        :rtype: list
        """
        # TODO create this functionality. A song list from an album should be generated
        if len(self._albums) > albumid >= 0:
            return self.music_list_from_folder(self._albums[albumid].location)
        else:
            raise IndexError('This album doesn\'t exists')

    def get_album_by_id(self, albumid):
        """
        Get an album by ID

        :param int albumid:
        :return: The album object or None if album does not exist
        :rtype: AlbumModel
        """
        for album in self._albums:
            if album.id == albumid:
                return album
        return None

    def shutdown(self):
        """
        Shutdown the musicplayer and clean up anything which needs to be cleaned up
        """
        self.log(c("shutting down", Colors.WARNING))
        self.close_streams = True
        self._player.stop()

    def playfile(self, file: str) -> bool:
        """
        Play a file without interrupting the original player

        :param file: the file to play
        :return: True if file played and False if file is not found
        :rtype: bool
        """
        if self._player.get_state() != vlc.State.Playing:
            if os.path.isfile(file):
                # create new player so it doesn't disturb the original
                player = self.v.media_player_new()
                player.audio_set_volume(self._player.audio_get_volume())
                player.set_media(self.v.media_new(file))
                player.play()
                return True
            else:
                return False

    def __process_conf__(self):
        self._allowed_extensions = set(
            self._config.get(self._section, 'allowed_extensions', fallback='mp3,wav').split(','))
        self._player.audio_set_volume(self._config.getint(self._section, 'start_volume', fallback=70))
        self._musicdir = self._config.get(self._section, 'musiclocation', fallback='music').replace('\\', '/')
        self._allow_empty_albums = self._config.getboolean(self._section, 'allow_empty_albums', fallback=False)

    def __get_song_by_id(self, song_id):
        """
        Retrieve song by id
        Returns None when not found

        :param song_id:
        :return:
        """
        for album in self._albums:
            for song in album.songlist:
                if song.id == song_id:
                    return song
        return None

    def find_album_by_id(self, albumid: int) -> Union[AlbumModel, None]:
        """
        Find Album object by its ID

        :param albumid:
        :return: Album object or None if album not found
        """
        for album in self._albums:
            if album.id == albumid:
                return album
        return None

    def find_song_by_id(self, song_id: int) -> Union[Tuple[AlbumModel, SongModel], Tuple[None, None]]:
        """
        Find Song object by its ID, if not found None is returned for album and song

        :param song_id:
        :return: The album where song resides in and the song itself, or [None, None] if song is not found
        """
        for album in self._albums:
            for song in album.songlist:
                if song.id == song_id:
                    return album, song
        return None, None

    def set_position(self, pos: float):
        """
        Sets the position in the song

        :param pos: The position in the song as float indicated between 0 and 1
        """
        pos = constrain(pos, 0, 1)
        self._player.set_position(pos)
        self._fire_event(self.Events.POS_CHANGE)

    class Events:
        # TODO: make objects from events so more info is available about the event
        VOLUME_CHANGE = 9
        FINISHED = 8
        PLAY_NEXT = 7
        PAUSING = 6
        PLAY_PREV = 5
        POS_CHANGE = 4
        VOLUME_DOWN = 3
        VOLUME_UP = 2
        PLAYING = 1
        STOPPING = 0

    def __update_clients(self):
        if LOG:
            self.log("Updating clients")
        self.last_update_time = int(time.time())

    def RetrieveAlbumList(self, request: mmp_pb2.MediaData, context):
        alist = mmp_pb2.AlbumList()
        alist.album_list.extend([album.to_protobuf() for album in self._albums])
        return alist

    def RetrieveSongList(self, request: mmp_pb2.MediaData, context):
        response = mmp_pb2.SongList()
        album = self.find_album_by_id(request.id)
        if album is not None:
            response.album_id = album.id
            response.song_list.extend([song.to_protobuf() for song in album.songlist])
            return response
        else:
            self.log("Album does not exist")
            # TODO: add this to response
            # retdict['result'] = 'error'
            # retdict['message'] = 'Album does not exist'
        return response

    def Play(self, request, context):
        response = mmp_pb2.MMPResponse()
        if request.state == mmp_pb2.MediaControl.PLAY:
            if request.song_id != 0:
                album, song = self.find_song_by_id(request.song_id)
                if song is not None:
                    self.play(song)
                    self.__update_clients()
                    response.result = mmp_pb2.MMPResponse.OK
                else:
                    response.result = mmp_pb2.MMPResponse.ERROR
                    response.error = 'song with id ' + str(request.song_id) + ' does not exist'
        elif request.state == mmp_pb2.MediaControl.PAUSE:
            self.pause()
            self.__update_clients()
            response.result = mmp_pb2.MMPResponse.OK
        elif request.state == mmp_pb2.MediaControl.STOP:
            self.stop()
            self.__update_clients()
            response.result = mmp_pb2.MMPResponse.OK
        return response

    def ChangeVolume(self, request: mmp_pb2.VolumeControl, context):
        response = mmp_pb2.MMPResponse()
        self.change_volume(request.volume_level)
        self.__update_clients()
        response.result = mmp_pb2.MMPResponse.OK
        return response

    def ChangePosition(self, request: mmp_pb2.PositionControl, context):
        response = mmp_pb2.MMPResponse()
        pos = request.position
        if 0 <= pos < 100:
            self.set_position(int(pos) / 100)
            self.__update_clients()
            response.result = mmp_pb2.MMPResponse.OK
        else:
            response.result = mmp_pb2.MMPResponse.ERROR
            response.error = 'vol not defined or not a number between 0-100'
        return response

    def Previous(self, request: mmp_pb2.PlaybackControl, context):
        response = mmp_pb2.MMPResponse()
        self.play_previous()
        self.__update_clients()
        response.result = mmp_pb2.MMPResponse.OK
        return response

    def Next(self, request: mmp_pb2.PlaybackControl, context):
        response = mmp_pb2.MMPResponse()
        self.play_next()
        self.__update_clients()
        response.result = mmp_pb2.MMPResponse.OK
        return response

    def RetrieveMMPStatus(self, request: mmp_pb2.MMPStatusRequest, context):
        return self.__get_status()

    def RegisterMMPNotify(self, request, context):
        self.playfile(self._config.get(self._section + '/events', 'onconnected', fallback='resources/connected.mp3'))
        # when client subscribes return first status
        yield self.__get_status()
        last_status_time = int(time.time())
        # keep this stream open so we can push updates when needed
        while not self.close_streams:
            # keep checking if clients should be notified
            while self.last_update_time > last_status_time:
                last_status_time = self.last_update_time
                yield self.__get_status()

    def AddNext(self, request: mmp_pb2.MediaData, context):
        # TODO: Check if request is for album or song
        response = mmp_pb2.MMPResponse()
        album, song = self.find_song_by_id(request.id)
        if song is not None:
            self._music_queue.add_next(song)
            response.result = mmp_pb2.MMPResponse.OK
            response.message = 'Song will be played next'
        else:
            response.result = mmp_pb2.MMPResponse.ERROR
            response.message = 'song with id ' + str(request.id) + ' does not exist'
        return response

    def AddToQueue(self, request, context):
        # TODO: Check if request is for album or song
        response = mmp_pb2.MMPResponse()
        album, song = self.find_song_by_id(request.id)
        if song is not None:
            self._music_queue.add(song)
            response.result = mmp_pb2.MMPResponse.OK
            response.message = 'Song added to queue'
        else:
            response.result = mmp_pb2.MMPResponse.ERROR
            response.message = 'song with id ' + str(request.id) + ' does not exist'
        return response

    def get_queue(self) -> MusicQueue:
        return self._music_queue

    def __get_status(self):
        status = mmp_pb2.MMPStatus()
        try:
            # get current vlc state -> replace "State." part -> to uppercase = this should match proto state
            status.state = mmp_pb2.MMPStatus.State.Value(str(self._player.get_state()).replace('State.', '').upper())
        except ValueError:
            status.state = mmp_pb2.MMPStatus.NOTHINGSPECIAL
        current_song = self._music_queue.current()
        if current_song is not None:
            status.current_song.CopyFrom(current_song.to_protobuf())
        status.volume = self._player.audio_get_volume()
        status.mute = bool(self._player.audio_get_mute())
        status.position = int(self._player.get_position() * 100 if self._player.get_position() != -1 else -1)
        status.elapsed_time = int(self._player.get_time() / 1000 if self._player.get_time() != -1 else -1)
        return status
