"""
Utility functions.

Three sections:

- logging
- packet structure conventions,
- user input validation,
- terminal interaction improvements

"""
import os
import sys
import logging
import error_handling as check

# logging

"""
Sets up a simple logger which outputs to log_file.
"""
def config_logger(log_file = ""):
    logging.basicConfig(
        format="%(levelname)s %(message)s",
        #format="%(name)s:[%(levelname)s]: %(message)s",
        #format="%(asctime)s %(message)s",
        filename= log_file,
        level=logging.INFO
    )

# message sending

def recv_msg(id, sender_socket, message_handler):
    received_message = check.socket_recv(sender_socket, id)

    if(received_message is not None and len(received_message) > 0):
        parsed_message = read_packet(received_message)

        msg = " ".join(["message received from:",
                parsed_message["source_ip"]])
        show_status(id, msg)
        report(id, parsed_message, "reading packet:")
        
        message_handler(parsed_message)

# packet structure conventions

"""
Write a packet given a compliant dictionary. 

(useful for packet partial modification)
"""
def rewrite_packet(message_data):
    source_ip = message_data["source_ip"]
    destination_ip = message_data["destination_ip"]
    source_mac = message_data["source_mac"]
    destination_mac = message_data["destination_mac"]
    payload = message_data["message"]

    packet = write_packet(
        source_ip,
        destination_ip ,
        source_mac,
        destination_mac,
        payload
    )

    return packet

"""
Write a packet from zero.
"""
def write_packet(source_ip, destination_ip, source_mac, destination_mac,
    payload):
    ip_header =  " ".join([source_ip, destination_ip])
    ethernet_header =  " ".join([source_mac, destination_mac])
    packet = " ".join([ip_header, ethernet_header, payload])
    return packet

"""
Read a packet and store the analysis in a standard dictionary if it
is written in a valid format.
"""
def read_packet(received_message):
    rcv_msg = received_message.split(" ", 4)
    if len(rcv_msg) > 4: 
        parsed_message = {
            "source_ip" : rcv_msg[0],
            "destination_ip" : rcv_msg[1],
            "source_mac" : rcv_msg[2],
            "destination_mac" : rcv_msg[3],
            "message" : rcv_msg[4]
        }
        return parsed_message
    else:
        return None

"""
Reads a packet following the rules adopted and shows it both in the 
currently configured logger and on stdin.
"""
def report(id, parsed_message, action):
    separator = ""
    for _ in range(0,80):  separator = separator + "*"

    msg = action \
    + "\n" + separator \
    + "\nLevel 2:" \
    + "\nSource MAC address: " + parsed_message["source_mac"] \
    + "\nDestination MAC address: " + parsed_message["destination_mac"] \
    + "\nLevel 3:" \
    + "\nSource IP address: " + parsed_message["source_ip"] \
    + "\nDestination IP address: " + parsed_message["destination_ip"] \
    + "\nMessage: \n" + parsed_message["message"] \
    + "\n" + separator

    show_status(id, msg)

"""
Performs an integrity check to see if the client should have received this 
packet.
"""
def integrity_check(client_id, client_data, parsed_message):
    print("Packet integrity check:")

    print("destination MAC address matches client", client_id, " MAC address: ",
    client_data["mac_address"] == parsed_message["destination_mac"])

    print("destination IP address matches client ", client_id, " IP address:",
    client_data["ip_address"] == parsed_message["destination_ip"])

# user input validation

def is_in_list(elem, list, entities_to_id):
    return int(elem)-1 in range(0,len(list))

def is_in_dict(elem, dict, entities_to_id):
    el = entities_to_id[int(elem)-1]
    return el in dict.keys()

def not_in_dict(elem, dict, entities_to_id):
    el = entities_to_id[int(elem)-1]
    return el not in dict.keys()

def is_number(number):
    try:
        int(number)
        return True
    except ValueError:
        return False

def retrieve_id(validator, validable_list, entities_to_id):
    request_completed = False
    while request_completed is False:
        id = input("\n> ")
        if(is_number(id) and validator(id, validable_list, entities_to_id)):
            request_completed = True
            return int(id)-1
        else:
            clear()
            print("Wrong client id inputted")

# terminal interaction improvements

def print_separator(min = 0, max = 50, separator_char = "*", spaces = True):
    string = ""
    for _ in range(min,max):  string = string + separator_char
    if(spaces is True):
        print("\n" + string + "\n")
    else:
        print(string, end='')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    # works both on posix and nt

def show_termination():
    input("Press any key to return to the helm" + "\nCommand status:")
    clear()

def show_status(entity_id, action):
    message = " ".join(["[" + entity_id + "]:", action])
    # print(message)
    logging.info(message)
