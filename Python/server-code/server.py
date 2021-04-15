# server (threaded for each client)
import socket
from threading import Thread
import time 
import sys

HOST = '127.0.0.1'  # default server on localhost
PORT = 22000  # port for server
speed = .1  # timer count speed
newPort = PORT + 1;

# Connections use TCP
# Server takes information from Server Controller and Client and sends it to Engine. Takes information from Engine and sends it to Client.

# if len(sys.argv) > 1:  # if any args (should I pass in HOST too?)
#    PORT = int(sys.argv[1])
# getting the HOST name; assume for now that PORT is the default
if len(sys.argv) > 1:
    HOST = sys.argv[1]
    print("HOST set to", HOST)
    # this doesn't necessarily make sense for the server

class endSignal(Exception):
    pass

# globals (should I remove these?) USE DICTIONARIES (atomic push/pop) to communicate between threads?

# Boolean signalling the end of the server
serverEnd = False

num_clients = 0
num_controls = 0
serverData = "0 0" # Data received from the Engine and sent to the Client
clientData = "default123" # Data received from the Client and sent to the Engine
controlData = "Pause " # Data received from the Server Controller and sent to the Engine
engineResponded = True

timer = time.clock() # Timer. Started in main, used to calculate time since system started
startTimer = False # Timer starts when this is set to true in Main

# Thread communicating with a Server Control instance. One thread/instance.
def control_thread(portNum):
    global serverEnd, count, num_clients, num_controls, controlData
    print("Connecting to Server Control...")
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_socket.bind((HOST, portNum))
    c_socket.listen(1)
    cont_conn, add = c_socket.accept()
    
    print("Connected to Server Control at address", add)

    try:
        while serverEnd == False:
            data = cont_conn.recv(1024).decode("utf-8")
            print("From Server Control:")
            print (data)
            if data == 'End':   #Exits all server controls and ends the server
                serverEnd = True
                controlData = "End "
                print("Command: End")
                raise endSignal
            elif data == 'Exit':  #Exits just this server control
                print("Server control at address ", add, "on port", portNum, "self-terminated")
                num_controls -= 1
                if num_controls == 0:
                    print("0 controls; terminating Orchestrate");
                    serverEnd = True
                    controlData = "End "
                    raise endSignal
                break
            else:
                controlData = data + " "
                print("Command: " + data)
           
    except endSignal:
        c_socket.close()        
    except ConnectionResetError:
        print("[control thread] server control closed unexpectedly")
        serverEnd = True

    c_socket.close()

count = 0.0

newPort = PORT + 1
clientList = []
controlList = []
timeList = []
engineList = []

# Thread that listens for new connections and assigns them to appropriate threads/ports
def get_clients():
    global serverEnd, newPort, clientList, controlList, num_clients, num_controls, num_engines
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # client connections
    client_socket.bind((HOST, PORT)) 
    client_socket.listen(1)
    
    while True:
        if serverEnd:
            break
        c_conn, addr = client_socket.accept()  # wait for client on the next port
        if serverEnd:
            break
        name = c_conn.recv(1024).decode("utf-8")
        c_conn.send(bytes(str(newPort), 'utf-8'))
        if name == 'Control': # Sets up new server controller instance
            print("[Get Clients] Connected to new server control at address", addr, "-> Sending to port", newPort)
            control = Thread(target=control_thread, args=[newPort])
            control.start()

            controlTimer = Thread(target=time_sender, args=[newPort])
            controlTimer.daemon = False
            controlTimer.start()
            
            newPort += 2 # 2 ports, 1 for control_thread and one for time_sender
            num_controls += 1
            time.sleep(1)
            
            controlList.append(control)
            timeList.append(controlTimer)
        
        elif name == 'Engine': # Sets up new engine instance
            print("[Get Clients] Connected to new engine at address", addr, "-> Sending to port", newPort)
            engine = Thread(target=engine_thread, args=[newPort, name])
            engine.start()

            engineList.append(engine)
            newPort += 1
            time.sleep(1)
          
        else: # Sets up client instance
            print("[Get Clients] Connected to", name, "at address", addr, "-> Sending to port", newPort)
            client = Thread(target=serve, args=(newPort, name))
            clientList.append(client)
            client.start()
            num_clients += 1
            newPort += 1
        
    client_socket.close()

# Thread that communicates with clients. One thread per client instance
def serve(portNum, c_name):
    global serverEnd, count, HOST, clientData, num_clients, state, engineResponded, serverData
    print("Connecting to Client...")
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_socket.bind((HOST, portNum))
    c_socket.listen(1)
    cont_conn, add = c_socket.accept()
    
    print("Connected to", c_name, "on port", portNum)
    
    oldSendData = ""
    
    try:
        while True:
            if serverEnd:
                break
            if engineResponded == False:
                continue
            sendData = serverData
            if (sendData != oldSendData): # Only sends data if new data to send
                oldSendData = sendData
                print("Sending -> " + sendData + " <- to client") # Shows what is being sent to client
                cont_conn.send(bytes(sendData,'utf-8')) # Sends data to client
            clientData = str(cont_conn.recv(1024).decode("utf-8")) # Wait for data from client
            print('clientData = ', clientData)
            serverData = clientData
            if not clientData:
                print("Nothing received from client")
            print("Received " + clientData + " from client")
            engineResponded = False
           
    except ConnectionResetError:
        print("[control thread] Client closed unexpectedly")
        serverEnd = True
    except endSignal:
        exitMessage = "END"
        print("Sending End signal to client")
        cont_conn.send(bytes(exitMessage,'utf-8'))

    c_socket.close()
           

# Thread that sends timing data to Server Controllers. 1 thread/controller instance
def time_sender(portNum):
    global count, num_clients, serverEnd, timer, startTimer
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, (portNum + 1))) 
    sock.listen(1)
    sconn, addr = sock.accept()

    try:
        while True:
            if serverEnd:
                control_data = "END"
                sconn.send(bytes(control_data, 'utf-8'))
                break
            if not startTimer:
                continue
            print("Time: " + str(time.time() - timer)) # calculates time
            control_data = str(time.time() - timer) + " " + str(num_clients) # calculates time to send to contoller
            sconn.send(bytes(control_data, 'utf-8'))  # send data to control # sends time to controller
            # print("sent to control:", control_data)
            time.sleep(3)  # so these don't go too fast
    except ConnectionResetError:
        print("[time_sender] server control closed unexpectedly")
        serverEnd = True
    except BrokenPipeError:
        print("[time_sender] server control closed")
    
    sock.close()

# Thread that communicates with Engine
def engine_thread(portNum, c_name):
    global serverEnd, count, HOST, clientData, num_clients, num_engines, controlData, state, engineResponded, serverData
    print("Connecting to Engine...")
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_socket.bind((HOST, portNum))
    c_socket.listen(1)
    cont_conn, add = c_socket.accept()
    state = 0
   
    print("Connected to", c_name, "on port", portNum)
 
    oldSendData = "" + ""
    
    try:
        while True:
            sendData = controlData + clientData # Combine data from globals for server controllers and clients 
            if (sendData != oldSendData): # Only send if there's some change
                oldSendData = sendData
                print("Sending -> " + sendData + " <- to engine")
                cont_conn.send(bytes(sendData,'utf-8'))
                controlData = "Default "
                engineData = cont_conn.recv(1024).decode("utf-8") # Wait for data from engine
                print("Received " + engineData + " from engine")
                engineResponded = True
                if (engineData == "end123 "): # Signal to end session
                    break
           
    except ConnectionResetError:
        print("[control thread] Engine closed unexpectedly")
        serverEnd = True

    c_socket.close()
    
if __name__ == '__main__':
    print("Sever. Enables communication between Engine, Contollers and Clients.")  

    print("Starting \"Get Clients\" thread (Ready to accept a new client)...")
    client_control = Thread(target=get_clients, args=())
    client_control.start()

    while True:  # Starts timer when at least one each of engine, server contoller and client have started
        if not startTimer and (len(engineList) != 0) and (len(controlList) != 0) and (len(clientList) != 0): 
            print("Starting timer")
            startTimer = True
            timer = time.time()
        if serverEnd:
            break

    # END SERVER
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # send a connection to the server to un-stick it
        s.connect((HOST, newPort))
        s.close()
        print("\"awaiting new client\" thread unstuck")
    except ConnectionRefusedError:
        print("newPort", newPort, "(\"awaiting new client\" thread connection) already closed")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # same for get_clients()
        s.connect((HOST, PORT))
        s.close()
        print("\"get clients\" thread unstuck")
    except ConnectionRefusedError:
        print("PORT", PORT, " (\"get clients\" thread connection) already closed")

    for c in clientList:
        c.join()
    print("Clients ended")
    for a in controlList:
        a.join()
    print("Controls ended")
    for t in timeList:
        t.join()
    for e in engineList:
        e.join()
    print("Engine ended")
    client_control.join()
    print("Server Controls Ended")
    print("Server Ended")
