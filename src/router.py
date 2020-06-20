#!/usr/bin/env python3
import socket
import time
import utilities as utils
import error_handling as check

# server_address = ("localhost", 8005)
# server_side -> gateway port
BUFFER_SIZE = 1024

# make_local_address per router

# all bound to the default gateway of their router
clients_list = [
    "92.10.10.15",
    "92.10.10.20",
    "92.10.10.25"
]

# code ARP request and response
arp_table_mac = {
    "92.10.10.15" : "32:04:0A:EF:19:CF",
    "92.10.10.20" : "10:AF:CB:EF:19:CF",
    "92.10.10.25" : "AF:04:67:EF:19:DA"
}

# code connections
arp_table_socket = {}

# missing arp_table_mac server-side

class RouterThread:
    def __init__(self, router_threads, clients_gateway_ip, arp_table_mac,
     router_data, router_id):
        self.router_clients, self.router_server = init(router_data)
        self.running = False
        self.arp_table_mac = arp_table_mac
        self.router_data = router_data
        self.router_id = router_id
    
    # TODO: ARP reply and request
    def listen_client_side(self):
        print("s")

    # TODO: how the router connects?
    def listen_client_connection(self):
        print("s")

    def stop_listening(self):
        self.running = False

    def go_online(self):
        server_address = self.router_data.get("gateway_port")

        connected = check.socket_connect(
            self.server_connection, 
            server_address,
            "Terminating thread"
        )

        return connected

    """
    Listens for packets received from the server and sends them to the clients 
    of his network.
    """
    # TODO: how routing happens?
    def forward_packets(self):
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

    def run_server_side(self):
        self.running = True

        # connect to server
        connected = self.go_online()
        if(connected is True):
            while self.running is True:
                self.forward_packets()

            self.router_server.close()

        # exit procedure
        utils.show_status(self.router_id,
                 "going offline")
        del self.router_threads[self]

def init(router_data):

    router_clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    router_clients.bind(router_data["client_side"]["router_address"])
    router_clients.listen(5)

    router_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    router_server.bind(router_data["server_side"]["router_address"])
    router_server.listen(5)

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
