import socket
import threading
import Queue
import json
import os
import time

from config import *
from pygame import mixer
from tools import colors as c

# for some reason if you initialize pygame and then the mixer, there is no sound on windows (weird?)
# pygame.init()
# Only 1 channel for playing the music
mixer.init(channels=1)

server = socket.socket()
conn = None
lock = threading.Lock()


class MusicPlayer:
    """ This class can play music with the pygame library
        it keeps track of which file it is playing and has play, pause, etc. controls
        Also it has a list of files it can play
    """
    # format musiclist[0] = {"name": "Best Music by Someone", "file": "C:/path/to/file.mp3"}
    _musiclist = []
    # This variable keeps status if music is playing or not
    _isPlaying = False
    current_song = None

    def __init__(self):
        self.music_list_form_folder('music')

    def isplaying(self):
        return self._isPlaying

    def getmusiclist(self):
        return self._musiclist

    def process_json(self, data):
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
        try:
            if data["cmd"] == "play":
                songid = int(data["song_id"])
                song = self._musiclist[songid]
                print("Trying to play '" + song['name'] + "' with id: " + str(songid))
                self.current_song = mixer.Sound(song["file"].replace("\\", "/"))
                print("length: " + self.current_song.get_length())
                self.current_song.play()
                self._isPlaying = True
                # TODO: put this in main thread and use Queue to also receive messages in new thread
                # for pausing and fading and what not ;p
                while mixer.get_busy():
                    return_dict["cur_song"] = songid
                    return_dict["cur_pos"] = mixer.music.get_pos()
                    return_dict["cur_vol"] = mixer.music.get_volume()
                    print("Sending: " + json.dumps(return_dict))
                    lock.acquire()
                    conn.sendall(json.dumps(return_dict) + "\n")
                    lock.release()
                    time.sleep(0.5)
                self._isPlaying = False
                print("Stopped playing song: " + song["name"])
            elif data["cmd"] == "pause":
                # TODO: create pausing functionality

                pass
            elif data["cmd"] == "changepos":
                if self._isPlaying and self.current_song.get_length() > data["pos"]:
                    self.current_song
                pass
        except IndexError as e:
            return_dict["result"] = "error"
            return_dict["exception"] = str(e)
        except Exception as e:
            return_dict["result"] = "error"
            return_dict["exception"] = str(e)
        return return_dict

    def music_list_form_folder(self, rootdir):
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
                    # prepend a dot before extension in allowed_extensions
                    if musicfile.endswith(["." + extension for extension in allowed_extensions]):
                        musiclist.append({"name": os.path.splitext(musicfile)[0], "file": subdir + "\\" + musicfile})
            # update instance musiclist and also return it
            self._musiclist = musiclist
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")


# ////    ///////   ///////     //         //  ///////    ///////
# ///       //        //    //     //       //   //         //    //
# //        //        //    //      //     //    //         //    //
#   /////   ///////   //////         //   //     ///////    //////
#       //  //        //   //         // //      //         //   //
# ///////   ////////  //    //         ///       ////////   //   //

def accept_connection():
    global conn
    # wait for connection
    print("Waiting for connection...")
    conn, addr = server.accept()
    print("Connection established | IP " + c.OKBLUE + addr[0] + c.ENDC + " | Port: " + str(addr[1]))
    return conn


def create_server():
    try:
        print(
            "Binding socket - HOST: " + (str(HOST) if str(HOST) is not "" else "0.0.0.0 (everyone)") + " PORT: " + str(
                PORT))
        # bind to host and port then listen for connections
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
    except Exception as msg:
        print(c.FAIL + "Bind failed: " + str(msg) + c.ENDC)
    server.listen(5)


############################################################################
# COMMAND PROCESSING
############################################################################

def process_json(raw_json):
    """
    This function processes the raw JSON decodes it, acts on the command(s) given and returns a response.
    A basic response exists of a {"result": "OK"} string
    :param raw_json:
    :return:
    """
    global conn
    return_dict = {}
    try:
        data = json.loads(raw_json)
        print(c.ENDC + "JSON Data: " + c.OKBLUE + str(data) + c.ENDC)

        # LIST command for getting list of songs
        try:
            data["cmd"] = data["cmd"].upper()
            if data["cmd"] == commands.LIST:
                # Get list of files
                try:
                    songlist = musicplayer.music_list_form_folder("music")
                    return_dict["songlist"] = []
                    for song in songlist:
                        return_dict["songlist"].append(song["name"])
                except IOError as e:
                    print("IOError: " + str(e))
                    return_dict["result"] = "error"
                    return_dict["exception"] = str(e)
            elif data["cmd"] == commands.PLAYER:
                try:
                    musicplayer.process_json(data["mplayer"])
                except IndexError as e:
                    print("No mplayer field in JSON")
                    return_dict["result"] = "error"
                    return_dict["exception"] = str(e)
            # OPTIONS for a list of options
            elif data["cmd"] == commands.OPTIONS:
                commandlist = []
                for command in vars(commands).itervalues():
                    command = str(command)
                    if command.isupper():
                        commandlist.append(command)
                return_dict["options"] = commandlist
            elif data["cmd"] == commands.PING:
                return_dict["ping"] = "OK"
            else:
                return_dict["result"] = "INVALID_COMMAND"
        except KeyError as e:
            return_dict["result"] = "error"
            return_dict["exception"] = str(e)
            pass

    except ValueError as e:
        print(c.FAIL + "incoming data not valid JSON: " + raw_json + c.ENDC)
        print(str(e))
        return_dict["result"] = "error"
        return_dict["exception"] = str(e)

    return json.dumps(return_dict, encoding="latin1")


############################################################################
############################################################################

class ReceiveMessagesThread(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        super(ReceiveMessagesThread, self).__init__()

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
                    print("received: " + line)
                    self.queue.put(line)
            except socket.error as msg:
                print(c.ENDC + "something went wrong: " + str(msg))
                conn = accept_connection()
                # if no data is present then socket is closed
        print("Client closed socket")
        conn.close()
        conn = accept_connection()
        conversation()


def conversation():
    q = Queue.Queue()
    global conn
    if conn is None:
        return
    # start new thread for listening for messages
    ReceiveMessagesThread(q).start()
    while True:
        try:
            while True:
                received_line = q.get()
                print("Received from other thread: " + received_line)
                response = process_json(received_line)
                print("Response: " + response)
                conn.sendall(response + "\n")
        except socket.error as msg:
            print(c.ENDC + "something went wrong: " + str(msg))
            conn = accept_connection()
            conversation()
        except Exception as msg:
            print(c.ENDC + "Something went wrong " + str(msg))
            main()
    print(c.FAIL + "Connection closed, wait for connections again..." + c.ENDC)
    conn = accept_connection()
    conversation()


def is_connected():
    global conn
    return conn is not None


def main():
    create_server()
    while True:
        global conn
        conn = accept_connection()
        conversation()


# Start main program
if __name__ == '__main__':
    musicplayer = MusicPlayer()
    main()
