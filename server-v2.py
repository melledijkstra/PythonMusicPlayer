# -*- coding: utf-8 -*-
import socket
import threading
import Queue
import json
import glob
import os
import time

import sys
import vlc
import tools

from config import *
from tools import colors as c

v = vlc.Instance()

server = socket.socket()
conn = None
lock = threading.Lock()


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

    def get_albums_and_songs(self, rootdir):
        """ Get albums and song from a specific folder and generates a dictionary from it

        :param rootdir:
        :return:
        """
        albums = self.album_list_from_folder(rootdir)
        for album in albums:
            album['songlist'] = self.music_list_from_folder(album['location'])
            print(album)
        return albums

    def album_list_from_folder(self, rootname):
        """ Generates a list of albums from specific directory
            every folder in the specified directory counts a an album.
            A list with dictionaries like this will be returned:
            Example:
            [ {'name': "House", 'location': "/music/House", song_count: 13},
            {name': "Rap", 'location': "/music/rap"} ]

        :param rootname:
        :return list:
        """
        albums = []

        if os.path.isdir(rootname):
            for selfdir, subdirs, files in os.walk(rootname):
                album = {'name': selfdir.split("\\")[-1], 'location': selfdir}
                song_count = 0
                for extension in allowed_extensions:
                    song_count += len(glob.glob1(selfdir, "*." + extension))
                album['song_count'] = song_count
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
        print(
            "Trying to play " + c.OKGREEN + song['name'] + c.CLEAR + " with id: " + c.OKGREEN + str(song_id) + c.CLEAR
        )
        self._current_song = v.media_new(song['file'].encode('utf-8', 'replace'))
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
        """
        Change the volume of the musicplayer
        :param float vol:
        :return:
        """
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

    def music_list_from_album(self, albumid):
        # TODO create this functionality. A song list from an album should be generated
        if len(self._albums) > albumid >= 0:
            return self.music_list_from_folder(self._albums[albumid]['location'])
        else:
            raise IndexError('This album doesn\'t exists')

    def init(self):
        """ Initializing musicplayer, scanning directory for albums and song, etc. """
        self._albums = self.album_list_from_folder(MUSIC_DIR)

    def get_album_by_id(self, albumid):
        """
        Get an album by ID

        :param int albumid:
        :return:
        :rtype: dict
        """
        return self._albums[albumid] if len(self._albums) > albumid > 0 else False

# set global musicplayer
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


def setup_server():
    musicplayer.init()


############################################################################
# COMMAND PROCESSING
############################################################################

def process_mplayer(_json):
    """
    This command processes commands for the music player

        :param _json: The command for processing
        :type _json: dict
        :rtype: dict
    """
    # Response dictionary
    return_dict = {"result": "ok"}
    try:
        if 'ctrl' in _json:
            _ctrl = commands.mplayer.ctrl
            if _json['ctrl']['cmd'] == _ctrl.PLAY and isinstance(_json['ctrl']['songid'], int):
                try:
                    musicplayer.play(_json['song_id'])
                except Exception as e:
                    print("Exception when trying to play a song: ", e)
                    return_dict['result'] = "error"
                    return_dict['message'] = str(e)
            elif _json['ctrl']['cmd'] == _ctrl.PAUSE:
                # TODO: create pausing functionality
                musicplayer.pause()
            elif _json['ctrl']['cmd'] == _ctrl.CHANGEPOS:
                musicplayer.change_pos(int(_json['pos']))
            elif _json['ctrl']['cmd'] == _ctrl.CHANGEVOL:
                musicplayer.change_vol(float(_json['vol']))
        elif 'data' in _json:
            _data = commands.mplayer.data
            if _json['data']['cmd'] == _data.LIST and 'type' in _json['data']:
                if _json['data']['type'] == _data.ALBUM:
                    return_dict['albumlist'] = musicplayer.album_list_from_folder(MUSIC_DIR)
                if _json['data']['type'] == _data.SONG:
                    if 'albumid' in _json['data'] and isinstance(_json['data']['albumid'], int):
                        return_dict['album'] = musicplayer.get_album_by_id(_json['data']['albumid'])
                        return_dict['songlist'] = musicplayer.music_list_from_album(_json['data']['albumid'])
                    else:
                        return_dict['songlist'] = musicplayer.music_list_from_folder_recursive(MUSIC_DIR)
    except IndexError as e:
        return_dict['result'] = "error"
        return_dict['message'] = "invalid index " + str(e)
    except Exception as e:
        return_dict['result'] = "error"
        return_dict['message'] = str(e)
    return return_dict


def process_youtube(data):
    """This function processes the json relative to youtube functionality

    :param data:
    :type data: dict
    :rtype: dict
    """
    # TODO: youtube_dl for downloading urls and put it in a specific folder specified by user
    youtube = {"result": "ok"}
    print("Downloading...")
    return youtube


def process_json(raw_json):
    """
    This function processes the raw JSON decodes it, acts on the command(s) given and returns a response.
    A basic response exists of a {"result": "OK"} string

    :param raw_json:
    :type raw_json: str
    :rtype: str
    """
    return_dict = {"result": "ok"}
    try:
        data = json.loads(raw_json)
        if commands.PLAYER in data:
            return_dict['mplayer'] = process_mplayer(data[commands.PLAYER])
        if commands.YOUTUBE in data:
            return_dict['youtube'] = process_youtube(data[commands.YOUTUBE])

    except ValueError as e:
        print(c.FAIL + "incoming data not valid JSON: " + raw_json + c.CLEAR)
        print(str(e))
        return_dict['result'] = "error"
        return_dict['message'] = str(e)

    return json.dumps(return_dict, encoding="utf-8")


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
            print(c.CLEAR + "something went wrong: " + str(msg))
            conn = accept_connection()
            conversation()
        except Exception as msg:
            print(c.CLEAR + "Something went wrong " + str(msg))
            main()
    print(c.FAIL + "Connection closed, wait for connections again..." + c.CLEAR)
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
    if hasattr(os, 'getuid') and not os.getuid() == 0:
        sys.exit(
            c.WARNING + "root priveleges needed, try restarting with this command: 'sudo python server-v2.py'" + c.CLEAR)
    main()
