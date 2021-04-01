import socket
import time
import sys
import datetime
import os
import math
from threading import Thread

HOST = '127.0.0.1'  # default server on localhost
PORT = 22000  # server port
splitData = []

# if len(sys.argv) > 1:  # if any args (should I pass in HOST too?)
#    PORT = int(sys.argv[1])
# getting the HOST name; assume for now that PORT is the default
if len(sys.argv) > 1:
    HOST = sys.argv[1]
    print("HOST set to", HOST)

p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p.connect((HOST, PORT))
p.send(b'Client1')  # name of client here
PORT = int(p.recv(1024).decode("utf-8")) 
print("Connecting to Server at port", PORT, HOST)
p.close()
serverData = " "

state = -1 # Possible states: -1 for not started, 0 for pause, 1 for print
count = 0 # Determines what line of the hardcoded conversation is being printed

server_time = 0.0
END = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receiver():
    global server_time, END, state, s, needsResponse, serverData
    
    time.sleep(1) # TEMPORARY FIX for timing problem
    s.connect((HOST, PORT))

    while not END:
        serverData = s.recv(1024).decode("utf-8")
        print("Received: " + serverData)      
    
        if (serverData == "END"):
            print("Server ended; exiting")
            END = True
            break
        splitServerData = serverData.split()
        serverData = splitServerData[len(splitServerData) - 2] + " " + splitServerData[len(splitServerData) - 1]
        print("Adjusted: " + serverData) 
    s.close()


if __name__ == '__main__':
    receiver = Thread(target=receiver, args=())
    receiver.daemon = False
    receiver.start()

    f = open("../../point.txt", "r")
    point = f.read()
    f.close()
    time.sleep(2)
    
    while True:  # While loop for duration of session
        
        if END:
            break

        if os.path.isfile("../../point.txt"):
            f = open("../../point.txt", "r")
            newPoint = f.read()
            f.close()
            #os.remove("../../point.txt")

        if (point != newPoint):
            s.send(newPoint.encode('utf-8'))
            print(newPoint)

        point = newPoint

    receiver.join()
    print("Client Ended")