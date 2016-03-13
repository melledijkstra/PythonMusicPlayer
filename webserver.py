import socket

HOST, PORT = '', 1010

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("Serving socket on port "+str(PORT))

# After every request the loop will go again
while True:
    # waiting till connection is made
    conn, addr = server.accept()
    # get 1024 bytes from the connector
    request = conn.recv(1024)
    # print address from connector (print localy)
    print("Connection from: "+str(addr[0]))
    # send a message to connector
    conn.send("Successfully connected")

    # close connection
    conn.close()


print("This will only run when server is closed")
