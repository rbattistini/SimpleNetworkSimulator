"""
Functions used to implement commands.
"""
import sys
import threading
from threading import Thread
import utilities as utils
import data_handling as data
from client import Client
from server import Server

client_id_request = "Type the id of the client"

"""
Creating a router bound to the router_data dict passed.

Tries to connect to its network gateway and listens for packets.
Allows to forward packets to the server and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The router_id and router_threads are given for future reference.

Note that it does NOT activate the network interface client_side and that it does
not have an arp table socket initialized. The router won't work if no clients
have previously contacted it.

To be functioning clients should be launched (connections established)
"""
# TODO: implement this
def launch_router(router_threads, router_id, router_data):
    print("S")

"""
Creating a server bound to the server_data dict passed.

Tries to connect to its default gateway and listens for packets.
Allows to monitor online and offline clients and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The server_id and server_thread are given for future reference.
"""
def launch_server(server_thread, server_id, server_data, routers_data):

    arp_table_mac = data.server_arp_table_generator(
        server_data["gateway_ip"],
        routers_data
    )

    routers_gateway_ip = data.generate_routers_list(
        routers_data
    )

    server_thread = Server(
        server_thread,
        arp_table_mac,
        routers_gateway_ip,
        server_data,
        server_id
    )

    server_thread[server_id] = server_thread

    listen_task = threading.Thread(
        target=server_thread.run,
    )

    listen_task.start()

    return listen_task

"""
Creating a client bound to the client_data dict passed.

Tries to connect to its default gateway and listens for packets.
Allows to send messages in future and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The client_id and client_threads are given for future reference.
"""
def launch_client(client_threads, client_id, client_data, routers_data):
    
    arp_table_mac = data.client_arp_table_generator(
        client_data["gateway_ip"],
        routers_data
    )

    client_thread = Client(
        client_threads,
        arp_table_mac,
        client_data,
        client_id
    )

    client_threads[client_id] = client_thread

    listen_task = threading.Thread(
        target=client_thread.run
    )

    listen_task.start()
    
    return listen_task

# client go offline

def stop_client(client_threads, client_id):
    client_threads[client_id].stop_listening()
    del client_threads[client_id]

# send a message

def send_message(recipient_id, sender_id, message, client_threads, clients_data):
    client_thread = client_threads[sender_id]
    recipient_ip = clients_data[recipient_ip]["ip_address"]
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
in the client_threads list is chosen.
"""
def ask_recipient(client_ids):
    print(client_id_request + " that will receive the message")
    client_id = utils.retrieve_id(utils.is_in_list, client_ids)
    client_id = client_ids[client_id]
    return client_id

"""
Returns a string representing the identifier of the client that should send
the message.

Note that the client must be online.
"""
def ask_sender(client_ids, client_threads):
    print(client_id_request + " that will send a message")
    client_id = utils.retrieve_id(utils.is_in_list, client_threads)
    client_id = client_ids[client_id]
    return client_id

"""
Ask all currently executing threads to close their connections and waits for 
their effective termination. (join used, no daemon threads)
"""
# TODO: decide if join should be used
def close_all_connections(entity_threads):

    # unpack dictionaries
    server_thread = entity_threads["server_thread"]
    router_threads = entity_threads["router_threads"]
    client_threads = entity_threads["client_threads"]

    for server, server_thread in server_thread.items():
        server_thread.stop_listening()
        server_task.join()
    for router, router_thread in router_threads.items():
        router_thread.stop_listening()
        router_task.join()
    for client, client_thread in client_threads.items():
        client_thread.stop_listening()
        client_task.join()

# functions used to execute commands

def client_go_online(client_ids, client_threads, clients_data, routers_data):
    print(client_id_request + " that will go online")

    client_id = utils.retrieve_id(utils.not_in_dict, client_threads)
    client_id = client_ids[client_id]

    launch_client(
        client_threads,
        client_id,
        clients_data[client_id],
        routers_data
    )

def client_go_offline(client_ids, client_threads):
    print(client_id_request + " that will go offline")
    client_id = utils.retrieve_id(utils.is_in_dict, client_threads)
    client_id = client_ids[client_id]
    stop_client(client_threads, client_id)

def send_message_routine(client_ids, client_threads, clients_data):
    recipient = ask_recipient(client_ids)
    sender = ask_sender(client_ids, client_threads)
    message = ask_message()
    send_message(recipient, sender, message, client_threads, clients_data)

"""
Called by the cli or the signal handler, used to show the exit screen.
"""
def clean_quit(entity_threads):
    utils.clear()
    print("Exiting from the simulation...")
    close_all_connections(entity_threads)
    sys.exit()

def show_help():
    utils.print_separator()
    utils.load_text("help.txt")
