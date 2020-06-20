import socket
import utilities as utils
import error_handling as check

BUFFER_SIZE = 1024

class Server:

    def __init__(self, server_thread, arp_table_mac, routers_gateway_ip,
     server_data, server_id):
        self.server_connection = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.server_connection.bind(server_data.get("port"))
        self.server_connection.listen(2)

        self.running = False
        self.routers_gateway_ip = routers_gateway_ip
        self.server_thread = server_thread
        self.server_data = server_data
        self.server_id = server_id

        self.arp_table_mac = arp_table_mac
        self.arp_table_socket = {}

    def run(self):
        self.online_clients = {} # IP address - boolean
        self.running = True
        self.connected = False
        
        # connect to router
        utils.show_status(self.server_id, "connecting to the network")
        connected = self.server_go_online()

        if(connected is True):
            utils.show_status(self.client_id, "connected to the network")
            while self.running is True:
                utils.show_status(self.client_id,
                 "listening for incoming packets")
                self.listen_packets()
        
        # exit procedure
        self.server_connection.close()
        utils.show_status(self.server_id,
                 "going offline")
        del self.server_thread[self]

    """
    Tells the server to go offline and consequently close its connection to the 
    network.
    """
    def stop_listening(self):
        self.running = False

    def mark_client_offline(self):
        self.online_clients[parsed_message.get("source_ip")] = False

    def mark_client_online(self):
        self.online_clients[parsed_message.get("source_ip")] = True

    def is_client_unreachable(self):
        return self.online_clients[
            self.parsed_message.get("destination_ip")
            ] is False or 
            self.online_clients[
            self.parsed_message.get("destination_ip")
            ] is None

    def resend_back_message(self):    
        msg = "Client" + self.parsed_message.get("destination_ip") + "is not online: resending message back"
        utils.show_status(self.server_id, msg)

        packet = utils.write_packet(
            self.server_data.get("server_ip"),
            self.parsed_message.get("source_ip"),
            self.server_data.get("server_mac"),
            self.arp_table_mac[
                self.server_data["gateway_ip"]
            ],
            "Client not currently available"
        )
        
        destination_socket =  self.arp_table_socket[
            self.server_data["gateway_ip"]
        ]

        check.socket_send(
            destination_socket,
            packet,
            "Could not send the message"
        )

    def forward_message(self):
        msg = "Client" + self.parsed_message.get("destination_ip") + "is online: forwading message"
        utils.show_status(self.server_id, msg)

        packet = utils.write_packet(
            self.parsed_message.get("source_ip"),
            self.parsed_message.get("destination_ip"),
            self.server_data.get("server_mac"),
            self.arp_table_mac[
                self.server_data["gateway_ip"]
            ],
            self.parsed_message.get("message")
        )

        destination_socket =  self.arp_table_socket[
            self.server_data["gateway_ip"]
        ]

        check.socket_send(
            destination_socket,
            packet,
            "Could not send the message"
        )

    """
    States what type of messages the server can handle.
    """
    def handle_message(self):
        if(self.parsed_message.get("message") == "{going offline}"):
            self.mark_client_offline()
        elif(self.parsed_message.get("message") == "{going online}"):
            self.mark_client_online()
        elif(self.is_client_unreachable()):
            resend_back_message()
        else:
            forward_message()
    
    """
    Listens for packets from the routers.
    """
    def listen_packets(self):   
        
        while True:
            received_message = check.socket_recv(
                self.server_connection,
                "Could not receive the message"
            )

            if(received_message is not None):
                self.parsed_message = utils.read_packet(received_message)

                msg = "Message received from: " + self.parsed_message["source_ip"]
                utils.show_status(self.server_id, msg)

                # four possibilities:
                # 1. a client notifies it is online 
                # 2. a client notifies it is offline
                # 3. a message should be sent back to a client
                # 4. a message should be forwarded to another client
                handle_message()

    """
    The server should be able to recognize the incoming connection associated to
    its default gateway and to accept all other connections.

    This way it can connect only with the needed router.
    """
    def server_go_online(self):

        # wait for all routers to connect and selectively builds its arp table socket (only one entry is needed)
        connections = len(self.routers_gateway_ip)
        while True:
            router_connection, address = self.server_connection.socket_accept("Connection could not be established")
            
            if(router_connection != None):
                print("Connected with router: ", address)
                connections -= 1
                if(self.routers_gateway_ip[address[1]] == self.server_data["gateway_ip"]):
                    self.arp_table_socket[self.server_data["gateway_ip"]] = router_connection
            if(connections == 0):
                print("All connections established")
                break

        return any(self.arp_table_socket)

