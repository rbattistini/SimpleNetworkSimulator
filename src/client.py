import socket
import threading
import time
from threading import Thread
import utilities as utils
import error_handling as check

BUFFER_SIZE = 1024
BROADCAST_MAC = "FF:FF:FF:FF:FF:FF"

class ClientThread(threading.Thread):

    """
    Initializes the client.

    The event synchronization primitive, among the initialization parameters
    given, is used to guarantee that the client will send its message when
    the router is actually listening.
    """
    def __init__(self, init_params): 

        self.connected = False

        self.clients_threads = init_params["clients_threads"]
        self.arp_table_mac = init_params["arp_table_mac"]
        self.client_data = init_params["client_data"]
        self.client_id = init_params["client_id"]
        self.router_thread = init_params["router_thread"]
        self.router_id = init_params["router_id"]
        self.sync_event_message = init_params["sync_event_message"]
        self.sync_event_connection = init_params["sync_event_connection"]
        
        self.stop_event = threading.Event()
        self.sleep_time = 1.0

        port = self.client_data["port"]
        address = ("localhost", port)
        self.client_connection = check.socket_create(
            address, 
            backlog = 0, 
            timeout = 3, 
            reuse_address = True
        )
        
        threading.Thread.__init__(self, name=self.client_id)

    """
    Client main loop.

    Listens for messages from the network.
    """         
    def run(self):
        utils.show_status(self.getName(), "starting")
        connected = self.go_online()

        if(connected is True):
            utils.show_status(self.client_id, "listening for incoming packets")
            while not self.stop_event.isSet():
                self.listen_packets()
        
        # exit procedure
        utils.show_status(self.client_id, "going offline")
        utils.show_status(self.client_id, "closing connection")
        self.client_connection.close()

        self.stop_event.clear()
        del self.clients_threads[self.client_id]
        
    """
    Tells the client to exit from its main loop.

    It goes offline thus closing its connection to the network.
    """
    def join(self, timeout=None):
        self.stop_event.set()
        threading.Thread.join(self, timeout)
        
    """
    Tells the router of its network to start listening for a message
    from this client.
    """
    def notify_incoming_message(self):
        msg = " ".join(["notifying", self.router_id, "of an incoming message"])
        utils.show_status(self.client_id, msg)
        my_ip_address = self.client_data["ip_address"]
        listen_task = threading.Thread(
            target=self.router_thread.listen_client_side,
            args=[my_ip_address],
            daemon=True
        )
        listen_task.start()
    
    """
    Tells the router of its network to start listening for a connection
    from this client.
    """
    def notify_incoming_connection(self):
        msg = " ".join(["notifying",self.router_id, \
         "of an incoming connection"])
        utils.show_status(self.client_id, msg)

        listen_task = threading.Thread(
            target=self.router_thread.listen_connections_client_side,
            daemon=True
        )
        listen_task.start()

    """
    Sends packets to other clients.
    """    
    def send_message(self, recipient_ip, message):

        gateway_ip = self.client_data["gateway_ip"]

        packet = utils.write_packet(
            self.client_data["ip_address"],
            recipient_ip,
            self.client_data.get("mac_address"),
            self.arp_table_mac[gateway_ip],
            message
        )

        utils.show_status(
            self.client_id,
            "waiting for router listening messages"
        )
        self.notify_incoming_message()
        # waiting for router approving message sending
        self.sync_event_message.wait()

        sent = check.socket_send(self.client_connection, packet, self.router_id)
        if(sent is True):
            msg = " ".join(["message sent to", gateway_ip])
            utils.show_status(self.client_id, msg)
        
        self.sync_event_message.clear()

    """
    Sends a special packet to notify the server it is currently online.

    Returns false if the connection was not established or the packet could not
    be sent (in the latter case the server will not recognize the client as 
    online, hence the action go_online is considered failed even if a connection
    has been created)
    """ 
    def go_online(self):
        
        utils.show_status(self.client_id, "connecting to the network")
        server_ip = self.client_data["server_ip"]
        router_port = self.client_data["gateway_port"]
        router_address = ("localhost", router_port)
        gateway_ip = self.client_data["gateway_ip"]

        self.notify_incoming_connection()
        # waiting for router approving connection
        self.sync_event_connection.wait() 
        self.sync_event_connection.clear() # ready for reuse

        connected = check.socket_connect(
            self.client_connection,
            router_address,
            self.client_id
        )
        
        if(connected is True):
            utils.show_status(self.client_id, "going online")
            # waiting for router completing connection procedure
            self.sync_event_connection.wait() 
            self.sync_event_connection.clear() # ready for reuse

            greeting_packet = utils.write_packet(
                self.client_data.get("ip_address"),
                server_ip,
                self.client_data.get("mac_address"),
                self.arp_table_mac[gateway_ip],
                "{going online}"
            )

            utils.show_status(
                self.client_id,
                "waiting for router accepting message"
            )
            self.notify_incoming_message()
            # waiting for router approving message sending
            self.sync_event_message.wait() 
            self.sync_event_message.clear()

            check.socket_send(
                self.client_connection,
                greeting_packet,
                self.client_id,
                "Greeting packet could not be sent"
            )
    
        return connected

    """
    Sends a special packet to notify the server it is currently offline.

    Then closes its connection to the network.
    """ 
    def go_offline(self):

        utils.show_status(self.client_id, "going offline")
        gateway_ip = self.client_data["gateway_ip"]
        server_ip = self.client_data["server_ip"]

        leave_packet = utils.write_packet(
            self.client_data.get("ip_address"),
            server_ip,
            self.client_data.get("mac_address"),
            self.arp_table_mac[gateway_ip],
            "{going offline}"
        )

        self.notify_incoming_message()
        self.sync_event_message.wait() # wait for router approval
        self.sync_event_message.clear()

        check.socket_send(
            self.client_connection,
            leave_packet,
            self.client_id,
            "Leave packet could not be sent"
        )

        self.join()

    """
    Listens for packets from the server.
    """
    def listen_packets(self):
        received_message = check.socket_recv(
            self.client_connection,
            self.client_id
        ) 

        if(received_message is not None and len(received_message) > 0):
            parsed_message = utils.read_packet(received_message)
            time.sleep(2) # give time to router to show its status
            msg = " ".join(["message received from:",
                parsed_message["source_ip"]])
            utils.show_status(self.client_id, msg)
            utils.report(
                self.client_id,
                parsed_message,
                "reading received packet"
            )

            if(parsed_message["destination_mac"] == BROADCAST_MAC):
                msg = " ".join(["received an ARP request from",
                    parsed_message["source_ip"]])
                utils.show_status(self.client_id, msg)

                self.send_message(
                    parsed_message.get("source_ip"),
                    "{ARP reply}"
                )
