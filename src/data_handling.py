#!/usr/bin/env python3
import sys
import yaml
import pprint
import utilities as utils

default_error_message = "\nFile loading failed:"

def load_network(path):
    network_data = {}
    try:
        with open(path, "r") as file:
            cfg = yaml.safe_load(file)
            servers_data = cfg["servers"]
            routers_data = cfg["routers"]
            clients_data = cfg["clients"]
    except yaml.YAMLError as err_msg:
        msg = " ".join(["error loading network configuration file", \
            str(err_msg)])
        utils.show_status("main", msg)
        sys.exit()

    # pack dictionaries
    network_data["servers_data"] = servers_data
    network_data["routers_data"] = routers_data
    network_data["clients_data"] = clients_data

    return network_data
    
def load_client_ids(clients_data):
    client_ids = []
    for client_id in clients_data.keys():
        client_ids.append(client_id)
    return client_ids

def load_text(path):
    try:
        with open(path,"r") as file:
            print(file.read())
    except IOError as msg:
        print(default_error_message, msg)
        sys.exit()

"""
Executes a set of functions to generate an ARP table for each client and server 
of the network.
 
The generation of the ARP tables (only arp_table_mac) happens in this way:

- each router searches in the list of the servers the one which has, as

- each client searches in the list of the routers the one which has, as one of
its gateways, the default gateway of the client. When such a router is found,
the client takes both the ip address and the mac address of the router and
creates its arp table.

- the server searches in the list of the routers the one which has, as one of
its gateways, the default gateway of the server. When such a router is found,
the server takes both the ip address and the mac address of the router and
creates its arp table.

"""

def router_arp_table_generator(router_id, servers_data, routers_data):
    arp_table_mac = {}
    router_data = routers_data[router_id]
    my_ip_address = router_data["server_side"]["ip_address"]
    my_network_connections = router_data["network_connections"]
    server_ip = router_data["server_side"]["server_ip"]
    for server, server_data in servers_data.items():
        if server_ip == server_data["ip_address"]:
            arp_table_mac[
                server_data["ip_address"]
            ] = server_data["mac_address"]

    for router, router_data in routers_data.items():
        ip_address = router_data["server_side"]["ip_address"]
        network_connections = router_data["network_connections"]
        if(my_ip_address in network_connections or ip_address in my_network_connections):
            arp_table_mac[
                ip_address
            ] = router_data["server_side"]["mac_address"]

    return arp_table_mac

def client_arp_table_generator(gateway_ip, routers_data):
    arp_table_mac = {}
    for router, router_data in routers_data.items():
        if router_data["client_side"]["ip_address"] == gateway_ip:
            arp_table_mac[
                router_data["client_side"]["ip_address"]
            ] = router_data["client_side"]["mac_address"]

    return arp_table_mac

def server_arp_table_generator(gateway_ip, routers_data):
    arp_table_mac = {}
    
    for router, router_data in routers_data.items():
        if router_data["server_side"]["ip_address"] == gateway_ip:
            
            arp_table_mac[
                router_data["server_side"]["ip_address"]
            ] = router_data["server_side"]["mac_address"]

    return arp_table_mac

"""
A dictionary of associations between a port and the ip of a client.
Used to identify clients in the network (this is needed only because
clients are all on localhost)
"""
def clients_ip_port_generator(clients_data, gateway_ip):
    clients_gateway_ip = {}
    for client, client_data in clients_data.items():
        default_gateway = client_data["gateway_ip"]
        if(gateway_ip == default_gateway):
            clients_gateway_ip[
                client_data["port"]
            ] = client_data["ip_address"]

    return clients_gateway_ip

def routers_ip_port_generator(routers_data, gateway_ip):
    routers_gateway_ip = {}
    for router, router_data in routers_data.items():
        network_connections = router_data["network_connections"]
        if(gateway_ip in network_connections.keys()):
            routers_gateway_ip[
                router_data["server_side"]["port"]
            ] = router_data["server_side"]["ip_address"]

    return routers_gateway_ip

"""
Routing tables generation. Dynamic routing protocols are not used.
"""
def ask_routing_table(router_id, network_data, routing_table):

    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]
    this_router_data = routers_data[router_id]
    my_ip_address = routers_data[router_id]["server_side"]["ip_address"] 
    my_network_connections = this_router_data["network_connections"] 
    server_ip = this_router_data["server_side"]["server_ip"]

    # Query other routers in the network
    for router, router_data in routers_data.items():
        if(router != router_id):
            network_connections = router_data["network_connections"]
            ip_address = router_data["server_side"]["ip_address"]  

            # If this router will connect with you ask him the list of
            # hosts he can reach and update the routing table accordingly
            # OR
            # If you will connect with this router ask him the list of
            # hosts he can reach and update the routing table accordingly
            if(my_ip_address in network_connections or str(ip_address) in my_network_connections):
                ip_client_side = router_data["client_side"]["ip_address"]  
                address_book = create_address_book(
                    ip_client_side,
                    ip_address,
                    clients_data
                )
                routing_table.update(address_book)

                # tells the auxiliary router how to reach the server
                if(server_ip in network_connections):
                    routing_table.update(((server_ip, ip_address), ))
            
    return routing_table

def create_address_book(ip_client_side, ip_server_side, clients_data):

    # Which clients can this router reach?
    clients = clients_ip_port_generator(clients_data, ip_client_side).values()
    # pp.pprint(clients)     
    address_book = {} # Client_ip_address -> Router_ip_address
    for client in clients:
        address_book[client] = ip_server_side

    return address_book

if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    routing_table = {}
    routings_table = {}
    network_data = load_network("../resources/network.yml")
    servers_data = network_data["servers_data"]
    routers_data = network_data["routers_data"]
    router_data = routers_data["router1"]
    clients_data = network_data["clients_data"]
    # pp.pprint(router_arp_table_generator("router1", servers_data, routers_data))
    server_data = network_data["servers_data"]
    server_ip = router_data["server_side"]["server_ip"]
    # print(ask_routing_table("router1", network_data, routing_table))
    # pp.pprint(ask_routing_table("router1", network_data, routing_table))
    # pp.pprint(ask_routing_table("router2", network_data, routings_table))
    # pp.pprint(clients_ip_port_generator(clients_data, "1.5.10.1"))
    """string = " ".join(["ciao", "come", "va?"])
    list = string.split()
    pp.pprint(list)"""


# pp.pprint(ask_routing_table("router2", network_data, routing_table))
# pp.pprint(network_data)
# pp.pprint(server_ip)
# pp.pprint(router_arp_table_generator(server_data, router_data))
# pp.pprint(server_arp_table_generator("195.1.10.1", routers_data))
# pp.pprint(client_arp_table_generator("92.10.10.1", routers_data))
# pp.pprint(load_client_ids(clients_data))
# pp.pprint(routers_ip_port_generator(routers_data, "195.1.10.1"))
# pp.pprint(routers_list_generator(routers_data, "195.1.10.1"))
