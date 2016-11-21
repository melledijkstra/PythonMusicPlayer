# -*- coding: utf-8 -*-
import json
import os
import socket
import sys
import threading
import Queue
from musicplayer import *
from ConfigParser import SafeConfigParser

from config import *
from tools import colors as c

server = socket.socket()
conn = None
lock = threading.Lock()


# ////    ///////   ///////     //         //  ///////    ///////
# ///       //        //    //     //       //   //         //    //
# //        //        //    //      //     //    //         //    //
#   /////   ///////   //////         //   //     ///////    //////
#       //  //        //   //         // //      //         //   //
# ///////   ////////  //    //         ///       ////////   //   //


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
    config = SafeConfigParser(defaults={})
    config.readfp(open('config.ini'))

    musicserver = MusicServer(config)
    musicserver.serve()
    create_server()
    while True:
        global conn
        conn = accept_connection()
        conversation()


# Start main program
if __name__ == '__main__':
    # Check if program is run with root privileges, which is needed for socket communication
    if hasattr(os, 'getuid') and not os.getuid() == 0:
        sys.exit(
            c.WARNING + "root priveleges needed, try restarting with this command: 'sudo python server-v2.py'" + c.CLEAR)
    main()
