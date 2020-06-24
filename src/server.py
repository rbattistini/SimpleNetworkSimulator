import socket
import time
import threading
import utilities as utils
import error_handling as check

BUFFER_SIZE = 1024

class ServerThread(threading.Thread):

    """
    Initializes the server.
    """
    def __init__(self, init_params):
        self.stop_event = threading.Event()
        self.connected = False

        self.server_thread = init_params["servers_thread"]
        self.arp_table_mac = init_params["arp_table_mac"]
        # self.routers_gateway_ip = init_params["routers_gateway_ip"]
        self.server_data = init_params["server_data"]
        self.server_id = init_params["server_id"]
        # self.sync_event_message = init_params["sync_event_message"]

        self.online_clients = {} # IP address - boolean

        port = self.server_data.get("port")
        address = ("localhost", port)
        self.server_connection = check.socket_create(
            address,
            backlog = 0,
            timeout = 0,
            reuse_address = True
        )
        # self.server_connection.settimeout(5)

        threading.Thread.__init__(self, name=self.server_id)

    """
    Server main loop.

    Listens for messages from the network.
    """         
    def run(self):
        utils.show_status(self.getName(), "starting")
        connected = self.go_online()

        if(connected is True):
            utils.show_status(self.server_id, "listening for incoming packets")
            while not self.stop_event.isSet():
                self.listen_packets()
        
        # exit procedure
        self.server_connection.close()
        utils.show_status(self.server_id,"going offline")
        del self.server_thread[self.server_id]

    """
    Tells the server to exit from its main loop.

    It goes offline thus closing its connection to the network.
    """
    def join(self, timeout=None):
        self.stop_event.set()
        threading.Thread.join(self, timeout)

    def mark_client_offline(self, parsed_message):
        online_ip = parsed_message.get("source_ip")
        self.online_clients[online_ip] = False
        msg = " ".join([online_ip, "is offline"])
        utils.show_status(self.server_id, msg)

    def mark_client_online(self, parsed_message):
        online_ip = parsed_message.get("source_ip")
        self.online_clients[online_ip] = True
        msg = " ".join([online_ip, "is online"])
        utils.show_status(self.server_id, msg)

    def is_client_unreachable(self, parsed_message):
        client_ip = parsed_message.get("destination_ip")
        return client_ip not in self.online_clients \
        or self.online_clients[client_ip] is False

    def send_message(self, parsed_message):
        destination_ip = self.server_data["gateway_ip"]
        packet = utils.rewrite_packet(parsed_message)

        msg = " ".join(["Sending message to:", destination_ip])
        utils.show_status(self.server_id, msg)

        check.socket_send(
            self.server_connection,
            packet,
            "Could not send the message"
        )

    def resend_back_message(self, parsed_message):    
        msg = " ".join(["client", parsed_message["destination_ip"], \
            "is not online: resending message back", str(parsed_message)])
        utils.show_status(self.server_id, msg)

        parsed_message.update(
            source_ip=self.server_data.get("server_ip"),
            source_mac=self.server_data.get("server_mac"),
            destination_mac=self.arp_table_mac[
                self.server_data["gateway_ip"]
            ],
            message="Client not currently available"

        )

        self.send_message(parsed_message)

    def forward_message(self, parsed_message):
        msg = " ".join(["client", parsed_message["destination_ip"], \
            "is online: forwading message"])
        utils.show_status(self.server_id, msg)

        parsed_message.update(
            source_mac=self.server_data.get("mac_address"),
            destination_mac=self.arp_table_mac[
                self.server_data["gateway_ip"]
            ]
        )

        utils.report(
            self.server_id,
            parsed_message,
            "reading packet received from a router"
        )

        self.send_message(parsed_message)

    """
    States what type of messages the server can handle.
    """
    def handle_message(self, parsed_message):
        time.sleep(3)
        utils.show_status(
            self.server_id,
            "deciding how to handle the message..."
        )

        if(parsed_message["message"] == "{going offline}"):
            self.mark_client_offline(parsed_message)
        elif(parsed_message["message"] == "{going online}"):
            self.mark_client_online(parsed_message)
        elif(self.is_client_unreachable(parsed_message)):
            self.resend_back_message(parsed_message)
        else:
            self.forward_message(parsed_message)
    
    """
    Listens for packets from the routers.

    Four possibilities:
    - a client notifies it is online
    - a client notifies it is going offline
    - a packet received from a client should be sent back to the sender because
    the recipient client is not online
    - a packet received from a client should be forwarded the the recipient
    client because it is online
    """
    def listen_packets(self):   

        utils.recv_msg(
            self.server_id,
            self.server_connection,
            self.handle_message
        )

        utils.show_status(self.server_id, "packet received successfully")

    """
    Connects to its default gateway.
    """
    def go_online(self):
        # time.sleep(1)
        utils.show_status(self.server_id, "connecting to the network")

        router_port = self.server_data["gateway_port"]
        router_address = ("localhost", router_port)
        gateway_ip = self.server_data["gateway_ip"]

        connected = check.socket_connect(
            self.server_connection,
            router_address
        )
        
        if(connected is True):
            msg = " ".join(["connected to", gateway_ip, "going online"])
            utils.show_status(self.server_id, msg)

        return connected