from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        if client_address[0] in banlist:
            client.close()
            broadcast(bytes("Banned IP %s attempted to join the chat." % client_address[0], "utf8"))
        else:
            client.send(bytes("Welcome to the LGS Y12 Computing chatroom! Please enter your name!", "utf8"))
            addresses[client] = client_address
            Thread(target=handle_client, args=(client,client_address)).start()

def handle_client(client, ip):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    clientip = ip[0]
    ipNameList[name] = clientip
    welcome = 'Welcome %s! If you ever want to quit, type !quit to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg == bytes("!quit", "utf8"):
            client.send(bytes("!quit", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break
        elif bytes("!kick", "utf8") in msg and (clientip in adminList):
            for mem in clients:
                iptuple = mem.getpeername()
                userip = iptuple[0]
                kickip = msg[6:].decode()
                if userip == kickip:
                    mem.close()
                    kickedname = clients[mem]
                    del clients[mem]
                    broadcast(bytes("%s has been kicked from the chat." % kickedname, "utf8"))
                    break
            else:
                print("IP NOT FOUND")
        elif msg == bytes("!iptables", "utf8"):
            for key in ipNameList:
                client.send(bytes("#: " + key + " || " + ipNameList[key], "utf8"))
                time.sleep(0.003)
        elif msg == bytes("!online", "utf8"):
            for key in ipNameList:
                client.send(bytes('#: ' + key, "utf8"))
                time.sleep(0.003)
        elif msg == bytes("!iplist", "utf8"):
            for key in ipNameList:
                client.send(bytes('#: ' + ipNameList[key], "utf8"))
                time.sleep(0.003)
        elif msg == bytes("!help", "utf8"):
            client.send(bytes("#: Commands:", "utf8"))
            time.sleep(0.003)
            client.send(bytes("#: !help - Bring up help dialog\n", "utf8"))
            time.sleep(0.003)
            client.send(bytes("#: !online - Print online players\n", "utf8"))
            time.sleep(0.003)
            client.send(bytes("#: !iplist - Print a list of IPs\n", "utf8"))
            time.sleep(0.003)
            client.send(bytes("#: !iptables - Print IP / Name table\n", "utf8"))
            time.sleep(0.003)
            client.send(bytes("#: !quit - Quit\n", "utf8"))
        else:
            broadcast(msg, name+": ")
            
def broadcast(msg, prefix=""):  # prefix is for name identification.

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)
    #iptuple = sock.getsockname()
    #print(iptuple[0])


        
clients = {}
addresses = {}

banlist = []
adminList = ['172.30.12.56', '172.30.12.87']

ipNameList = {}

flagvar = ""

#HOST = '172.30.12.30'
HOST = '172.30.12.56'
PORT = 7000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
