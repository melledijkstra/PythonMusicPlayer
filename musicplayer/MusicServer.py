import socket
import threading
from tools import colors as c


class MusicServer:
    """ The Music Server which the Android app connects with """

    def __init__(self, config):
        self._conn = socket.socket
        self.__process_conf__(config)

    def serve(self):
        """
        This method starts the music server and listens for incoming connections
        :return:
        """
        pass

    def __process_conf__(self, conf):
        """
        Process the given configuration from ini file
        :return:
        """
        # TODO: process the configuration given

    def __accept_connection__(self):
        # wait for connection
        print("Waiting for connection...")
        conn, addr = self._conn.accept()
        print("Connection established | IP " + c.OKBLUE + addr[0] + c.CLEAR + " | Port: " + str(addr[1]))
        return conn

    def create_server():
        try:
            print(
                "Binding socket - HOST: " + (
                    str(HOST) if str(HOST) is not "" else "0.0.0.0 (listen to everyone)") + " PORT: " + str(
                    PORT))
            # bind to host and port then listen for connections
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
        except Exception as msg:
            print(c.FAIL + "Bind failed: " + str(msg) + c.CLEAR)
            time.sleep(5)
            create_server()
        setup_server()
        server.listen(5)

    class ReceiveMessagesThread(threading.Thread):
        def __init__(self, queue):
            super(ReceiveMessagesThread, self).__init__()
            self.queue = queue

        def run(self):
            """
            This function just waits when a new message comes in
            :return:
            """
            global conn
            buf = ''
            recv_buf = 1024
            data = True
            # check if data is empty string, if so then socket was probably disconnected then stop loop
            while data:
                try:
                    print("Waiting for messages...")
                    data = conn.recv(recv_buf)
                    buf += data

                    if data is "":
                        break

                    while buf.find('\n') != -1:
                        line, buf = buf.split('\n', 1)
                        print(c.CLEAR + "Received: " + c.OKBLUE + line + c.CLEAR)
                        self.queue.put(line)
                        time.sleep(0.1)
                except socket.error as msg:
                    print(c.CLEAR + "something went wrong: " + str(msg))
                    conn = accept_connection()
                    # if no data is present then socket is closed
            print("Client closed socket")
            conn.close()
            conn = accept_connection()
            conversation()

    class UpdateSongInfoThread(threading.Thread):
        def __init__(self, player):
            self._player = player
            super(UpdateSongInfoThread, self).__init__()

        def run(self):
            global conn
            song_info = {}
            print("Sending updates started")
            while self._player.get_time() == 0:
                pass
            while self._player.is_playing():
                song_info['cur_pos'] = self._player.get_time()
                song_info['cur_vol'] = self._player.audio_get_volume()
                try:
                    conn.sendall(json.dumps(song_info) + "\n")
                except IOError as e:
                    print("Error with sending updates: ", e)
                    break
                time.sleep(0.1)
            print("Stopped sending updates")
