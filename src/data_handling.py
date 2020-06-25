#!/usr/bin/env python3
import sys
import yaml
import pprint

default_error_message = "\nFile loading failed:"

def load_network():
    network_data = {}
    try:
        with open('../resources/network_basic.yml', "r") as file:
            # logging.info("file loaded successfully")
            cfg = yaml.safe_load(file)
            servers_data = cfg["servers"]
            routers_data = cfg["routers"]
            clients_data = cfg["clients"]
    except yaml.YAMLError as msg:
        print(default_error_message, msg)
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

def router_arp_table_generator(servers_data, router_data):
    arp_table_mac = {}
    server_ip = router_data["server_side"]["server_ip"]
    for server, server_data in servers_data.items():
        if str(server_ip) == server_data["ip_address"]:
            arp_table_mac[
                server_data["ip_address"]
            ] = server_data["mac_address"]

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
    # gateway_ip = router_data["client_side"]["ip_address"]
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
        # pp.pprint(network_connections)
        # print(router_data["server_side"]["port"])
        # print(router_data["server_side"]["ip_address"])
        if(gateway_ip in network_connections.keys()):
            routers_gateway_ip[
                router_data["server_side"]["port"]
            ] = router_data["server_side"]["ip_address"]

    return routers_gateway_ip

"""
Routing tables generation. Dynamic routing protocols are not used.
"""
def ask_routing_table(router_id, network_data, routing_table):
    # for each router in network_connections
    # create the associated clients_gateway_ip
    # as key the ip addresses of the clients
    # as value the ip address of the router

    # if nesting level is more than 1?
    # recursion
    # each router ask other router connected
    # each router replies with its routing table

    # see who will connect with you
    # for each ask him his routing table
    # return your clients list

    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]
    this_router_data = routers_data[router_id]
    ip_address = routers_data[router_id]["server_side"]["ip_address"]  

    clients = clients_ip_port_generator(
                clients_data, this_router_data).values()       
    clients_ip = {}

    for client in clients:
        clients_ip[client] = ip_address
    
    # print(ip_address)
    for router, router_data in routers_data.items():
        # print(router_id, router)
        if(router != router_id):
            network_connections = router_data["network_connections"]
           
            # pp.pprint(network_connections.keys())
            if(ip_address in network_connections.keys()):
                routing_table.update(clients_ip)
                ask_routing_table(router, network_data, routing_table)
    
    # routing_table.update(clients_ip)
    return routing_table
                
pp = pprint.PrettyPrinter(indent=4)
routing_table = {}
network_data = load_network()
pp.pprint(ask_routing_table("router1", network_data, routing_table))
# pp.pprint(network_data)
routers_data = network_data["routers_data"]
router_data = routers_data["router1"]
clients_data = network_data["clients_data"]

server_data = network_data["servers_data"]
server_ip = router_data["server_side"]["server_ip"]
"""string = " ".join(["ciao", "come", "va?"])
list = string.split()
pp.pprint(list)"""

# pp.pprint(server_ip)
# pp.pprint(router_arp_table_generator(server_data, router_data))
# pp.pprint(server_arp_table_generator("195.1.10.1", routers_data))
# pp.pprint(client_arp_table_generator("92.10.10.1", routers_data))
# pp.pprint(load_client_ids(clients_data))
# pp.pprint(routers_ip_port_generator(routers_data, "195.1.10.1"))
# pp.pprint(routers_list_generator(routers_data, "195.1.10.1"))

"""
Router1
routing_table = {
    "1.5.10.15"" : "195.1.10.2",
    "1.5.10.20"" : "195.1.10.2",
    "1.5.10.25"" : "195.1.10.2"
}
Router2
routing_table = {
    "92.10.10.15" : "195.1.10.1",
    "92.10.10.20" : "195.1.10.1",
    "92.10.10.25" : "195.1.10.1",
    "195.1.10.10" : "195.1.10.1"
}

"""