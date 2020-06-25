"""
Functions used to implement commands.
"""
import sys
import threading
import time
import logging
from threading import Thread
import utilities as utils
import data_handling as data
from server import ServerThread
from router import RouterThread
from client import ClientThread

client_id_request = "Type the id of the client"
sync_event_connection = threading.Event()
sync_event_message = threading.Event()

"""
Creating a router bound to the router_data dict passed.

Tries to connect to its network gateway and listens for packets.
Allows to forward packets to the server and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The router_id and routers_threads are given for future reference.

Note that it does NOT activate the network interface client_side and that it does
not have an arp table socket initialized. The router won't work if no clients
have previously contacted it.

To be functioning clients should be launched (connections established)
"""
def launch_router(router_id, entities_threads, network_data):

    # unpack dictionaries
    servers_data = network_data["servers_data"]
    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]

    routers_threads = entities_threads["routers_threads"]

    router_ip_server_side = routers_data[router_id]["server_side"]["ip_address"]
    router_ip_client_side = routers_data[router_id]["client_side"]["ip_address"]
    router_data = routers_data[router_id]

    arp_table_mac = data.router_arp_table_generator(
        servers_data,
        router_data
    )

    routers_gateway_ip = data.routers_ip_port_generator(
        routers_data,
        router_ip_server_side
    )

    clients_gateway_ip = data.clients_ip_port_generator(
        clients_data,
        router_ip_client_side
    )

    routing_table = {}
    routing_table = data.ask_routing_table(
        router_id,
        network_data,
        routing_table
    )
    
    init_params = {
        "router_id" : router_id,
        "routers_data" : routers_data,
        "routers_threads" : routers_threads,
        "clients_gateway_ip" : clients_gateway_ip,
        "routers_gateway_ip" : routers_gateway_ip,
        "arp_table_mac" : arp_table_mac,
        "routing_table" : routing_table,
        "sync_event_message" : sync_event_message,
        "sync_event_connection" : sync_event_connection
    }

    router_thread = RouterThread(
        init_params
    )
    
    routers_threads[router_id] = router_thread

    router_thread.start()

"""    listen_clients_connections_task = threading.Thread(
        target=router_thread.listen_client_connection,
        daemon=True
    )

    listen_clients_connections_task.start()"""


"""
Creating a server bound to the server_data dict passed.

Tries to connect to its default gateway and listens for packets.
Allows to monitor online and offline clients and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The server_id and server_thread are given for future reference.
"""
def launch_server(server_id, entities_threads, network_data):

    # unpack dictionaries
    servers_data = network_data["servers_data"]
    routers_data = network_data["routers_data"]

    routers_threads = entities_threads["routers_threads"]
    servers_threads = entities_threads["servers_threads"]

    server_data = servers_data[server_id]
    default_gateway = server_data["gateway_ip"]

    arp_table_mac = data.server_arp_table_generator(
        default_gateway,
        routers_data
    )

    for router, router_data in routers_data.items():
        if(router_data["server_side"]["ip_address"] == default_gateway):
            router_id = router
            break

    router_thread = routers_threads[router_id]

    init_params = {
        "servers_threads" : servers_threads,
        "arp_table_mac" : arp_table_mac,
        "router_id" : router_id,
        "router_thread" : router_thread,
        "server_data" : server_data,
        "server_id" : server_id,
    }

    server_thread = ServerThread(
        init_params
    )

    servers_threads[server_id] = server_thread

    """listen_task = threading.Thread(
        target=server_thread.run,
        daemon=False
    )

    listen_task.start()"""

    server_thread.start()

"""
Creating a client bound to the client_data dict passed.

Tries to connect to its default gateway and listens for packets.
Allows to send messages in future and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The client_id and clients_threads are given for future reference.
"""
def launch_client(clients_threads, client_id, client_data, routers_data, routers_threads):
    
    arp_table_mac = data.client_arp_table_generator(
        client_data["gateway_ip"],
        routers_data
    )

    default_gateway = client_data["gateway_ip"]

    for router, router_data in routers_data.items():
        if(router_data["client_side"]["ip_address"] == default_gateway):
            router_id = router
            break

    router_thread = routers_threads[router_id]

    init_params = {
        "clients_threads" : clients_threads,
        "arp_table_mac" : arp_table_mac,
        "client_data" : client_data,
        "client_id" : client_id,
        "router_thread" : router_thread,
        "router_id" : router_id,
        "sync_event_message" : sync_event_message,
        "sync_event_connection" : sync_event_connection
    }

    client_thread = ClientThread(
        init_params
    )

    clients_threads[client_id] = client_thread

    client_thread.start()

def stop_client(clients_threads, client_id):
    clients_threads[client_id].join()
    utils.show_status("cli", "client exited successfully")

"""
Show clients status
"""
def show_address_book(client_ids, clients_data, clients_threads):

    row_format = " {:10} | {:10} | {:10}"
    show_table_header("Clients list", row_format)
    hosts_status(clients_data, clients_threads, row_format)

"""
Show host id, ip_address and status.
"""
def hosts_status(hosts_data, hosts_thread, row_format):
    status = ""
    for host, host_data in hosts_data.items():
        if(host in hosts_thread):
            status = " online"
        else:
            status = " offline"
        ip_address = host_data["ip_address"]
        print(row_format.format(host, ip_address, status))

"""
Show router id, ip_address and status.
"""
def routers_status(routers_data, routers_threads, row_format):
    status = ""
    for router_id, router_data in routers_data.items():
        if(router_id in routers_threads):
            status = " online"
        else:
            status = " offline"
        ip_address = router_data["server_side"]["ip_address"]
        print(row_format.format(router_id, ip_address,status))
  
def show_table_header(title, row_format):

    print(title)
    utils.print_separator(False)

    print(row_format.format("entity", "ip_address", "status"))
    utils.print_separator(0,50,"-", False)
    print("")

def send_message(recipient_id, sender_id, message, clients_threads, clients_data):
    client_thread = clients_threads[sender_id]
    recipient_ip = clients_data[recipient_id]["ip_address"]
    client_thread.send_message(recipient_ip, message)

def ask_message():
    request_completed = False
    while request_completed is False:
        message = input("\nEnter the text message to send: ")
        choice = input("\nConfirm sending message: (type n to abort)")
        if(choice != "n"):
            request_completed = True
    return message

"""
Returns a string representing the identifier of the client that should receive
the message.

Note that it does not check if a thread of the client is currently running.
This way the server can resend the message back to the sender if a client not
in the clients_threads list is chosen.
"""
def ask_recipient(client_ids, clients_data, clients_threads):
    print(client_id_request + " that will receive the message")
    show_address_book(client_ids, clients_data, clients_threads)
    client_id = utils.retrieve_id(utils.is_in_list, client_ids, client_ids)
    return client_ids[client_id]

"""
Returns a string representing the identifier of the client that should send
the message.

Note that the client must be online.
"""
def ask_sender(client_ids, clients_data, clients_threads):
    print(client_id_request + " that will send a message")
    show_address_book(client_ids, clients_data, clients_threads)
    client_id = utils.retrieve_id(utils.is_in_list, clients_threads, client_ids)
    return client_ids[client_id]

"""
Ask all currently executing threads to close their connections and waits for 
their effective termination. 
"""
def close_all_connections(entities_threads):
    utils.show_status("main", "beginning shutdown")
    # unpack dictionary
    servers_threads = entities_threads["servers_threads"]
    routers_threads = entities_threads["routers_threads"]
    clients_threads = entities_threads["clients_threads"]

    # creating defensive copies to avoid changing size of the dictionary during
    # iteration
    servers_threads_list = list(servers_threads.values())
    routers_threads_list = list(routers_threads.values())
    clients_threads_list = list(clients_threads.values())

    for server_thread in servers_threads_list:
        server_thread.join()

    for router_thread in routers_threads_list:
        router_thread.join()

    for client_thread in clients_threads_list:
        client_thread.join()

    utils.show_status("main", "shutdown completed")

# functions used to execute commands

def client_go_online(client_ids, clients_threads, clients_data, routers_data, routers_threads):
    print(client_id_request + " that will go online")
    show_address_book(client_ids, clients_data, clients_threads)
    client_id = utils.retrieve_id(utils.not_in_dict, clients_threads, client_ids)
    client_id = client_ids[client_id]

    launch_client(
        clients_threads,
        client_id,
        clients_data[client_id],
        routers_data,
        routers_threads
    )

def client_go_offline(client_ids, clients_data, clients_threads):
    print(client_id_request + " that will go offline")
    show_address_book(client_ids, clients_data, clients_threads)
    print(clients_threads)
    client_id = utils.retrieve_id(utils.is_in_dict, clients_threads, client_ids)
    client_id = client_ids[client_id]
    stop_client(clients_threads, client_id)

def send_message_routine(client_ids, clients_threads, clients_data):
    recipient = ask_recipient(client_ids, clients_data, clients_threads)
    sender = ask_sender(client_ids, clients_data, clients_threads)
    message = ask_message()
    send_message(recipient, sender, message, clients_threads, clients_data)

"""
Called by the cli or the signal handler, used to show the exit screen.
"""
def clean_quit(entities_threads):
    # utils.clear()
    print("Exiting from the simulation...")
    # logging.info(str(entities_threads))
    close_all_connections(entities_threads)
    # time.sleep(5)
    sys.exit()

def show_help():
    utils.print_separator()
    utils.load_text("help.txt")

class MyHandler:
    def __init__(self, entities_threads):
        self.entities_threads = entities_threads
    def __call__(self, signo, frame):
        clean_quit(self.entities_threads)