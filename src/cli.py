#!/usr/bin/env python3
import utilities as utils
import sys
import commands as cmd
import data_handling as data

commands_list = [
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

    # launch server
    for()

    # launch routers

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
def show_network_status(network_data, entity_data):

    server_data = network_data["server_data"]
    
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
        command_prompt = command_prompt + "\n" + "[" + str(commands_list.index(command) + 1) + "]: " + command
    command_prompt = command_prompt + prompt_dict.get("footer")
    print(command_prompt)

"""
Associates to the chosen input a command.

Higher order function used to avoid evaluating strings, representing commands, 
at runtime through exec method.
"""
def launch_command(command):
    if(command == "Make a client connect"):
        return cmd.client_go_online()
    elif(command == "Make a client disconnect"):
        return cmd.client_go_offline()
    elif(command == "Send a message (requires an online client)"):
        return cmd.send_message_routine()
    elif(command == "Show help"):
        return cmd.show_help()
    elif(command == "Quit"):
        return cmd.clean_quit()

"""
Used to clean up before exiting.
"""
def signal_handler(signal, frame):
    print( 'Exiting simulation (Ctrl+C pressed)')
    cmd.clean_quit()

"""
Command line interface main loop.
"""
def launch_helm():

    # show_welcome()
    init()

    while True:  
        show_network_status()
        show_prompt(commands_list)
        command_id = utils.retrieve_id(utils.is_in_list, commands_list)
        utils.clear()
        utils.print_separator()
        launch_command(commands_list[command_id])
        utils.clear()
        input("Press any key to return to the helm" + "\nCommand status:")
        utils.clear()

launch_helm() 

