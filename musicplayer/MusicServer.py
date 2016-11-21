import socket
import threading

class MusicServer:
    """ The Music Server which the Android app connects with """
    def __init__(self, config):
        self._conn = socket.socket

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
