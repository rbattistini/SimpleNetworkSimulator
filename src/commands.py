import sys
import utilities as utils
from threading import Thread
from alt_client import ClientThread
import threading

client_id_request = "Type the id of the client"

# Functions used to implement commands

def launch_router():
    router_threads = {}
    for router_id, router_data in routers.items():
        print("Launching router ", router_id)
        router_thread = threading.Thread(target=run, args=[router_data])
        router_thread.start()
        router_threads[router_thread] = router_id
    
    for key in router_threads:
        print("waiting for termination of ", router_threads[key])
        key.join()
    
    print("***************************************************************")

def launch_server():
    print("Launching server")

# client go online

"""
Creating a client bound to the client_data dict passed.

Tries to connect and listens for packets.
Allows to send messages in future and to ask for termination.

If connection fails it simply closes itself and deletes autonomsly from the list
of currently active threads.

The client_id and client_threads are given for future reference.
"""
def launch_client(client_threads, client_id, client_data):
    
    arp_table_mac = client_arp_table_generator(client_data["router_address"][1])

    client_thread = ClientThread(client_threads, arp_table_mac, client_data)
    client_threads[client_id] = client_thread

    listen_task = threading.Thread(
        target=client_thread.run,
        args=[server_data.get("server_ip")],
    )

    listen_task.start()


# client go offline

def stop_client(client_threads, client_id):
    client_threads[client_id].stop_listening()
    del client_threads[client_id]

# send a message

def send_message(recipient_id, sender_id, message):
    # use the number to retrieve the thread from the list
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
def ask_sender(client_ids):
    print(client_id_request + " that will send a message")
    client_id = utils.retrieve_id(utils.is_in_list, client_threads)
    client_id = client_ids[client_id]
    return client_id

"""
Ask all currently executing threads to close their connections and waits for 
their effective termination. (join used, no daemon threads)
"""
def close_all_connections():
    print("call stop on all threads")

# functions used to execute commands

def client_go_online(client_ids):
    print(client_id_request + " that will go online")
    client_id = utils.retrieve_id(utils.not_in_dict, client_threads)
    client_id = client_ids[client_id]
    launch_client(client_threads, client_id, clients_data[client_id])

def client_go_offline(client_ids):
    print(client_id_request + " that will go offline")
    client_id = utils.retrieve_id(utils.is_in_dict, client_threads)
    client_id = client_ids[client_id]
    stop_client(client_threads, client_id)

def send_message_routine(client_ids):
    recipient = ask_recipient(client_ids)
    sender = ask_sender(client_ids)
    message = ask_message()
    return send_message(recipient, sender, message)

"""
Called by the cli or the signal handler, used to show the exit screen.
"""
def clean_quit():
    utils.clear()
    print("Exiting from the simulation...")
    close_all_connections()
    sys.exit()

def show_help():
    utils.print_separator()
    utils.load_text("help.txt")
