#!/usr/bin/env python3
import socket
import utilities as utils

BUFFER_SIZE = 1024

server_data = {
    "server_ip" : "92.10.10.05",
    "server_mac" : "00:00:0A:BB:28:FC",
    "server_address" : ("localhost", 8005)
}

# primer for creating arp_table_socket
routers_list = [
    "92.10.10.10"
]

# not like an ARP table, used to handle multiple networks
network_table = {
    "92.10.10.15" : "92.10.10.10",
    "92.10.10.20" : "92.10.10.10",
    "92.10.10.25" : "92.10.10.10"
}

arp_table_mac = {
    "92.10.10.10" : "05:10:0A:CB:24:EF"
}

def init(server_data):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_data.get("server_address"))
    server.listen(2)
    return server

def listen_packets(server_connection, server_data, arp_table_socket):
    online_clients = {} # IP address - boolean

    while True:
        received_message = server_connection.recv(BUFFER_SIZE).decode("utf-8")   
        parsed_message = utils.read_packet(received_message)     

        if(parsed_message.get("message") == "{going offline}"):
            online_clients[parsed_message.get("source_ip")] = False
        elif(parsed_message.get("message") == "{going online}"):
            online_clients[parsed_message.get("source_ip")] = True
        else:
            if(online_clients[parsed_message.get("destination_ip")] is False or online_clients[parsed_message.get("destination_ip")] is None):
                message = "Client" + parsed_message.get("destination_ip") + "is not online: resending message back"
                packet = write_packet(
                    server_data.get("server_ip"),
                    parsed_message.get("source_ip"),
                    server_data.get("server_mac"),
                    arp_table_mac[
                        network_table[parsed_message.get("source_ip")]
                    ],
                    message
                )
                destination_socket =  arp_table_socket[
                    network_table[parsed_message.get("source_ip")]
                ]
            else:
                message = "Client" + parsed_message.get("destination_ip") + "is online: forwading message"
                packet = write_packet(
                    parsed_message.get("source_ip"),
                    parsed_message.get("destination_ip"),
                    server_data.get("server_mac"),
                    arp_table_mac[
                        network_table[parsed_message.get("destination_ip")]
                    ],
                    parsed_message.get("message")
                )
                destination_socket =  arp_table_socket[
                    network_table[parsed_message.get("destination_ip")]
                ]

        print("Message received from: "+ parsed_message.get("source_ip"))
        print(message)
        destination_socket.send(bytes(packet, "utf-8")) 

def connect_to_routers(server, routers_list):
    print("Waiting for routers...")
    arp_table_socket = {}

    while True:
        router_connection, address = server.accept()
        if(router_connection != None):
            print("Connected with client: ", address)
            print(len(routers_list))
            arp_table_socket[routers_list.pop()] = router_connection
        if(len(routers_list) == 0):
            print("All connections established")
            break

    return arp_table_socket

if __name__ == "__main__":
    server = init(server_data)
    arp_table_socket = connect_to_routers(server, routers_list)
    # send_packets(server_data, network_table, arp_table_mac, arp_table_socket)
    listen_packets(server, server_data, arp_table_socket)
    # mantieni un'interfaccia verso le reti attiva dopo aver stabilito le connessioni
    # smista i messaggi
