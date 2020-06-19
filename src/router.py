"""
Code for a router with a pre-created arp table. (Level 3 IP-ARP)
"""
from socket import AF_INET, socket, SOCK_STREAM
import time
import logics

BUFFER_SIZE = 1024

"""
Router binds itself to two channels, entering and exiting.

Now the router is NOT online, it cannot forward messages.

- router_data, router_port for each direction
- backlog queue dimension
"""
def init(router_data):

    """ 
    Creates a socket INET (IPv4 protocol) of type STREAM to connect with 
    clients.
    """

    # CREATE
    router_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # BIND
    logics.bind_socket(router_receive,
        ("localhost", router_data["router_receive_port"]))

    # SET BACKLOG QUEUE
    router_receive.listen(5)

    """
    Creates a socket INET (IPv4 protocol) of type STREAM to connect with the 
    server and the other router.
    """

    # CREATE
    router_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # BIND
    logics.bind_socket(router_send,
        ("localhost", router_data["router_send_port"]))

    # SET BACKLOG QUEUE
    router_send.listen(5)

    return (router_send, router_receive)

"""
Creates an arp table from a dictionary of clients connected to the router's 
network.

This step in necessary to allow the router to correctly forward messages.
If an arp table is not created the router cannot do anything with the messages
it receives.

- clients_data from the config file
"""
def init_arp_table(clients_data):

    arp_table = {}

    for client in clients_data:
        arp_table[str(client)]["ip_address"] = clients_data[str(client)]["mac_address"]

"""
Now the router can forward messages.

- router_data, from the config file, all which was not used previously
- router, created during the configuration run
- arp_table, created during the second configuration run
- address, of the server to be connected to
"""
def run(router_send, router_data, arp_table, address):
    while (client1 == None or 
        client2 == None or 
        client3 == None):

        # listen for new connections and return the associated socket object
        client, address = router_send.accept()
        print("Connection established")
        # it is in the arp table?
        # who is online?

        if(client1 == None):
            client1 = client
            print("Client 1 is online")
        
        elif(client2 == None):
            client2 = client
            print("Client 2 is online")
        else:
            client3 = client
            print("Client 3 is online")

    router_send.connect(address) 

    while True:
        try:
            # it must wait for one of the clients to connect and send a message
            received_message = router_send.recv(BUFFER_SIZE).decode("utf-8")
        # if an error occurs probably is due to the router abandoning the 
        # network
        except OSError:
            break
        
        # as soon the message is received is printed and routed to the server
        message = logics.read_packet(received_message)
        logics.report(message, false)
        logics.assemble_packet(message)

        ethernet_header = router_mac + arp_table_mac[destination_ip]    
        IP_header = source_ip + destination_ip    
        packet = ethernet_header + IP_header + message


        destination_socket = arp_table_socket[destination_ip]
        
        # it must wait for the server to receive the routed message
        # sends an utf-8 encoded byte stream to the destination socket
        destination_socket.send(bytes(packet, "utf-8"))
        time.sleep(2)

"""
Listens for incoming packets from clients and forwards them to the server after 
dissecting them and changing ONLY the destination MAC address.

Listens for incoming packets from the server and forwards them to the client
after dissecting them and changing ONLY the destination MAC address.
"""
def listen_packets():
    print("forwading incoming packets")