"""
Utility functions.

Three sections:

- packet structure conventions,
- user input validation,
- terminal interaction improvements

"""
import os
import sys

# packet structure conventions

"""
Write a packet given a compliant dictionary. 

(useful for packet partial modification)
"""
def modify_packet(message_data):

    IP_header = ""
    ethernet_header = ""
    IP_header = message_data.get("source_ip") + message_data.get("destination_ip")     
    
    ethernet_header =  message_data.get("source_mac") + message_data.get("destination_mac")

    packet = ethernet_header + IP_header + message_data.get("message")

    return packet

"""
Write a packet from zero.
"""
def write_packet(source_ip, destination_ip, source_mac, destination_mac, payload):
    IP_header = ""
    ethernet_header = ""
    IP_header =  IP_header + source_ip + destination_ip     
    ethernet_header =  ethernet_header + source_mac + destination_mac
    packet = ethernet_header + IP_header + payload
    return packet

"""
Read a packet and store the analysis in a standard dictionary.
"""
def read_packet(received_message):
    if len(received_message.split())>0: 
        parsed_message = {
            "source_mac" : received_message[0:17],
            "destination_mac" : received_message[17:34],
            "source_ip" : received_message[34:45],
            "destination_ip" : received_message[45:56],
            "message" : received_message[56:]
        }
        return parsed_message
    else:
        return None

"""
Read a packet following the rules adopted.
"""
def report(parsed_message):

    print("* Packet Level 2:")

    print("Source MAC address:", parsed_message.get("source_mac"), 
    "Destination MAC address: ", parsed_message.get("destination_mac"))

    print("* Packet Level 3:")

    print("Source IP address:",parsed_message.get("source_ip"), 
    "Destination IP address: ", parsed_message.get("destination_ip"))

    print("* Message:")
    print(parsed_message.get("message"))

    print_separator()

# user input validation

def is_in_list(elem, list):
    return int(elem)-1 in range(0,len(list))

def is_in_dict(elem, dict):
    return elem in dict.keys()

def not_in_dict(elem, dict):
    return elem not in dict.keys()

def is_number(number):
    try:
        int(number)
        return True
    except ValueError:
        return False

def retrieve_id(validator, validable_list):
    request_completed = False
    while request_completed is False:
        id = input("\n> ")
        if(is_number(id) and validator(id, validable_list)):
            request_completed = True
            return int(id)-1
        else:
            clear()
            print("Wrong client id inputted")

# terminal interaction improvements

def print_separator():
    string = ""
    for _ in range(0,50):  string = string + "*"
    print("\n" + string + "\n")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    # works both on posix and nt
