#!/usr/bin/env python3
import sys
import signal
import time
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
    "footer" : "\n\nType a number to launch the associated command: \n" \
            + "(type q to return to this commands' list)",
}

entities_threads = {}

# functions used by the cli.

def init():
    network_data = data.load_network("../resources/network.yml")
    # unpack dictionaries
    servers_data = network_data["servers_data"]
    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]

    client_ids = data.load_client_ids(clients_data)

    servers_threads = {}
    routers_threads = {}
    clients_threads = {}

    global entities_threads
    entities_threads = {
        "servers_threads" : servers_threads,
        "routers_threads" : routers_threads,
        "clients_threads" : clients_threads
    }

    # launch main router connected to the server
    for router_id, router_data in routers_data.items():
        network_connections = router_data["network_connections"]
        server_ip = router_data["server_side"]["server_ip"]    
        if(server_ip in network_connections):
            cmd.launch_router(router_id, entities_threads, network_data)
        
    # launch server  
    for server_id, server_data in servers_data.items():
        cmd.launch_server(server_id, entities_threads, network_data)
    
    # launch other routers
    for router_id, router_data in routers_data.items():
        network_connections = router_data["network_connections"]
        server_ip = router_data["server_side"]["server_ip"]    
        if(server_ip not in network_connections):
            cmd.launch_router(router_id, entities_threads, network_data)

    return network_data, entities_threads, client_ids

def show_welcome():
    data.load_text("../resources/ascii.txt")
    input("Press any key to initialize the network" + "\n> ")
    utils.clear()


"""
Prints a table showing currently active entities.
"""
def show_network_status(network_data, entity_threads):

    # unpack dictionaries
    servers_data = network_data["servers_data"]
    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]

    servers_thread = entity_threads["servers_threads"]
    routers_threads = entity_threads["routers_threads"]
    clients_threads = entity_threads["clients_threads"]

    row_format = " {:<15} | {:<15} | {:<15}"

    cmd.show_table_header("Network status:", row_format)
    cmd.hosts_status(servers_data, servers_thread, row_format)
    cmd.routers_status(routers_data, routers_threads, row_format)
    cmd.hosts_status(clients_data, clients_threads, row_format)

    utils.print_separator()

"""
Prints a list of the available commands taken from the given commands_list.
"""
def show_prompt(commands_list):
    command_prompt = prompt_dict["header"]
    for command in commands_list:
        command_prompt = command_prompt + "\n" + "[" + str(commands_list.index(command) + 1) + "]: " + command
    command_prompt = command_prompt + prompt_dict["footer"]
    print(command_prompt)

"""
Associates to the chosen input a command.
"""
def launch_command(command, network_data, entity_threads, client_ids):

     # unpack dictionaries
    routers_data = network_data["routers_data"]
    clients_data = network_data["clients_data"]
    clients_threads = entity_threads["clients_threads"]
    routers_threads = entity_threads["routers_threads"]

    if(command == "Make a client connect"):
        cmd.client_go_online(
            client_ids,
            clients_threads,
            clients_data,
            routers_data,
            routers_threads
        )

    elif(command == "Make a client disconnect"):
        cmd.client_go_offline(
            client_ids,
            clients_data,
            clients_threads
        )

    elif(command == "Send a message (requires an online client)"):
        cmd.send_message_routine(
            client_ids,
            clients_threads,
            clients_data
        )

    elif(command == "Show help"):
        cmd.show_help()
    elif(command == "Quit"):
        cmd.clean_quit(entity_threads)

"""
Command line interface main loop.
"""
def launch_cli():
    
    utils.config_logger("messages.log")
    show_welcome()
    network_data, entities_threads, client_ids = init()
    signal.signal(signal.SIGINT, cmd.MyHandler(entities_threads))

    try:
        while True:  
            show_network_status(network_data,entities_threads)
            show_prompt(command_ids)
            command_id = utils.retrieve_id(utils.is_in_list, command_ids, command_ids)

            utils.clear()
            utils.print_separator()

            launch_command(
                command_ids[command_id],
                network_data,
                entities_threads,
                client_ids
            )

            utils.clear()

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    launch_cli() 

