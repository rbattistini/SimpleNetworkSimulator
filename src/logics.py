import logging

"""
Used by clients to create new messages that will be composed in packets by
the router and sent through the network. The client will include in the msg the 
actual string with the message and the destination_ip.

Server should not create new messages, only the clients should use this 
function.

- msg, (destination_ip, message)
- sending_socket, the socket from which the message can be sent
"""
def send_message(msg, sending_socket):
    # msg = create_msg(destination_ip, msg)
    # write_packet()
    sending_socket.send(bytes(msg, "utf-8"))

"""
Used by a client to close its socket.
"""
def go_offline():
    print("Going offline")

"""
Used by a client to reopen its socket after initialization.
"""
def go_online():
    print("Going online")

"""
States how a packet is created.

Used when an entity of the network needs to create a packet.
To signal others that the packet was sent from a specific entity.

- message_data, the dictionary with the correct info to write a packet,
responsibility of correctly forming this structure is demanded to another
function.
"""
def write_packet(message_data):

    IP_header = message_data.get("source_ip") + message_data.get("destination_ip")     
    
    ethernet_header =  message_data.get("source_mac") + message_data.get("destination_mac")

    packet = ethernet_header + IP_header + message_data.get("message")

    return packet


"""def create_message(source_ip, destination_ip, source_mac, destination_mac, payload):
    message["source_ip"] = source_ip
    message["destination_ip"] = destination_ip
    message["source_mac"] = source_mac
    message["destination_mac"] = destination_mac
    message["message"] = payload
    return message"""


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

    print("* Packet Level 2:")

    print("Source MAC address:", parsed_message.get("source_mac"), 
    "Destination MAC address: ", parsed_message.get("destination_mac"))

    print("* Packet Level 3:")

    print("Source IP address:",parsed_message.get("source_ip"), 
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
def bind_socket(socket, address):
    try:
        socket.bind(address)
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    print('Socket bind complete')

"""
Tries to receive a message from the socket given with the buffer size specified.
"""
def rcv_msg(socket, buffer_size):
    try:
        # it must wait for one of the clients to connect and send a message
        received_message = socket.recv(buffer_size).decode("utf-8")
        # if an error occurs probably is due to the router abandoning the 
        # network
    except OSError as msg:
        print("Message cannot be received. Error Code : " + str(msg[0]) 
        + " Message " + msg[1])
    print("Message successfully received")
    return received_message

"""
Sets up a simple logger which outputs to log_file.
"""
def logger(log_file):
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        filename= log_file,
        level=logging.INFO
    )

"""
Each entity of the network has an arp table. IP del destinatario è noto. 
(default gateway della rete) manca MAC address del default gateway
-> ARP request con indirizzo mac Address FF:FF:FF:FF:FF
IL MAC address del default gateway è necessario!!!
Aspetta una ARP request per compilare la sua arp table.
ARP configuration completed.

Livello 2 mac address
Livello 3 ip address


"""