import socket
import time
import sys
import datetime
import os
import math
from threading import Thread
import requests
import webbrowser

HOST = '127.0.0.1'  # default server on localhost
PORT = 22000  # server port

# if len(sys.argv) > 1:  # if any args (should I pass in HOST too?)
#    PORT = int(sys.argv[1])
# getting the HOST name; assume for now that PORT is the default
if len(sys.argv) > 1:
    HOST = sys.argv[1]
    print("HOST set to", HOST)

p = socket.socket()
p.connect((HOST, PORT))
p.send(b'Client 2')  # name of client here
PORT = int(p.recv(1024).decode("utf-8"))  # should be 22001 for client 1
print("Connecting to Server at port", PORT, HOST)
p.close()

server_time = 0.0
END = False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverData = ""

def receiver():
    global server_time, END
    s = socket.socket()
    time.sleep(2) # TEMPORARY FIX for timing problem
    s.connect((HOST, PORT))

    while not END:
        serverData = s.recv(1024).decode("utf-8")
        print("Received: " + serverData)      
    
        if (serverData == "END"):
            print("Server ended; exiting")
            END = True
            break
        #splitServerData = serverData.split()
        #serverData = splitServerData[len(splitServerData) - 2] + " " + splitServerData[len(splitServerData) - 1]
        #print("Adjusted: " + serverData) 

    s.close()


if __name__ == '__main__':
    receiver = Thread(target=receiver, args=())
    receiver.daemon = False
    receiver.start()

    sendWord = "default123" # Default value when actual media isn't being printed
    time.sleep(2)
    
    while True:  # While loop for duration of session
        
        if END:
            break

    s.send(sendWord.encode('utf-8'))

    receiver.join()
    print("Client Ended")