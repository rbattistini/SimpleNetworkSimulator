"""
Code for a server that monitors online and offline clients.

Note that it does NOT send messages to other clients.

This server belongs to the network spanned by an arbitrary number of routers.
"""
from socket import AF_INET, socket, SOCK_STREAM
import sys
import logics

"""
Server binds itself to a port using a TCP socket. 
(Why TCP and not UDP? more stable, performant connection)

Now the server is NOT online, it is not ready to receive nor send messages.

- address, (host, port)
- backlog queue dimension
"""
def init(address): 
    """
    Creates a socket INET (IPv4 protocol) of type STREAM to connect with the 
    server and the other router.
    """

    # CREATE
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # BIND
    logics.bind_socket(address)

    # BACKLOG
    server.listen(2)
    return server

"""
Runs the server.

It listens for any packets sent by its routers and forwards them.

- server, socket given by the configuration run
- server_data, given from the config file
"""
def launch(server, server_data, routers_list):
    print ('the web server is up on port:', server_data.get("server_port"))
    print ('Ready to serve...')
    connect_to_routers(server, routers_list)
    listen_packets(server_data)

"""
Waits until has established a connection with all the routers it should be
connected, as stated in routers_list.

It should be called BEFORE listen_packets.

WARNING: It cannot distinguish among different routers, it only employs the 
lenght of the list given.

Returns a list of all the routers connection established.
"""
def connect_to_routers(server, routers_list):
    print("Waiting for  routers...")
    router_connections = {}
    counter = len(routers_list)

    while True:
        routerConnection, address = server.accept()
        if(routerConnection != None):
            print("Connected with router: ", address)
            router_connections.add(routerConnection)
            counter -= 1
        if(counter is 0):
            print("All connections established")
            break

    return router_connections

"""
Listens for incoming packets and resends them to the correct destination after
dissecting them and changing ONLY the destination MAC address.

It should be called AFTER connect_to_routers.

- server_data, 
- router_connections,  
"""
def listen_packets(server_data, router_connections):
    while True:
        
        # Tiene traccia dei client online e offline: REGISTRAZIONE CLIENT
        # popolata per la prima volta mano a mano che i client si connettono
        # per la prima volta, dictionary id-bool
        online_clients = {}

        # dictonary id-ip address ausiliario, di modo che i client possano avere
        # un nome
        clients_table = {}
        
        packet_data = {}
        packet = logics.write_packet(packet_data)

        source_ip = server_ip
        IP_header = IP_header + source_ip + destination_ip
        source_mac = server_mac
        destination_mac = router_mac         
        ethernet_header = ethernet_header + source_mac + destination_mac
        packet = ethernet_header + IP_header + message
        
        forward_message(router_connections, packet)  


"""
A server knows who are his routers but knows also all the clients each router
can forward messages to? 

Or it can know if the message should be forwarded to a client of the network or
to a client of another network? Should the router tell this to the server?

In other words when a server forwards a message received from a router should 
send it to ALL its linked routers? Then each router checks if there is a client
in its network that matches the destination ip and forwards the message to it?

Sends a packet to all the routers or to only one router? Which one? 

Used when a message should be sent:
- from a client to a router, (the client only knows one router)
- from a router to a server, (the router only knows one server)
- from a server to a router. (the server knows multiple routers)

- destination_socket, where the packet should be sent
- packet, the correctly formatted message
""" 
def forward_message(destination_socket, packet):
    destination_socket.send(bytes(packet, "utf-8"))