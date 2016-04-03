import socket

from Managers import FileManager
from config import commands
from tools import colors

HOST, PORT = socket.gethostname(), 1010
server = socket.socket()
filemanager = FileManager()


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
    print(colors.ENDC + "Command: " + colors.OKBLUE + bytes(cmd).decode() + " " + colors.ENDC)

    # LIST command for getting list of songs
    if cmd == commands.LIST:
        # Get list of files
        try:
            songlist = filemanager.musiclistfromfolder("music")
            tmplist = []
            for musicitem in songlist:
                tmplist.append(musicitem["name"])
            response = ':'.join(tmplist)
        except IOError as e:
            print("IOError: " + str(e))
            response = "error " + e.message
    # OPTIONS for a list of options
    elif cmd == commands.OPTIONS:
        commandlist = []
        for command in vars(commands).itervalues():
            command = str(command)
            if command.isupper():
                commandlist.append(command)
        response = ','.join(commandlist)
    else:
        response = "INVALID_COMMAND"

    print("RESPONSE: " + response)

    return response + "\n"


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
            conn.send(response.encode())

        except socket.error as msg:
            print(colors.ENDC + "something went wrong: " + str(msg))
            conn = accept_connection()
        except Exception as msg:
            print(colors.ENDC + "Something went wrong " + str(msg))
            main()
    print("Connection closed, wait for connections again")
    conn = accept_connection()
    conversation(conn)


def main():
    create_server()
    conn = accept_connection()
    conversation(conn)


# Start main program
if __name__ == '__main__':
    # print(process_command("OPTIONS"))
    main()
