# Orchestrate 2.1
This branch contains only Python code, as all work currently done on the 2.1 iteration of Orchestrate is in python. Other content was removed for cleanliness. For deleted content, see other branches.
## Python
The Python subsection contains the server, server controller, and clients.
### Overview
The Server runs on port 22000. <br>
The Server control run on port 21999, and the server has a thread running there too. <br>
The Server control can send a variety of commands to the server, including START and END. <br>
Clients connect to server on port 22000, and get redirected to the next free port (22001). <br>
### Basic Structure
Server - (runs always) - directs client to proper port, sends out times to client. <br>
Server Control (run w/ server) - sends commands to server (END, PAUSE, etc...)  - can have multiple instances <br>
Client - (Each on a different port) - occasionally receives time data, re-sync - can have multiple instances <br>
Engine - (run w/ server) - takes information from Server and provides instructions for Client
Can Broadcast across a network (use client HOST = '10.236.42.120', server HOST = '')
### Roadmap
* Figure out communication issues between programs
* Continue to generalize what types of media can work with Orchestrate
* Test thoroughly & improve
