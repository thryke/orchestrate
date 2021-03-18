import socket
import time
import sys
import datetime
import os
import math
import signal
from threading import Thread
import select

HOST = '127.0.0.1'  # default server on localhost
PORT = 22000
timer = "0"
num_clients = "0"
newPort = PORT
endControl = False

# Server Control. Takes in user input and sends it to Server.

# if len(sys.argv) > 1:  # if any args (should I pass in HOST too?)
#    PORT = int(sys.argv[1])
# getting the HOST name; assume for now that PORT is the default
if len(sys.argv) > 1:
    HOST = sys.argv[1]
    print("HOST set to", HOST)

def time_receiver():  # Receives timing data from server
    global timer, num_clients, newPort, endControl
   
    socket1 = socket.socket()
    #time.sleep(1)
    socket1.connect((HOST, (newPort + 1)))

    while True:
        if endControl:
            break
        server_data = socket1.recv(1024).decode("utf-8")
        if not server_data:
            print("Server control stopped receiving server data")
            break
        elif server_data == "END":
            print("Server terminated")
            endControl = True
            break
        else:
            temp_data = server_data.split()
            timer = temp_data[0]
            num_clients = temp_data[1]
            # print("[server time: " + timer + "] [# of clients: " + num_clients + "]")
            # time.sleep(3)  # to stay with server

    socket1.close()
    


print("Server Control. sends commands to the Server")
# These should be defined by designer of engine/client/controller; should be only part of Server Controller that needs modification
print("Commands: \"Start\", \"Restart\", \"Resume\", \"Pause\", \"Forward\", \"Back\", \"SET TIME int\", \"Exit\", and \"End\"")

p = socket.socket()
p.connect((HOST, PORT))
p.send(b'Control')
newPort = int(p.recv(1024).decode("utf-8"))
p.close()

time.sleep(1)
s = socket.socket()
s.connect((HOST, newPort))

get_server_data = Thread(target=time_receiver, args=())
get_server_data.daemon = False
get_server_data.start()

while True:
    if endControl:
        s.send(bytes("END", 'utf-8'))
        break
    # Display server information and prompt user for command
    print ("[server time: " + timer + "] [# of clients: " + num_clients + "] Enter Server command:")
    while not endControl:
        # Take in input command
        inputCommand, o, e = select.select( [sys.stdin], [], [], .1 )
        if inputCommand:
            clientData = sys.stdin.readline().strip()
            print('Sending command:', clientData, 'to Server')
            # Send command to server
            s.send(bytes(clientData, 'utf-8'))
            if clientData == "Exit":
                break
            break
        


get_server_data.join()
s.close()

print('Server Control Ended')
