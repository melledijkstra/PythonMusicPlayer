import os
from configparser import RawConfigParser

from mpserver.musicplayer import MusicPlayer
from .grpc import mmp_pb2
from .grpc import mmp_pb2_grpc as rpc
from .interfaces import Logger, EventFiring
from .models import SongModel
from .tools import Colors
from .tools import colorstring as c


class DataManager(rpc.DataManagerServicer, Logger, EventFiring):
    """
    DataManager class
    """

    _section = 'datamanager'

    def __init__(self, mplayer: MusicPlayer, config: RawConfigParser):
        super(DataManager, self).__init__()
        self._mplayer = mplayer
        self._config = config
        self.__process_conf()

    class Events:
        DOWNLOAD_FINISHED = 1
        DOWNLOAD_UPDATE = 0

    def __process_conf(self):
        pass

    def renamesong(self, song: SongModel, newtitle: str):
        current_song = self._mplayer.get_queue().current()
        if current_song is not None and current_song.id == song.id:
            raise RenameException("Can not rename song which is currently playing")
        if newtitle != "":
            try:
                self.log("Renaming " + song.title + " to " + newtitle)
                _, ext = os.path.splitext(song.filepath)
                self.log(song.filepath + "  ->  " + os.path.dirname(song.filepath) + os.sep + newtitle + ext)
                os.rename(song.filepath, os.path.dirname(song.filepath) + os.sep + newtitle + ext)
                return True
            # TODO: don't catch these errors, let upper level work with that
            except OSError as e:
                self.log(c(e, Colors.RED))
        return False

    def DeleteAlbum(self, request, context):
        return super().DeleteAlbum(request, context)

    def DeleteSong(self, request, context):
        return super().DeleteSong(request, context)

    def RenameAlbum(self, request, context):
        return super().RenameAlbum(request, context)

    def RenameSong(self, request: mmp_pb2.RenameData, context):
        response = mmp_pb2.MMPResponse()
        album, song = self._mplayer.find_song_by_id(request.id)
        if song is not None:
            try:
                self.renamesong(song, request.new_title)
            except RenameException as e:
                response.result = mmp_pb2.MMPResponse.ERROR
                response.message = "Could not rename this song"
                response.error = str(e)
        else:
            response.result = mmp_pb2.MMPResponse.ERROR
            response.message = 'song with id ' + str(request.id) + ' does not exist'
        return response

    def MoveSong(self, request, context):
        return super().MoveSong(request, context)


class RenameException(Exception):
    """
    TODO: write documentation
    """
