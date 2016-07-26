# -*- coding: utf-8 -*-
import socket
import threading
import Queue
import json
import glob
import os
import time
import vlc
import tools

from config import *
from tools import colors as c


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
            song_info["cur_pos"] = self._player.get_time()
            song_info["cur_vol"] = self._player.audio_get_volume()
            try:
                conn.sendall(json.dumps(song_info) + "\n")
            except IOError as e:
                print("Error with sending updates: " + str(e))
                break
            time.sleep(0.1)
        print("Stopped sending updates")


class MusicPlayer:
    """ This class can play music with the pygame library
        it keeps track of which file it is playing and has play, pause, etc. controls
        Also it has a list of files it can play
    """
    # TODO: remove states if not used
    IDLE = 0
    PLAYING = 1
    PAUSED = 2

    _albums = []

    # This variable keeps status if music is playing or not
    _current_song = None
    _player = None

    updateSongInfoThread = None

    def __init__(self):
        self._player = v.media_player_new()
        self._player.audio_set_volume(80)

    def getmusiclist(self):
        return self._musiclist

    def process_json(self, data):
        """ This command processes commands for the music player

            :param data: The command for processing
            :type data: dict
        """
        # TODO: Clean up this function
        # Response dictionary
        return_dict = {"result": "ok"}
        try:
            if data["cmd"] == "play":
                try:
                    self.play(int(data["song_id"]))
                except Exception as e:
                    print("Exception: " + str(e))
                    return_dict["result"] = "error"
                    return_dict["exception"] = str(e)
            elif data["cmd"] == "pause":
                # TODO: create pausing functionality
                self.pause()
            elif data["cmd"] == "changepos":
                self.change_pos(int(data["pos"]))
            elif data["cmd"] == "changevol":
                self.change_vol(data["vol"])
        except IndexError as e:
            return_dict["result"] = "error"
            return_dict["exception"] = "invalid index " + str(e)
        except Exception as e:
            return_dict["result"] = "error"
            return_dict["exception"] = str(e)
        return return_dict

    def get_albums_and_songs(self, rootdir):
        """ Get albums and song from a specific folder and generates a dictionary from it

        :param rootdir:
        :return:
        """
        albums = self.album_list_from_folder(rootdir)
        for album in albums:
            album["songlist"] = self.music_list_from_folder(album["location"])
            print(album)
        return albums

    def album_list_from_folder(self, rootdir):
        """ Generates a list of albums from specific directory
            every folder in the specified directory counts a an album.
            A list with dictionaries like this will be returned:
            Example:
            [ {'name': "House", 'location': "/music/House", song_count: 13},
            {name': "Rap", 'location': "/music/rap"} ]

        :param rootdir:
        :return list:
        """
        albums = []
        if os.path.isdir(rootdir):
            for selfdir, subdirs, files in os.walk(rootdir):
                album = {'name': selfdir.split("\\")[-1], 'location': selfdir}
                song_count = 0
                for extension in allowed_extensions:
                    song_count += len(glob.glob1(selfdir, "*." + extension))
                album["song_count"] = song_count
                albums.append(album)
        self._albums = albums
        return albums

    def music_list_from_folder_recursive(self, rootdir):
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
                    if musicfile.endswith(allowed_extensions):
                        musiclist.append({"name": os.path.splitext(musicfile)[0], "file": subdir + "\\" + musicfile})
            # update instance musiclist and also return it
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")

    def play(self, song_id):
        song = self._musiclist[song_id]
        print("Trying to play " + c.OKGREEN + song['name'] + c.ENDC + " with id: " + c.OKGREEN + str(song_id) + c.ENDC)
        self._current_song = v.media_new(song["file"].encode('utf-8', 'replace'))
        self._current_song.parse()
        print("\tDuration: " + str(self._current_song.get_duration()))
        self._player.set_media(self._current_song)
        self._player.play()
        pre_info = {"cur_song": song_id, "length": self._current_song.get_duration()}
        print("\tsending pre_info: " + json.dumps(pre_info))
        conn.sendall(json.dumps(pre_info) + "\n")
        while not self._player.is_playing():
            continue
        self.updateSongInfoThread = UpdateSongInfoThread(self._player)
        self.updateSongInfoThread.start()

    def change_vol(self, vol):
        # TODO: send confirmation that volume changed
        if type(vol) is int:
            new_vol = tools.constrain(vol, 0, 100)
        elif vol == "down":
            new_vol = tools.constrain(self._player.audio_get_volume() - 3, 0, 100)
        elif vol == "up":
            new_vol = tools.constrain(self._player.audio_get_volume() + 3, 0, 100)
        else:
            print("volume type not accepted (" + str(vol) + ")")
            return
        print("Setting volume to: " + str(new_vol))
        self._player.audio_set_volume(new_vol)

    def change_pos(self, pos):
        # TODO: change position of song and send update
        self._player.set_time(tools.constrain(pos, 0, self._player.get_media().get_duration()))
        if not self._player.is_playing():
            self._player.play()

    def pause(self):
        if self._player.is_playing():
            self._player.pause()
        elif self._player.get_time() < self._player.get_media().get_duration():
            print(str(self._player.get_time()) + " - " + str(self._player.get_media().get_duration()))
            self._player.pause()
            self.updateSongInfoThread = UpdateSongInfoThread(self._player)
            self.updateSongInfoThread.start()

    def stop(self):
        self._player.stop()
        self._current_song = None

    def music_list_from_folder(self, rootdir):
        """ returns a list with music names in the directory specified.
            see allowed_extensions in config file for allowed extensions

            Returns a list with dictionaries
            like so: musiclist[{"name":"Best Music by someone","file":"path/to/file.mp3"}]

            :param rootdir: Folder to search for music files
            :type rootdir: str
            :return: The list with all music names in the specified folder
            :rtype: list
        """
        musiclist = []
        if os.path.isdir(rootdir):
            for musicfile in os.listdir(rootdir):
                if musicfile.endswith(allowed_extensions):
                    musiclist.append({"name": os.path.splitext(musicfile)[0], "file": rootdir + "\\" + musicfile})
            # update instance musiclist and also return it
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")


v = vlc.Instance()

server = socket.socket()
conn = None
lock = threading.Lock()

musicplayer = MusicPlayer()


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
    return_dict = {"result": "ok"}
    try:
        data = json.loads(raw_json)

        # LIST command for getting list of songs
        try:
            data["cmd"] = data["cmd"].upper()
            if data["cmd"] == commands.LIST:
                # get list of everything
                return_dict["albums"] = musicplayer.get_albums_and_songs(MUSIC_DIR)
                print(return_dict)
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
                    print(c.ENDC + "Received: " + c.OKBLUE + line + c.ENDC)
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
    main()
