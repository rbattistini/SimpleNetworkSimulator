#!/usr/bin/env python3
import sys
import yaml
import pprint

# translate the number in a string, a list of strings
client_ids = []

default_error_message = "\nFile loading failed:"

def load_network():
    network_data = {}
    try:
        with open('../resources/network.yml', "r") as file:
            # logging.info("file loaded successfully")
            cfg = yaml.safe_load(file)
            server_data = cfg["servers"]
            routers_data = cfg["routers"]
            clients_data = cfg["clients"]
    except yaml.YAMLError as msg:
        print(default_error_message, msg)
        sys.exit()

    # pack dictionaries
    network_data["servers_data"] = server_data
    network_data["routers_data"] = routers_data
    network_data["clients_data"] = clients_data

    # complement_data()
    return network_data
    
def complement_data():
    generate_arp_tables()
    # make_local_addresses()
    clients_data = make_local_addresses(clients_data, "router_port", "router_address")
    load_client_ids()

def load_client_ids():
    for client_id in clients_data.keys():
        global client_ids
        client_ids.append(client_id)

def load_text(path):
    try:
        with open(path,"r") as file:
            print(file.read())
    except IOError as msg:
        print(default_error_message, msg)
        sys.exit()

"""
Executes a set of functions to generate an ARP table for each client and server of the network.
 
The generation of the ARP tables (only arp_table_mac) happens in this way:

- each client searches in the list of the routers the one which has, as one of
its gateways, the default gateway of the client. When such a router is found,
the client takes both the ip address and the mac address of the router and
creates its arp table.

- the server searches in the list of the routers the one which has, as one of
its gateways, the default gateway of the server. When such a router is found,
the server takes both the ip address and the mac address of the router and
creates its arp table.

"""

def routers_list_generator(routers_data):
    routers_gateway_ip = {}
    for router, router_data in routers_data.items():
        routers_gateway_ip[
            router_data["server_side"]["default_gateway"]
        ] = router_data["server_side"]["ip_address"]

    return routers_gateway_ip

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
Composes local addresses for each entity of the network from the ports given 
in the configuration file:

port -> ("localhost", port)

This way no use of tags like !!python/tuple is needed an safe load can be used.
"""
def make_local_addresses(dict, port_number, address_name):
    for client_id, client_data in dict.items():
        new_client_data = make__local_address(client_data, port_number, address_name)
        del client_data
        dict[client_id] = new_client_data
    return dict

def make__local_address(dict, port_number, address_name):
    tuple=("localhost", dict.get(port_number))
    del dict[port_number]
    dict[address_name] = tuple
    return dict

# pp = pprint.PrettyPrinter(indent=4)
load_network()
