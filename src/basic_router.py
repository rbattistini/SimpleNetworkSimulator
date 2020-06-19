"""
Code for a router with a void arp table.
"""
from socket import AF_INET, socket, SOCK_STREAM
import time
import logics

BUFFER_SIZE = 1024
BROADCAST_MAC = "FF:FF:FF:FF:FF:FF"

arp_table = {}
arp_table_socket = {}

"""
Router binds itself to two interfaces, entering and exiting.

Now the router is NOT online, it cannot forward messages.

Parameters:
- router_data, router_port for each direction
- backlog queue dimension

Return value:
- a tuple, (router_send, router_receive) with the two interfaces associated
with the socket.
"""
def init(router_data):

    # CREATE
    router_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # BIND
    logics.bind_socket(router_client,
        ("localhost", router_data["router_receive_port"]))

    # SET BACKLOG QUEUE
    router_client.listen(5)

    # CREATE
    router_server= socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # BIND
    logics.bind_socket(router_server,
        ("localhost", router_data["router_send_port"]))

    # SET BACKLOG QUEUE
    router_server.listen(5)

    return (router_client, router_server)

"""
The router makes all needed connections on the specified interface.
Why is needed to know all possible connectors? Because the router can't
search always for new connections, it does one thing at a time.

The router waits till all the entities on the specified interface make
a connection.
What happens if a client goes offline and closes the connection?
"""
def client_connection(router_socket, connectors_list):
    print("Waiting for  clients...")
    client_connections = {}
    counter = len(connectors_list)

    while True:
        # listen for new connections and return the associated socket object
        client_connection, address = router_socket.accept()
        print("Connection established")

        if(client_connection != None):
            print("Connected with client: ", address)
            client_connections.add(client_connection)
            counter -= 1

        if(counter == 0):
            print("All connections established")
            break

    # router_socket.connect(address) 
    return client_connections

def listen_packets(router_send, router_receive, router_data):
    
    while True:
        try:
            # BLOCKING 
            # it must wait for one of the clients to connect and send a message
            received_message = router_receive.recv(BUFFER_SIZE).decode("utf-8")
        # if an error occurs probably is due to the router abandoning the 
        # network (does this happen?)
        except OSError:
            break

        waiting_for_ARP_reply = False
        # A message has been received.
        parsed_message = logics.read_packet(received_message)
        
        # Is the message received an ARP request and the message to be sent 
        # an ARP reply?
        # YES, prepare an ARP reply and send to the client connected with 
        # the source_ip
        # source_ip (-> port )-> socket
        if(parsed_message.get("destination_mac") == BROADCAST_MAC):

            parsed_message.update(
                destination_mac=parsed_message.get("source_mac"),
                source_mac=router_data.get("mac_address")
            )

            destination_socket = arp_table_socket[
                parsed_message.get("source_ip")
            ]

        # NO
        # Is the message received an ARP reply?
        # If the mac address is not associated with an ip AND
        # the ip address of the source is paired with the missing mac address
        # create a new entry in the arp_table (source_ip, source_mac)

            waiting_for_ARP_reply = False
        # NO
        # Should an ARP request be sent?
        # YES, prepare an ARP request and send to the client connected with 
        # the source_ip
        # source_ip (-> port) -> socket
        elif(arp_table[parsed_message.get("destination_ip")] is None):

            parsed_message.update(
                destination_mac=BROADCAST_MAC,
                source_mac=router_data.get("mac_address")
            )
            destination_socket = arp_table_socket[
                parsed_message.get("source_ip")
            ]

            waiting_for_ARP_reply = True

        # NO, forward the packet changing only level 2 to the client
        # connected with the destination_ip
        # destination_ip -> port -> socket
        else:
            parsed_message.update(
                destination_mac=arp_table[
                    parsed_message.get("destination_ip")
                ],
                source_mac=router_data.get("mac_address")
            )

            destination_socket = arp_table_socket[
                parsed_message.get("destination_ip")
            ]
            
        # prepare and send the packet
        packet = logics.write_packet(parsed_message) # prepare the packet
        # sends an utf-8 encoded byte stream to the destination socket
        destination_socket.send(bytes(packet, "utf-8"))
        # it must wait for the client to receive the routed message
        time.sleep(2)
