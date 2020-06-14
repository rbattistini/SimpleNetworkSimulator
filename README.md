# A simple network simulation

This project was realized for the course *Programmazione di Reti* of the DISI at the University of Bologna in the AY 2019/2020.

The aim is to simulate a small SERVER-ROUTER-CLIENT architecture on the same 
node as shown here: 

<img src="/resources/simple_network_simulation.png" alt="A picture of the network" class="center">

## Features

### Requested Features

- A server must keep track of which clients enter and leave the network.

- When a client (active on the network) wants to send a message to another 
client, he will have to send the message to the server which will deliver the 
message to the recipient only if the recipient client is active, alternatively 
it will return a message to the sender indicating that the recipient client 
is not online.

- The IP and Ethernet headers must be considered in the simplified version, 
that is, composed only of the IP and Mac Address addresses.

### Additional features

- Specifications of the entities that made up the network are stored in a 
configuration file named "network.yml". A different number of 
clients, routers and servers could be created to simulate the network.

- The arp tables are dinamically created by the routers.

- Different termination conditions of the simulation are available.
    - fixed amount of time passed
    - completition of the clients' agenda
    - manual duration if the duration is set to infinite

## Run the simulation

First see if [requirements](#dependencies) are met.

Then on GNU/Linux^[1] and MacOS Catalina, chmod and launch on the terminal the script `main.py` with administrator privilegies. 

`sudo ./main.py`

On Windows 10 open a terminal and launch the script `main.py`.

`./main.py`

> **Note:** the simulation will automatically stop itself after one minute if no
command line arguments are given.

## Stop the simulation 

Just press <kbd>CTRL</kbd> + <kbd>C</kbd> on the terminal in which the main 
script was launched. This will send a SIGINT to all the members of the network 
launched by the main script.

Note that the simulation will stop automatically if one termination condition 
that was specified at the time the main script was launched is met.

## Requirements

Python interpreter 3.8.1 64-bit (On Windows)
Python interpreter 3.8.2 64-bit (On GNU/Linux)
Conda environment is optional.
Python 2.x is not supported.

[1]: tested on Ubuntu 20.04 Focal Fossa and Arch Linux.