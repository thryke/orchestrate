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

# Test Engine to be used with Client1.py. Each line of conversation prints after the previous line automatically.

# if len(sys.argv) > 1:  # if any args (should I pass in HOST too?)
#    PORT = int(sys.argv[1])
# getting the HOST name; assume for now that PORT is the default
if len(sys.argv) > 1:
    HOST = sys.argv[1]
    print("HOST set to", HOST)

p = socket.socket()
p.connect((HOST, PORT))
p.send(b'Engine')  # name of client here
PORT = int(p.recv(1024).decode("utf-8")) 
print("Connecting to Server at port", PORT, HOST)
p.close()
data = ""
server_time = 0.0
END = False
s = socket.socket()


def receiver():
    global server_time, END, data, s
    
    time.sleep(2) # TEMPORARY FIX for timing problem
    s.connect((HOST, PORT))

    while END == False:
        data = s.recv(1024).decode("utf-8")
        if not data:
            data = ""
    s.close()


if __name__ == '__main__':
    receiver = Thread(target=receiver, args=())
    receiver.daemon = False
    receiver.start()

    start_server = True
    time1 = datetime.datetime.now()  # will get redefined on START
    
    oldSplitData = data.split()
    
    count = 0
    state = 0
    currState = 0
    oldState = 0
    print("State = 0")
    print ("Count = 0")
    
    oldServerInfo = ""
    serverInfo = str(state) + " " + str(count) + " "
    
    PAUSE = False
    RESTART = False
    RESUME = False
    FORWARD = False
    BACK = False
    while END == False:  # DO CLIENT THINGS HERE
        
        if data == "":
            # data = "default default123"        
            continue
            
        splitData = data.split()
    
        
        if oldSplitData == splitData:
            continue
        oldSplitData = splitData
        
        print(splitData)
            
        clientWord = splitData[len(splitData) - 1] 
           
      #  if splitData[0] == "Default":
       #     print("DEFAULT DETECTED")
        #    s.send(str(state).encode('utf-8'))
        #    continue
            
       
        if splitData[0] == "End":
            serverInfo = "end123"
            s.send(serverInfo.encode('utf-8'))
            END = True
            break
        elif splitData[0] == "Pause":
            PAUSE = True
            RESTART = False
            RESUME = False
        elif splitData[0] == "Start":
            PAUSE = False
            RESTART = True
            RESUME = False
        elif splitData[0] == "Restart":
            PAUSE = False
            RESTART = True
            RESUME = False
        elif splitData[0] == "Resume":
            PAUSE = False
            RESTART = False
            RESUME = True
        elif splitData[0] == "Back":
            state = currState
            BACK = True
            PAUSE = False
        elif splitData[0] == "Forward":
            state = currState
            FORWARD = True
            PAUSE = False
        
      
        
        
       # greeting = ["Hello,", "How're", "You?"]
       # response = ["Fine,", "Thanks.", "Yourself?"]
       # response2 = ["Very", "Well,", "Thanks."]
       # parting = ["So", "Long," "Then."]
        
  
        if PAUSE:
            state = 0
            serverInfo = str(state) + " " + str(count) + " "
            s.send(serverInfo.encode('utf-8'))
        if RESUME:
            state = 1
            serverInfo = str(state) + " " + str(count) + " "
            s.send(serverInfo.encode('utf-8'))
        if RESTART:
            state = 1
            count = 1
            serverInfo = str(state) + " " + str(count) + " "
            s.send(serverInfo.encode('utf-8'))
        if FORWARD:
            state = 1
            count += 1
            serverInfo = str(state) + " " + str(count) + " "
            s.send(serverInfo.encode('utf-8'))
        if BACK:
            if (count > 1):
                count -= 1
                state = 1
                serverInfo = str(state) + " " + str(count) + " "
                s.send(serverInfo.encode('utf-8'))
        else:
            if (splitData[1] == "You?") and (count == 1):
                state = 1
                count += 1
            elif (splitData[1] == "Yourself?") and (count == 2):
                state = 1
                count += 1
            elif (splitData[1] == "Thanks.") and (count == 3):
                state = 1
                count += 1
            elif (splitData[1] == "Then.") and (count == 4):
                state = 1
                count += 1
            serverInfo = str(state) + " " + str(count)
            s.send(serverInfo.encode('utf-8'))
             
        FORWARD = False
        BACK = False
        RESTART = False
        RESUME = False
            
        if (serverInfo != oldServerInfo):
            print("New server info: " + serverInfo)
            oldServerInfo = serverInfo
               
            

        # cls is Windows only
        # os.system('cls')

    receiver.join()
    print("Engine Ended")
