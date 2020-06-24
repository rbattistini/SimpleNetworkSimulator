import socket
import threading
import time
from threading import Thread
import utilities as utils
import error_handling as check

BUFFER_SIZE = 1024
BROADCAST_MAC = "FF:FF:FF:FF:FF:FF"

class RouterThread(threading.Thread):

    """
    Initializes the router.

    The event synchronization primitive, among the initialization parameters
    given, is used to guarantee that the client will send its message when
    the router is actually listening.
    """
    def __init__(self, init_params):
        self.stop_event = threading.Event()
        self.waiting_arp_request = False
        self.connected_to_server = False

        self.router_threads = init_params["routers_threads"]
        self.server_id = init_params["server_id"]
        self.server_thread = init_params["server_thread"]
        self.clients_gateway_ip = init_params["clients_gateway_ip"]
        self.routers_gateway_ip = init_params["routers_gateway_ip"]
        self.arp_table_mac = init_params["arp_table_mac"]
        self.routers_data = init_params["routers_data"]
        self.router_id = init_params["router_id"]
        self.routing_table = init_params["routing_table"]
        self.sync_event_message = init_params["sync_event_message"]
        self.sync_event_connection = init_params["sync_event_connection"]
        self.router_data = self.routers_data[self.router_id]
        self.server_ip = self.router_data["server_side"]["server_ip"]

        max_conn_clients = min(len(self.clients_gateway_ip), 2)
        max_conn_clients = max(max_conn_clients, 5)
        max_conn_routers = min(len(self.routers_gateway_ip), 2)
        max_conn_routers = max(max_conn_routers, 5)

        self.init(max_conn_clients, max_conn_routers)

        self.packets_queue = []
        self.arp_table_socket = {}

        threading.Thread.__init__(self, name=self.router_id)
    
    """
    Router main loop.

    Listens for packets received from the server.
    """
    def run(self):

        connected = self.go_online()
        if(connected is True):
            while not self.stop_event.isSet():
                self.listen_server_side()

            utils.show_status(self.router_id, "closing connections")
            # self.socket_server_side.shutdown(0)
            self.socket_server_side.close()
            # self.socket_client_side.shutdown(0)
            self.socket_client_side.close()

        # exit procedure
        self.stop_event.clear()
        utils.show_status(self.router_id, "going offline")
        del self.router_threads[self.router_id]
    
    """
    Tells the router to exit from its main loop.

    It goes offline thus closing its connection to the network.
    """
    def join(self, timeout=None):
        self.stop_event.set()
        threading.Thread.join(self, timeout)
    
    """
    Called by a client that wants to connect.
    
    This router waits for a connection. As soon as a connection is established 
    the router updates accordingly its arp table socket.

    Returns true if a connection was recognized, false otherwise.
    """
    def listen_client_connection(self):

        utils.show_status(
            self.router_id,
            "releasing lock, client can connect to this router"
        )
        self.sync_event_connection.set()

        while True:
            client_connection, address = check.socket_accept(
                self.socket_client_side,
                self.router_id
            )

            if(client_connection != None and 
            client_connection not in self.arp_table_socket):    
                    ip_address = self.clients_gateway_ip[address[1]]
                    self.arp_table_socket[ip_address] = client_connection
                    msg = " ".join(["connected with client", str(ip_address)])
                    utils.show_status(self.router_id, msg)
                    self.sync_event_connection.set() # waiting for router approval
                    break # only the first valid connection is accepted

    """
    States whether a message received from the server should be sent to another 
    router or forwarded to one of the clients in its network.

    In the latter case states also if an ARP request should be made.
    """
    # TODO: finish here
    def handle_message_server_side(self, parsed_message):

        destination_ip = parsed_message["destination_ip"]
        utils.show_status(
            self.router_id,
            "deciding where the message should go..."
        )

        if(destination_ip not in self.routing_table):

            if(destination_ip not in self.arp_table_mac 
            and self.waiting_arp_request is False):

                utils.show_status(self.router_id, "sending ARP request")
                self.waiting_arp_request = True
                self.packets_queue.append(parsed_message)
            
                packet = utils.write_packet(
                    self.router_data["client_side"]["ip_address"],
                    destination_ip,
                    self.router_data["client_side"]["mac_address"],
                    BROADCAST_MAC,
                    "{ARP request}"
                )

                destination_socket = self.arp_table_socket[destination_ip]

                check.socket_send(
                    destination_socket,
                    packet,
                    self.router_id,
                    "Packet could not be sent"
                )

                return

            else:
                utils.show_status(
                    self.router_id,
                    "forwading packet to recipient client"
                )
                new_destination_mac = self.arp_table_mac[destination_ip]
                destination_socket = self.arp_table_socket[destination_ip]

        else:
            utils.show_status(
                self.router_id,
                "forwading packet to another router"
            )
            new_destination_mac = self.arp_table_mac[       
                    self.routing_table[destination_ip]
                ]
        
            destination_socket = self.arp_table_socket[       
                self.routing_table[destination_ip]
            ]

        new_source_mac = self.router_data["client_side"]["mac_address"]

        parsed_message.update(
                source_mac=new_source_mac,
                destination_mac=new_destination_mac
        )

        packet = utils.rewrite_packet(
            parsed_message    
        )

        # if(destination_socket is not None).
        check.socket_send( # WARNING
            destination_socket,
            packet,
            "Packet could not be sent"
        )
        time.sleep(2)
    
    def forward_to_server(self, parsed_message):
        destination_ip = self.server_ip
        new_source_mac = self.router_data["server_side"]["mac_address"]
        new_destination_mac = self.arp_table_mac[destination_ip]
        destination_socket = self.arp_table_socket[destination_ip]

        parsed_message.update(
            source_mac=new_source_mac,
            destination_mac=new_destination_mac
        )

        packet = utils.rewrite_packet(
            parsed_message    
        )

        utils.report(
            self.router_id,
            parsed_message,
            "preparing to forward the following packet:"
        )
        
        check.socket_send(
            destination_socket,
            packet,
            "packet to the server could not be sent"
        )

        msg = " ".join(["message sent to", destination_ip])
        utils.show_status(self.router_id, msg)
    
    # TODO: how to find destination socket here?
    def forward_to_router(self, parsed_message):
        destination_ip = self.server_ip # routing table?
        new_source_mac = self.router_data["server_side"]["mac_address"]
        new_destination_mac = self.arp_table_mac[destination_ip]
        destination_socket = self.arp_table_socket[destination_ip]

        parsed_message.update(
            source_mac=new_source_mac,
            destination_mac=new_destination_mac
        )

        packet = utils.rewrite_packet(
            parsed_message    
        )

        utils.report(
            self.router_id,
            parsed_message,
            "preparing to forward the following packet:"
        )
        
        check.socket_send(
            destination_socket,
            packet,
            "packet to the router could not be sent"
        )

        msg = " ".join(["message sent to", destination_ip])
        utils.show_status(self.router_id, msg)

    """
    States whether a message received from a client should be forwaded to the
    server or another router or treated as an ARP reply.
    """
    def handle_message_client_side(self, parsed_message):
        if(self.waiting_arp_request is True):
            self.arp_table_mac[
                parsed_message.get("source_ip")
            ] = parsed_message["source_mac"]
            self.waiting_arp_request = False
            packet_to_send = self.packets_queue.pop()
            self.handle_message_server_side(packet_to_send)
        elif(self.connected_to_server is True):
            self.forward_to_server(parsed_message)
        else:
            self.forward_to_router(parsed_message)
            time.sleep(2)

    """
    Listens for packets received from a client.

    Two possible cases:
    - ARP reply, update arp_table_mac and send last packet stored
    - forward message to the server
    """
    def listen_client_side(self, ip_address):
            
        utils.show_status(
            self.router_id,
            "releasing lock, client can send the message"
        )

        self.sync_event_message.set()

        sender_socket = self.arp_table_socket[ip_address]
        utils.recv_msg(
            self.router_id,
            sender_socket,
            self.handle_message_client_side
        )
        utils.show_status(self.router_id, "packet received successfully")

    """
    Listens for packets received from the server.
    
    Two possible cases:
    - the packet is forwarded to one of the clients connected to this router
    - the packet is forwarded to another router
    """
    def listen_server_side(self):
        received_message = check.socket_recv(
            self.socket_server_side,
            self.router_id
        )

        if(received_message is not None and len(received_message) > 0):
            parsed_message = utils.read_packet(received_message)

            msg = " ".join(["message received from:", self.server_ip])
            utils.show_status(self.router_id, msg)
            utils.report(
                self.router_id,
                parsed_message,
                "reading packet received from the server"
            )

            self.handle_message_server_side(parsed_message)
            time.sleep(2)

    """
    This router waits for a connection with a server or another router. 
    As soon as a connection is established the router updates accordingly its
    arp table socket.
    """
    def listen_connections(self):

        network_connection, address = check.socket_accept(
            self.socket_server_side,
            "Connection could not be established"
        )
    
        if(network_connection != None and
            network_connection not in self.arp_table_socket):
            
            if(address[1] in self.routers_gateway_ip):
                ip_address = self.routers_gateway_ip[address[1]]
                msg = " ".join(["connected with router:", ip_address])
                utils.show_status(self.router_id, msg)
            else:
                msg = " ".join(["connected with server:", self.server_ip])
                utils.show_status(self.router_id, msg)
                ip_address = self.server_ip
            self.arp_table_socket[ip_address] = network_connection

    def accept_connections(self):
        connections = len(self.routers_gateway_ip) + 1

        while connections > 0:
            self.listen_connections()
            connections -= 1

        utils.show_status(self.router_id, "all connections established")
   
    def connect_with_routers(self, network_connections):
        for ip_address, port in network_connections.items():
                connected = check.socket_connect(
                    self.socket_server_side,
                    ("localhost", port)
                )
                if(connected is True):
                    msg = " ".join(["connected with router:", ip_address])
                    utils.show_status(self.router_id, msg)

        utils.show_status(self.router_id, "all connections established")
    
    """
    A router connects with other routers or the server.
    
    This happens depending on the network configuration file, in the dictionary 
    network_connections.
    """
    def go_online(self):
        # time.sleep(2)
        network_connections = self.router_data["network_connections"]

        if(self.server_ip in network_connections): 
            self.connected_to_server = True
            self.accept_connections() 
        else:   # connect with routers in network_connections
            self.connect_with_routers(network_connections)
            
        utils.show_status(self.router_id, "connected to the network")

    """
    Creates two sockets, one for handling clients and the other for
    connecting to the network with the server and potentially with other
    routers.
    """
    def init(self, max_connections_clients, max_connections_routers):

        router_port = self.router_data["client_side"]["port"]
        address = ("localhost", router_port)

        self.socket_client_side = check.socket_create(
            address, 
            backlog = max_connections_clients, 
            timeout = 5, 
            reuse_address = True
        )

        router_port = self.router_data["server_side"]["port"]
        address = ("localhost", router_port)

        self.socket_server_side = check.socket_create(
            address, 
            backlog = max_connections_routers, 
            timeout = 5, 
            reuse_address = True
        )
