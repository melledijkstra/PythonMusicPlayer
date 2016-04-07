import socket

from Managers import MusicPlayer
from config import *
from tools import colors

HOST, PORT = socket.gethostname(), 1010
server = socket.socket()
musicplayer = MusicPlayer()


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
    print("Connection established | IP " + colors.OKBLUE + addr[0] + colors.ENDC + " | Port: " + str(addr[1]))
    return conn


def create_server():
    try:
        print("Binding socket - HOST: " + str(HOST) + " PORT: " + str(PORT))
        # bind to host and port then listen for connections
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
    except Exception as msg:
        print(colors.FAIL + "Bind failed: " + str(msg) + colors.ENDC)
    server.listen(5)


############################################################################

def process_command(cmd):
    cmd = cmd.upper()
    print(colors.ENDC + "Command: " + colors.OKBLUE + bytes(cmd).decode() + colors.ENDC)

    cmdlist = cmd.split(CMD_SEPERATOR)

    print(cmdlist)

    # LIST command for getting list of songs
    if cmdlist[0] == commands.LIST:
        # Get list of files
        try:
            songlist = musicplayer.musicListFromFolder("music")
            tmplist = []
            for musicitem in songlist:
                tmplist.append(musicitem["name"])
            response = ':'.join(tmplist)
        except IOError as e:
            print("IOError: " + str(e))
            response = "error " + e.message
    elif cmdlist[0] == commands.PLAYER:
        if len(cmdlist) > 1:
            response = musicplayer.process_command(cmdlist)
        else:
            response = commands.INVALID
    # OPTIONS for a list of options
    elif cmdlist[0] == commands.OPTIONS:
        commandlist = []
        for command in vars(commands).itervalues():
            command = str(command)
            if command.isupper():
                commandlist.append(command)
        response = CMD_SEPERATOR.join(commandlist)
    else:
        response = "INVALID_COMMAND"

    # every communication should be uppercase
    response = response.upper()
    print("RESPONSE: " + response)
    return response.upper() + "\n"


############################################################################

def conversation(conn):
    while True:
        try:
            # wait for input
            print("Waiting for input...")
            cmd = conn.recv(1024)
            cmd = str.decode(cmd)

            # check if command is empty string, if so then socket was probably disconnected
            if cmd == "":
                # if no data is present then socket is closed
                print("Client closed socket")
                conn.close()
                break

            if "\n" in cmd:
                cmd = cmd.replace("\n", "")

            cmd = cmd.upper()

            response = process_command(cmd)
            # send response uppercase, because the whole communication is uppercase
            response = response.upper()
            conn.send(response.encode())

        except socket.error as msg:
            print(colors.ENDC + "something went wrong: " + str(msg))
            conn = accept_connection()
        except Exception as msg:
            print(colors.ENDC + "Something went wrong " + str(msg))
            main()
    print(colors.FAIL + "Connection closed, wait for connections again..." + colors.ENDC)
    conn = accept_connection()
    conversation(conn)


def main():
    create_server()
    conn = accept_connection()
    conversation(conn)


# Start main program
if __name__ == '__main__':
    cmd = ""
    while cmd != "q":
        cmd = raw_input("Type command: ")
        process_command(cmd)
        # main()
