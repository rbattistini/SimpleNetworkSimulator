import logging

"""
Used by clients to create new messages that will be composed in packets and sent
through the network.

Server should not create new messages, only the clients should use this 
function.
"""
def send_message(destination_ip):
    message = create_message()
    write_packet()
    destination_socket.send(bytes(packet, "utf-8"))

"""
States how a packet is created.

Used when an entity of the network needs to create a packet.
To signal others that the packet was sent from a specific entity.

- message_data, the dictionary with the correct info to write a packet,
responsibility of correctly forming this structure is demanded to another
function.
"""
def write_packet(message_data):

    IP_header = message_data.get("source_ip")
    + message_data.get("destination_ip")     
    
    ethernet_header =  message_data.get("source_mac") 
    + message_data.get("destination_mac")

    packet = ethernet_header + IP_header + message_data.get("message")

    return packet

"""
States how the header of a packet should be read.

Used when an entity of the network needs to disassemble a packet.
To see from where it was coming and where it should go.
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
Prints a message received by an entity of the network.
"""
def report(parsed_message):

    print("* Packet source:")

    print("Source MAC address:", parsed_message.get("source_mac"), 
    "Source IP address: ", parsed_message.get("source_ip"))

    print("* Packet destination:")

    print("Destination MAC address:",parsed_message.get("destination_mac"), 
    "Destination IP address: ", parsed_message.get("destination_ip"))

    print("* Message:")
    print(parsed_message.get("message"))

    print("***************************************************************")

"""
Performs an integrity check to see if the client should have received this 
packet.
"""
def integrity_check(client_data):
    print("* Packet integrity:")

    print("destination MAC address matches client", client_id,
    " MAC address: ", client_data.get("mac_address") == parsed_message.get("destination_mac"))

    print("destination IP address matches client ", client_id,
    " IP address:", client_data.get("ip_address") == parsed_message.get("destination_ip"))

"""
Tries to bind the socket to the host and port specified.
"""
def bind_socket(socket, to_bind):
    try:
        socket.bind(to_bind)
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    print('Socket bind complete')

"""
Sets up a simple logger which outputs to log_file.
"""
def logger(log_file):
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        filename= log_file,
        level=logging.INFO
    )
