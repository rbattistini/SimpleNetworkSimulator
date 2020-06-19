#!/usr/bin/env python3
import socket
import time
import utilities as utils

server_address = ("localhost", 8005)
BUFFER_SIZE = 1024

router_data = {
    "server_side" :
        { "router_ip" : "92.10.10.10",
        "router_mac" : "05:10:0A:CB:24:EF",
        "router_address" : ("localhost",8101)},
    "client_side" : 
        { "router_ip" : "92.10.10.30",
        "router_mac" : "05:10:0A:CB:54:EF",
        "router_address" : ("localhost",8201)}
}

# all bound to the default gateway of their router
clients_list = [
    "92.10.10.15",
    "92.10.10.20",
    "92.10.10.25"
]

arp_table_mac = {
    "92.10.10.15" : "32:04:0A:EF:19:CF",
    "92.10.10.20" : "10:AF:CB:EF:19:CF",
    "92.10.10.25" : "AF:04:67:EF:19:DA"
}

arp_table_socket = {}

class RouterThread:
    def __init__(self, router_data):
        self.router_clients, self.router_server = init(router_data)
        self.running = False
                
    def start_listening_server_side(self, router_data, server_ip, arp_table_mac):
        self.running = True

        # connect_to_server
        self.router_server.connect(router_data["server_address"])

        arp_table_generator()

        while self.running is True:
            forward_packets(self.router_server, self.client_data, router_data)

        close_server_connection()
    
    def listen_client_side(self):
        print("s")

    def listen_client_connection(self):
        print("s")

    def stop_listening_server_side(self):
        self.running_server_side = False


def init(router_data):

    router_clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    router_clients.bind(router_data["client_side"]["router_address"])
    router_clients.listen(5)

    router_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    router_server.bind(router_data["server_side"]["router_address"])
    # router_server.listen(5)

    return (router_clients, router_server)

def connect_to_clients(router_clients, router_server, clients_list, server_address):
    print("Waiting for clients...")
    arp_table_socket = {}

    while True:
        client_connection, address = router_clients.accept()
        if(client_connection != None):
            print("Connected with client: ", address)
            print(len(clients_list))
            arp_table_socket[clients_list.pop()] = client_connection
        if(len(clients_list) == 0):
            print("All connections established")
            break

    server = (server_address)
    router_server.connect(server) # router_server is bound to a port

    return arp_table_socket

"""
Listens for packets received from the server and sends them to the clients 
of his network.
"""
def forward_packets(router_server, arp_table, arp_table_socket, router_data):
    while True:

        received_message = router_server.recv(BUFFER_SIZE).decode("utf-8")   
        parsed_message = utils.read_packet(received_message)     
        utils.report(parsed_message)

        parsed_message.update(
            destination_mac=arp_table[
                parsed_message.get("destination_ip")
            ],
            source_mac=router_data["client_side"]["router_mac"]
        )

        destination_socket = arp_table_socket[
            parsed_message.get("destination_ip")
        ]

        packet = utils.modify_packet(parsed_message)
        destination_socket.send(bytes(packet, "utf-8"))
        time.sleep(2)

if __name__ == "__main__":
    router_clients, router_server = init(router_data)
    arp_table_socket = connect_to_clients(router_clients, router_server, clients_list, server_address)
    forward_packets(router_server, arp_table_mac, arp_table_socket, router_data)
    # mantieni attiva un'interfaccia verso il server
    # su richiesta attiva un'interfaccia verso il client