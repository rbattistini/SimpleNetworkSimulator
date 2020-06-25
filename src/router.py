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

        self.routers_threads = init_params["routers_threads"]
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
        self.network_connections = self.router_data["network_connections"]
        if(self.server_ip in self.network_connections):
            max_conn_routers = min(len(self.routers_gateway_ip), 2)
            max_conn_routers = max(max_conn_routers, 5)
        else:
            max_conn_routers = 0
        self.init(max_conn_clients, max_conn_routers)

        self.packets_queue = []
        self.arp_table_socket = {}

        threading.Thread.__init__(self, name=self.router_id)
    
    """
    Router main loop.

    Listens for packets received from the server.
    """
    def run(self):

        utils.show_status(self.getName(), "starting")
        connected = self.go_online()
        if(self.connected_to_server is False):
            if(connected is True):
                utils.show_status(self.router_id, "listening for packets")
            
                while not self.stop_event.isSet():
                    self.listen_server_side_aux_router()

                utils.show_status(self.router_id, "closing connections")
                # self.socket_server_side.shutdown(0)
                self.socket_server_side.close()
                # self.socket_client_side.shutdown(0)
                self.socket_client_side.close()

            # exit procedure
            self.stop_event.clear()
            utils.show_status(self.router_id, "going offline")
            del self.routers_threads[self.router_id]
        elif(connected is True):
            utils.show_status(self.router_id, "listening for packets")
        else:
            self.join()
        
    """
    Tells the router to exit from its main loop.

    It goes offline thus closing its connection to the network.
    """
    def join(self, timeout=None):
        if(self.connected_to_server is True):
            utils.show_status(self.router_id, "going offline")
            self.socket_server_side.close()
            self.socket_client_side.close()
            self.stop_event.clear()
            del self.routers_threads[self.router_id]
        else:
            self.stop_event.set()
            threading.Thread.join(self, timeout)
    
    def send_message(self, parsed_message, destination_socket, destination_ip):
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
            self.router_id,
            "packet to the client could not be sent"
        )

        msg = " ".join(["message sent to", destination_ip])
        utils.show_status(self.router_id, msg)
    
    def forward_message(self, parsed_message, new_source_mac, destination_ip, 
    new_destination_mac):

        if(destination_ip not in self.routing_table):
            destination_socket = self.arp_table_socket[destination_ip]
        else:
            destination_socket = self.routing_table[destination_ip]

        parsed_message.update(
            source_mac=new_source_mac,
            destination_mac=new_destination_mac
        )

        self.send_message(parsed_message, destination_socket, destination_ip)

    def send_arp_request(self, parsed_message, new_source_mac, destination_ip):
        self.waiting_arp_request = True
        self.packets_queue.append(parsed_message)
        destination_socket = self.arp_table_socket[destination_ip]

        new_message = {
            "source_ip" : self.router_data["client_side"]["ip_address"],
            "destination_ip" : destination_ip,
            "source_mac" : new_source_mac,
            "destination_mac" : BROADCAST_MAC,
            "message" : "{ARP request}"
        }

        self.send_message(new_message, destination_socket, destination_ip)

    def forward_to_client(self, parsed_message):
        destination_ip = parsed_message["destination_ip"]
        new_source_mac = self.router_data["client_side"]["mac_address"]

        if(destination_ip not in self.arp_table_mac 
                and self.waiting_arp_request is False):
            utils.show_status(self.router_id, "sending ARP request")
            self.send_arp_request(parsed_message, new_source_mac, destination_ip)
        else:
            utils.show_status(
                self.router_id,
                "forwading packet to recipient client"
            )                    
            new_destination_mac = self.arp_table_mac[destination_ip]
            self.forward_message(
                parsed_message, 
                new_source_mac, 
                destination_ip, 
                new_destination_mac
            )
        
    def forward_to_server(self, parsed_message):
        destination_ip = self.server_ip
        new_source_mac = self.router_data["server_side"]["mac_address"]
        new_destination_mac = self.arp_table_mac[destination_ip]

        self.forward_message(
            parsed_message, 
            new_source_mac, 
            destination_ip,
            new_destination_mac
        )
    
    def forward_to_aux_router(self, parsed_message):
        destination_ip = parsed_message["destination_ip"]
        new_source_mac = self.router_data["server_side"]["mac_address"]
        recipient_router_ip = self.routing_table[destination_ip]
        new_destination_mac = self.arp_table_mac[recipient_router_ip]
        self.forward_message(
            parsed_message, 
            new_source_mac, 
            recipient_router_ip,
            new_destination_mac
        )
    
    def forward_to_main_router(self, parsed_message):
        new_source_mac = self.router_data["server_side"]["mac_address"]
        destination_ip = parsed_message["destination_ip"]

        # find the router to which this one is connected
        for ip_address in self.network_connections:
            self.main_router_ip_address = ip_address
            break


        new_destination_mac = self.arp_table_mac[self.main_router_ip_address]
        destination_socket = self.socket_server_side

        parsed_message.update(
            source_mac=new_source_mac,
            destination_mac=new_destination_mac
        )
        
        utils.show_status(
            self.router_id,
            "notifying main router of incoming message"
        )
        self.notify_incoming_message()

        self.send_message(parsed_message, destination_socket, destination_ip)

    def handle_message_main_router(self, parsed_message):
        destination_ip = parsed_message["destination_ip"]
        source_mac = parsed_message["source_mac"]

        for ip_address, mac_address in self.arp_table_mac.items():
            if(mac_address == source_mac):
                sender_ip_address = ip_address

        if(sender_ip_address == self.server_ip):
            if(destination_ip in self.arp_table_socket):
                self.forward_to_client(parsed_message)
            else:
                self.forward_to_aux_router(parsed_message)
        else:
            self.forward_to_server(parsed_message)

    def handle_message_aux_router(self, parsed_message):
        self.forward_to_client(parsed_message)

    """
    States whether a message received from the server should be sent to another 
    router or forwarded to one of the clients in its network.

    In the latter case states also if an ARP request should be made.

    If a message is received from a router then it is forwaded to the server.
    """
    def handle_message_server_side(self, parsed_message):

        utils.show_status(
            self.router_id,
            "deciding where the message should go..."
        )

        if(self.connected_to_server is True):
            self.handle_message_main_router(parsed_message)
        else:
            self.handle_message_aux_router(parsed_message)

    """
    States whether a message received from a client should be forwaded to the
    server or another router or treated as an ARP reply.
    """
    def handle_message_client_side(self, parsed_message):
        client_ip = parsed_message.get("source_ip")
        client_mac = parsed_message["source_mac"]

        if(self.waiting_arp_request is True):
            self.arp_table_mac[client_ip] = client_mac
            self.waiting_arp_request = False
            message_to_send = self.packets_queue.pop()
            self.handle_message_server_side(message_to_send)
        elif(self.connected_to_server is True):
            self.forward_to_server(parsed_message)
        else:
            utils.show_status(self.router_id, "forwading to main router")
            self.forward_to_main_router(parsed_message)
        
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
        # releasing lock, client can send the message
        self.sync_event_message.set()

        sender_socket = self.arp_table_socket[ip_address]
        self.listen_on_demand(sender_socket, self.handle_message_client_side)

    def listen_server_side_main_router(self, ip_address):
        sender_socket = self.arp_table_socket[ip_address]
        self.listen_on_demand(sender_socket, self.handle_message_server_side)
    
    def listen_on_demand(self, sender_socket, handler):
        utils.recv_msg(
            self.router_id,
            sender_socket,
            handler
        )

    """
    Always called by an auxiliary router.

    Tells the main router to start listening for a message from this router.
    """
    def notify_incoming_message(self):
        utils.show_status(
            self.router_id,
            "notifying an incoming message from this router"
        )
        
        my_ip_address = self.router_data["server_side"]["ip_address"]

        for router, router_data in self.routers_data.items():
            if(router_data["server_side"]["ip_address"] == \
            self.main_router_ip_address):
                router_id = router
                break

        router_thread = self.routers_threads[router_id]

        # tell the main router to start listening for a message 
        # from this router
        listen_task = threading.Thread(
            target=router_thread.listen_server_side_main_router,
            args=[my_ip_address],
            daemon=True
        )
        listen_task.start()

    """
    Listens for packets received from another router.
    
    Two possible cases:
    - the packet is forwarded to one of the clients connected to this router
    - the packet is forwarded to another router
    """
    def listen_server_side_aux_router(self):

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
                "reading packet received"
            )

            self.handle_message_server_side(parsed_message)

    """
    Called by a client that wants to connect.
    
    This router waits for a connection. As soon as a connection is established 
    the router updates accordingly its arp table socket.

    Returns true if a connection was recognized, false otherwise.
    """
    def listen_connections_client_side(self):

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
                    msg = " ".join(["connected with client", ip_address])
                    utils.show_status(self.router_id, msg)
                    self.sync_event_connection.set() # waiting for router approval
                    break # only the first valid connection is accepted

    """
    This router waits for a connection with a server or another router. 
    As soon as a connection is established the router updates accordingly its
    arp table socket.
    """
    def listen_connections_server_side(self):

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
            return True
        return False

    """
    Tries to accept connections from routers and the server of the network.
    """  
    def accept_connections(self):
        connections = len(self.routers_gateway_ip) + 1

        while connections > 0:
            connected = self.listen_connections_server_side()
            if(connected is True): 
                connections -= 1

        utils.show_status(self.router_id, "all connections established")

    def connect_with_routers(self):
        connected_to_all = True
        for ip_address, port in self.network_connections.items():
                connected = check.socket_connect(
                    self.socket_server_side,
                    ("localhost", port),
                    self.router_id
                )
                if(connected is True):
                    msg = " ".join(["connected with router:", ip_address])
                    utils.show_status(self.router_id, msg)
                else:
                    connected_to_all = False

        utils.show_status(self.router_id, "all connections established")
        return connected_to_all

    """
    A router connects with other routers or the server.
    
    This happens if specified in the network configuration file.
    """
    def go_online(self):
        if(self.server_ip in self.network_connections): 
            self.connected_to_server = True
            self.accept_connections() 
            connected = True
        else:   # connect with routers in network_connections
            connected = self.connect_with_routers()
            
        utils.show_status(self.router_id, "connected to the network")
        return connected

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
