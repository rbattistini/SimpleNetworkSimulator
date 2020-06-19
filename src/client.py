"""
Code for a client that can be online and offline and can both send and receive
messages.
"""
from socket import AF_INET, socket, SOCK_STREAM
import time
import logics

BUFFER_SIZE = 1024

# HOW DOES THIS WORK??
# The client only knows the port on which the router is and the destination_ip!!
# It needs to know also the ip and mac address of the router to send messages???
"""
Client establishes a connection with its router. 

Now the client is online but it cannot receive nor send messages.

- address of the router, is given by the test class and extracted from 
the config file. 
"""
def initialize(address):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(1)
    # waits to be captured by an accept in the router
    # the router MUST be started first!!!
    client.connect(address)
    return client

"""
Client is able to receive and send data on the network.

It periodically does so until it has tried to contact all the clients on his
agenda.

- client is given from the configuration run.
- client_data from the config file.
"""
def run(client, client_data):
    # this loop is infinite because the client should always check if there are
    # incoming messages and should always be able to send messages while online.
    while True:
        # SEND
        logics.send_message()

        time.sleep(3)

        # HOW DOES THIS WORK??
        # RECEIVE (it must wait for the router to be ready) 
        # simply display the message received and checks if it was correctly
        # routed. NO registration in a list.
        received_message = logics.rcv_msg(client, BUFFER_SIZE)
        
        if(received_message is not None):
            # ANALYZE
            decoded_message = received_message.decode("utf-8")
            message = logics.read_packet(decoded_message)

            # DISPLAY
            if(logics.integrity_check(client_data)):
                logics.report(message)
            
        time.sleep(3)
