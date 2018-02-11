from concurrent import futures
from configparser import RawConfigParser

import grpc

# Generated gRPC classes
from mpserver.datamanager import DataManager
from .grpc import mmp_pb2_grpc as rpc

from .mediadownloader import MediaDownloader
from .interfaces import Logger, EventFiring
from .musicplayer import MusicPlayer
from .tools import colorstring as c, Colors


class MusicServer(Logger, EventFiring):
    """
    The Music Server which the client apps connects with.
    It sets up all of the different components and a gRPC server
    """
    _config_section = 'musicserver'

    def __init__(self, config: RawConfigParser):
        """
        :param config: The configuration for the music server
        :type config: RawConfigParser
        """
        super(MusicServer, self).__init__()
        self._event_callbacks = {}
        # initialize callback lists
        for attribute in [attr for attr in dir(self.Events()) if not callable(attr) and not attr.startswith("__")]:
            self._event_callbacks[attribute] = []
        self._config = config
        self.__process_conf__()
        # setup server components
        self._mplayer = MusicPlayer(config)
        self.__subscribe_listeners()
        self._media_downloader = MediaDownloader(self._config)
        self._data_manager = DataManager(self._mplayer, config)
        # Setup gRPC Server
        self._gserver = grpc.server(futures.ThreadPoolExecutor(max_workers=self._connection_count))
        rpc.add_MusicPlayerServicer_to_server(self._mplayer, self._gserver)
        rpc.add_DataManagerServicer_to_server(self._data_manager, self._gserver)
        rpc.add_MediaDownloaderServicer_to_server(self._media_downloader, self._gserver)
        self._gserver.add_insecure_port('[::]:' + str(self._port))

    def __subscribe_listeners(self):
        """
        Subscribe to music player events

        :return:
        """
        # self._mplayer.subscribe(MusicPlayer.Events.PLAYING, self.update_clients)
        # self._mplayer.subscribe(MusicPlayer.Events.PAUSING, self.update_clients)
        # self._mplayer.subscribe(MusicPlayer.Events.FINISHED, self.update_clients)
        # self._mplayer.subscribe(MusicPlayer.Events.VOLUME_CHANGE, self.update_clients)

    def serve(self):
        """
        This method starts the music server and listens for incoming connections
        """
        cmd = ''
        self._gserver.start()
        self.log("gRPC Server started... (port: " + str(self._port) + ")")
        while cmd != "exit":
            print(c("Command line functionality coming soon (type 'exit' to exit for now)", Colors.PINK))
            cmd = input("$-> ")
        self._gserver.stop(0)

    def __process_conf__(self):
        """
        Process the given configuration from ini file
        :return:
        """
        self._connection_count = self._config.get(self._config_section, 'connection_count', fallback=5)
        self._port = self._config.getint(self._config_section, 'port', fallback=1010)

    def shutdown(self):
        self.log(c("shutting down", Colors.WARNING))
        self._mplayer.shutdown()
        if self._gserver is not None:
            self._gserver.stop(0)
