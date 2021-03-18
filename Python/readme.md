Orchestrate 2.1 Code. Modified code is in the Python folder.
## server-code
Contians server.py. Must be run before other portions.
## initial-clients-code
Contains:
- serverControl.py, the server controller
- client1.py, the test client
- engine1.py - engine3.py, the test engines
## Other content
Other directories and files weren't updated with Orchestrate 2.1. They were removed from this branch as they are incompatible with Orchestrate 2.1. The content from the other directories and files can be found in other branches and adapted to the Orchestrate 2.1 system.
## Known Issue
The "End" command to terminate the session is a little inconsistent.
The biggest known issue is the communication protocol. Oftentimes, multiple messages will be returned from recv calls. This is likely due to the logic used to determine when to send and/or when to receive. The problem's been resolved for the included sample engines and clients but could cause problems for other engines and clients. The best solution I can think of would be a system of user-defined signals. Non-blocking recv loops would run constantly, and then if they receive anything, they would raise the signal and the program would know that there's new data to look at. Other solutions are welcome as well.
