import json
import socket
import time
import threading

from configparser import ConfigParser
from typing import List

from .musicplayer import MusicPlayer
from .interfaces import Logger
from .tools import printcolor as c, Colors


class MusicServer(Logger):
    """ The Music Server which the Android app connects with """
    _section = 'musicserver'

    def __init__(self, config: ConfigParser):
        """
        :param config:
        :type config: ConfigParser
        """
        super().__init__()
        self._listen = True
        self._eventcallback = set()
        self._config = config
        self.__process_conf__()
        self._mplayer = MusicPlayer(self._config)
        self._server = None
        self._clients = [] # type: List[threading.Thread]

    def serve(self):
        """
        This method starts the music server and listens for incoming connections
        :return:
        """
        # Setup the server if needed
        if self._server is None:
            self.__setup_server__()
        self._server.listen(self._connection_count)
        while self._listen:
            conn = self.__accept_connections__()
            # open new thread for every connection
            t = ReceiveMessagesThread(conn, self.__process_message__)
            # make daemon so that the main thread can kill this thread, otherwise it would be stuck
            t.setDaemon(True)
            t.start()
            self._clients.append(t)
            self.log("connection count: "+str(len(self._clients)))


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
        self._mplayer.playfile(self._config.get('musicserver/events', 'onconnected', fallback='resources/connected.mp3'))
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

    def __process_message__(self, raw_json: str) -> dict:
        """
        This function processes the raw JSON decodes it, acts on the command(s) given and returns a response.
        A basic response exists of a {"result": "OK"} string

        :param raw_json:
        :type raw_json: str
        :rtype: str
        """
        return_dict = {"result": "ok"}
        try:
            message = json.loads(raw_json)
        except json.JSONDecodeError as e:
            return_dict['result'] = 'error'
            return_dict['toast'] = 'invalid json'
        return json.dumps(return_dict)

    def shutdown(self):
        self.log(c("shutting down",Colors.WARNING))
        self._stop_listening = True
        for client in self._clients:
            client._stop()
        if self._server is not None:
            self._server.close()
        if self._mplayer is not None:
            self._mplayer.shutdown()

    def set_listen_state(self, state: bool):
        """
        Set the listening state of the musicserver
        """
        self._listen = state


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
        CONNECTED = 'connected'
        DISCONNECTED = 'disconnected'

    def subcsribe(self, event: str, callback):
        events = [attr for attr in dir(self.Events) if not callable(attr) and not attr.startswith("__")]
        if event in events:
            self._eventcallback[event].append(callback)

class ReceiveMessagesThread(threading.Thread, Logger):
    def __init__(self, conn: socket.socket, message_received_callback):
        super().__init__()
        self._callback = message_received_callback
        self._conn = conn

    def run(self):
        """
        This function just waits when a new message comes in
        :return:
        """
        buf = ''
        recv_buf = 1024
        data = True
        # check if data is empty string, if so then socket was probably disconnected then stop loop
        while data:
            try:
                self.log(threading.current_thread().name+": Waiting for messages...")
                data = self._conn.recv(recv_buf)
                buf += str(data, 'utf-8')

                if data is "":
                    break

                while buf.find('\n') != -1:
                    line, buf = buf.split('\n', 1)
                    self.log(threading.current_thread().name+": Received: " + c(line, Colors.BLUE))
                    response = self._callback(line)
                    print("Response: " + response)
                    self._conn.sendall(bytes(response + "\n", encoding='utf8'))
                    time.sleep(0.1)
            except socket.error as msg:
                print(c("something went wrong: " + str(msg), Colors.RED))
                break
                # if no data is present then socket is closed
        self.log(threading.current_thread().name+": "+c("Client closed socket", Colors.WARNING))
        self._conn.close()
        return

