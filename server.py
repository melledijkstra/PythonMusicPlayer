import socket
import thread
import json

from musicplayer import MusicPlayer
from config import *
from tools import colors as c

server = socket.socket()
musicplayer = MusicPlayer()

lock = thread.allocate_lock()


#   ////    ///////   ///////     //         //  ///////    ///////
# ///       //        //    //     //       //   //         //    //
# //        //        //    //      //     //    //         //    //
#   /////   ///////   //////         //   //     ///////    //////
#       //  //        //   //         // //      //         //   //
# ///////   ////////  //    //         ///       ////////   //   //

def accept_connection():
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

def process_json(raw_json, conn):
    """
    This function processes the raw JSON decodes it, acts on the command(s) given and returns a response.
    A basic response exists of a {"result": "OK"} string
    :param raw_json:
    :return:
    """
    return_dict = {}
    try:
        data = json.loads(raw_json)
        print(c.ENDC + "JSON Data: " + c.OKBLUE + str(data) + c.ENDC)

        # LIST command for getting list of songs
        try:
            if data["cmd"] == commands.LIST:
                # Get list of files
                try:
                    songlist = musicplayer.musicListFromFolder("music")
                    return_dict["songlist"] = []
                    for song in songlist:
                        return_dict["songlist"].append(song["name"])
                except IOError as e:
                    print("IOError: " + str(e))
                    return_dict["result"] = "error"
                    return_dict["exception"] = str(e)
            elif data["cmd"] == commands.PLAYER:
                return_dict["MPLAYER"] = musicplayer.process_command(data, conn)
                pass
                # if len(cmdlist) > 1:
                #     response = musicplayer.process_command(cmdlist)
                # else:
                #     response = commands.INVALID
            # OPTIONS for a list of options
            elif data["cmd"] == commands.OPTIONS:
                commandlist = []
                for command in vars(commands).itervalues():
                    command = str(command)
                    if command.isupper():
                        commandlist.append(command)
                return_dict["options"] = commandlist
            elif data["cmd"] == commands.PING:
                return_dict["result"] = "OK"
            else:
                return_dict["result"] = "INVALID_COMMAND"
        except KeyError as e:
            pass

    except ValueError as e:
        print(c.FAIL + "incoming data not valid JSON: " + raw_json + c.ENDC)
        print(str(e))
        return_dict["result"] = "error"
        return_dict["exception"] = str(e)

    return json.dumps(return_dict, encoding="latin1")


############################################################################
############################################################################

def wait_and_receive(conn):
    """
    This function just waits when a new message comes in
    :param conn: The connection from which to listen
    :type conn: socket.socket
    :return:
    """
    buf = ''
    recv_buf = 1024
    data = True
    # check if data is empty string, if so then socket was probably disconnected then stop loop
    while data:
        try:
            print("\nWaiting for messages...\n")
            data = conn.recv(recv_buf)
            buf += data

            if data is "":
                break

            while buf.find('\n') != -1:
                line, buf = buf.split('\n', 1)
                # TODO: DO something with incoming line
                print("received: " + line)
                response = process_json(line, conn) + "\n"
                print("Sending: " + response)
                lock.acquire()
                conn.sendall(response)
                lock.release()
        except socket.error as msg:
            print(c.ENDC + "something went wrong: " + str(msg))
            conn = accept_connection()
            # if no data is present then socket is closed
    print("Client closed socket")
    conn.close()
    conn = accept_connection()
    conversation(conn)


def conversation(conn):
    # start new thread for listening for messages
    thread.start_new_thread(wait_and_receive, (conn,))
    while True:
        try:
            user_input = raw_input(c.OKGREEN + "Type something to send: " + c.ENDC)
            lock.acquire()
            conn.sendall(user_input + "\n")
            lock.release()
        except socket.error as msg:
            print(c.ENDC + "something went wrong: " + str(msg))
            conn = accept_connection()
            conversation(conn)
        except Exception as msg:
            print(c.ENDC + "Something went wrong " + str(msg))
            main()
    print(c.FAIL + "Connection closed, wait for connections again..." + c.ENDC)
    conn = accept_connection()
    conversation(conn)


def main():
    create_server()
    while True:
        conn = accept_connection()
        conversation(conn)


# Start main program
if __name__ == '__main__':
    # cmd = ""
    # while cmd != "q":
    #     cmd = raw_input("Type command: ")
    #     process_command(cmd)
    main()
