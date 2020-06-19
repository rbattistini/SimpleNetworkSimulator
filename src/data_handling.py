import sys
import yaml

# data used to execute commands
server_data = {}
routers_data = {}
clients_data = {}

# reference to threads for termination (close connections)
client_threads = {}
router_threads = {}
server_thread = {}

# translate the number in a string, a list of strings
client_ids = []

default_error_message = "\nFile loading failed:"

def load_network():
    network_info = {}
    try:
        with open('network.yml', "r") as file:
            # logging.info("file loaded successfully")
            cfg = yaml.safe_load(file)
            global server_data
            server_data = cfg["servers"]
            global routers_data
            routers_data = cfg["routers"]
            global clients_data 
            clients_data = cfg["clients"]
    except yaml.YAMLError as msg:
        print(default_error_message, msg)
        sys.exit()

    network_info["server_info"] = server_data
    network_info["routers_info"] = routers_data
    network_info["clients_info"] = clients_data
    complement_data()
    

def complement_data():
    generate_arp_tables()
    make_local_addresses()
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
Executes a set of functions to generate an ARP table for each entity of the 
network.
 
The generation of the ARP tables (only arp_table_mac) happens in this way:

- each client searches


"""

def generate_arp_tables():
    server_arp_table_generator()
    router_arp_table_generator()
    client_arp_table_generator()

def client_arp_table_generator(router_port):
    arp_table_mac = {}
    for router, router_info in routers_data.items():
        if router_info["client_side"]["default_gateway"] == router_port:
            arp_table_mac[router_info["client_side"]["ip_address"]] = router_info["client_side"]["mac_address"]

    return arp_table_mac

def server_arp_table_generator():
    arp_table_mac = {}

def router_arp_table_generator():
    arp_table_mac = {}

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
