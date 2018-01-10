import json
import socket
import threading
import time
from configparser import RawConfigParser
from typing import Set

from mpserver.musicdownloader import MusicDownloader
from .interfaces import Logger, EventFiring
from .musicplayer import MusicPlayer
from .tools import colorstring as c, Colors


class MusicServer(Logger, EventFiring):
    """ The Music Server which the Android app connects with

    Attributes:
        listen      If true then server will keep accepting new connections
    """
    _section = 'musicserver'

    def __init__(self, config: RawConfigParser):
        """
        :param config:
        :type config: RawConfigParser
        """
        super(MusicServer, self).__init__()
        self.listen = True
        self._event_callbacks = {}
        for attribute in [attr for attr in dir(self.Events()) if not callable(attr) and not attr.startswith("__")]:
            self._event_callbacks[attribute] = []
        self._config = config
        self.__process_conf__()
        self._mplayer = MusicPlayer(self._config)
        # subscribe to musicplayer events so that clients get updates
        self._mplayer.subscribe(MusicPlayer.Events.PLAYING, self.update_clients)
        self._mplayer.subscribe(MusicPlayer.Events.PAUSING, self.update_clients)
        self._mplayer.subscribe(MusicPlayer.Events.FINISHED, self.update_clients)
        self._mplayer.subscribe(MusicPlayer.Events.VOLUME_CHANGE, self.update_clients)
        self._youtube_downloader = MusicDownloader(self._config)
        self._server = None
        self._clients = set()  # type: Set[socket.socket]

    def serve(self):
        """
        This method starts the music server and listens for incoming connections
        :return:
        """
        # Setup the server if needed
        if self._server is None:
            self.__setup_server__()
        self._server.listen(self._connection_count)
        while self.listen:
            conn = self.__accept_connections__()
            # open new thread for every connection
            t = ReceiveMessagesThread(conn, self.process_message, self.__on_connection_close)
            # make daemon so that the main thread can kill this thread, otherwise it would be stuck
            t.setDaemon(True)
            t.start()
            self._clients.add(conn)
            self.log("total connections: " + str(len(self._clients)))

    def __process_conf__(self):
        """
        Process the given configuration from ini file
        :return:
        """
        self._connection_count = self._config.get(self._section, 'connection_count', fallback=5)
        self._port = self._config.getint(self._section, 'port', fallback=1010)

    def __accept_connections__(self):
        self.log("Waiting for connection...")
        (conn, (ip, port)) = self._server.accept()
        self.log(c("Connection established | IP " + ip + " | Port: " + str(port), Colors.BLUE))
        self._mplayer.playfile(
            self._config.get(self._section + '/events', 'onconnected', fallback='resources/connected.mp3'),
            self._config.get(MusicPlayer._section, 'event_volume')
        )
        return conn

    def __setup_server__(self):
        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # set this option so that when we run this program again, we can reuse the address
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.log("Binding socket to port " + str(self._port))
            self._server.bind(('', self._port))
        except Exception as msg:
            self.log(c("Bind failed: " + str(msg), Colors.RED))
            # wait a few seconds then try again
            time.sleep(5)
            self.__setup_server__()

    def process_message(self, raw_message: str) -> str:
        """
        This function processes the raw message which comes from a client, acts on the command(s) given and returns a response.
        The response is in JSON format

        :param raw_message:
        :type raw_message: str
        :rtype: str
        """
        return_dict = {"result": "ok"}
        try:
            message = json.loads(raw_message)
            if isinstance(message, dict):
                if 'mplayer' in message:
                    return_dict['mplayer'] = self._mplayer.process_message(message['mplayer'])
                if 'youtube_dl' in message:
                    return_dict['youtube_dl'] = self._youtube_downloader.process_message(message['youtube_dl'])
        except json.JSONDecodeError as e:
            return_dict['result'] = 'error'
            return_dict['exception'] = str(e)
            return_dict['toast'] = 'Invalid JSON'
        return json.dumps(return_dict)

    def update_clients(self):
        self.log("updating status to all clients")
        for client in self._clients:
            response = json.dumps({"mplayer": {"control": self._mplayer.status()}})
            client.sendall(bytes(response + "\n", encoding='utf8'))

    def __on_connection_close(self, conn):
        self._fire_event(self.Events.DISCONNECTED)
        self._clients.discard(conn)

    def shutdown(self):
        self.log(c("shutting down", Colors.WARNING))
        self._stop_listening = True
        for client in self._clients:
            client.close()
        if self._server is not None:
            self._server.close()
        if self._mplayer is not None:
            self._mplayer.shutdown()

    def set_listen_state(self, state: bool):
        """
        Set the listening state of the musicserver
        """
        self.listen = state

    class Events:
        """
        This class has a collection of events that fire when the event happens.
        To subscribe on the event use:
        ```
        musicserver = MusicServer(config)
        musicserver.subsribe(MusicServer.Events.<event>, <your callable>)
        ```
        e.g.:
        ```
        musicserver.subcribe(MusicServer.Events.CONNECTED, self.onConnected)
        ```
        """
        CONNECTED = 1
        DISCONNECTED = 0


class ReceiveMessagesThread(Logger, threading.Thread):
    """
    # TODO: write documentation
    """

    def __init__(self, conn: socket.socket, message_received_callback, on_close_callback):
        super(ReceiveMessagesThread, self).__init__()
        self._callback = message_received_callback
        self._on_close = on_close_callback
        self._conn = conn

    def run(self):
        """
        This function just waits when a new message comes in
        :return:
        """
        buf = ""
        recv_buf = 1024
        data = True
        # check if data is empty string, if so then socket was probably disconnected then stop loop
        while data:
            try:
                # self.log(threading.current_thread().name+": Waiting for messages...")
                data = self._conn.recv(recv_buf)
                buf += str(data, 'utf-8')

                if data is "":
                    break

                while buf.find('\n') != -1:
                    line, buf = buf.split('\n', 1)
                    self.log(threading.current_thread().name + ": Received: " + c(line, Colors.BLUE))
                    response = self._callback(line)
                    # self.log(threading.current_thread().name+": Response: " + response)
                    self._conn.sendall(bytes(response + "\n", encoding='utf8'))
                    time.sleep(0.06)
            except Exception as e:
                print(c("something went wrong: " + str(e), Colors.RED))
                break
                # if no data is present then socket is closed
        self.log(threading.current_thread().name + ": " + c("Closing socket connection", Colors.WARNING))
        self._conn.close()
        self._on_close(self._conn)
        return
