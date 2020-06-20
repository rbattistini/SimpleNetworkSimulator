#!/usr/bin/env python3
import sys
import utilities as utils
import commands as cmd
import data_handling as data

command_ids = [
        "Make a client connect",
        "Make a client disconnect",
        "Send a message (requires an online client)",
        "Show help",
        "Quit"
]

prompt_dict = {
    "header" : "Commands:\n",
    "footer" : "\n\nType a number to launch the associated command:",
}

# functions used by the cli.

def init():
    network_data = data.load_network()
    client_ids = data.load_client_ids()

    server_thread = {}
    router_threads = {}
    client_threads = {}

    entity_threads = {
        "server_thread" : server_thread,
        "router_threads" : router_threads,
        "client_threads" : client_threads
    }

    # unpack dictionaries
    server_data = network_data["servers_data"]
    routers_data = network_data["routers_data"]
    # clients_data = network_data["clients_data"]

    # launch server
    for server_id, server_data in server_data:
        cmd.launch_server(server_thread, server_id, server_data, routers_data)

    # launch routers
    for router_id, router_data in routers_data:
        cmd.launch_router(router_threads, router_id, router_data)

    return network_data, entity_threads, client_ids

def show_welcome():
    data.load_text("ascii.txt")
    input("Press any key to initialize the network" + "\n> ")
    utils.clear()

"""
Used by show_network_status to gather info about the currents status of the
simulated network.
"""
def entity_status(row_format, entity_list, online_entity_list):
    status = ""
    for entity in entity_list:
        if(entity in online_entity_list):
            status = " online\n"
        else:
            status = " offline\n"
        print(row_format.format(entity,status), end="")

"""
Prints a table showing currently active entities.
"""
def show_network_status(network_data, entity_threads):

    # unpack dictionaries
    server_data = network_data["server_data"]
    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]

    server_thread = entity_threads["server_thread"]
    router_threads = entity_threads["router_threads"]
    client_threads = entity_threads["client_threads"]

    row_format = " {:<10} |  {:>8}"

    print("Network status:")
    utils.print_separator()

    print(row_format.format("entity", "status "))
    string = ""
    for _ in range(0,25):  string = string + '-'
    print(string)

    entity_status(row_format, server_data, server_thread)
    entity_status(row_format, routers_data, router_threads)
    entity_status(row_format, clients_data, client_threads)

    utils.print_separator()

"""
Prints a list of the available commands taken from the given commands_list.
"""
def show_prompt(commands_list):
    command_prompt = prompt_dict.get("header")
    for command in commands_list:
        command_prompt = command_prompt + "\n" + "[" 
        + str(commands_list.index(command) + 1) + "]: " 
        + command
    command_prompt = command_prompt + prompt_dict.get("footer")
    print(command_prompt)

"""
Associates to the chosen input a command.
"""
def launch_command(command, network_data, entity_threads, client_ids):

     # unpack dictionaries
    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]
    client_threads = entity_threads["client_threads"]

    if(command == "Make a client connect"):
        cmd.client_go_online(
            client_ids,
            client_threads,
            clients_data,
            routers_data
        )

    elif(command == "Make a client disconnect"):
        cmd.client_go_offline(
            client_ids,
            client_threads
        )

    elif(command == "Send a message (requires an online client)"):
        cmd.send_message_routine(
            client_ids,
            client_threads,
            clients_data
        )

    elif(command == "Show help"):
        cmd.show_help()
    elif(command == "Quit"):
        cmd.clean_quit(entity_threads)

"""
Used to clean up before exiting.
"""
def signal_handler(signal, frame, entity_threads):
    print( 'Exiting simulation (Ctrl+C pressed)')
    cmd.clean_quit(entity_threads)

"""
Command line interface main loop.
"""
def launch_helm():

    # show_welcome()
    network_data, entity_threads, client_ids = init()

    # TODO: add signal handler

    try:
        while True:  
            show_network_status(network_data,entity_threads)
            show_prompt(command_ids)
            command_id = utils.retrieve_id(utils.is_in_list, command_ids)

            utils.clear()
            utils.print_separator()

            launch_command(
                command_ids[command_id],
                network_data,
                entity_threads,
                client_ids
            )

            utils.clear()

    except KeyboardInterrupt:
        pass

launch_helm() 

