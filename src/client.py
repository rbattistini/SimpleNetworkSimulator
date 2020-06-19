import socket
import error_handling as check
import utilities as utils

BUFFER_SIZE = 1024

class Client:

    def __init__(self, client_threads, arp_table_mac, client_data):

        self.client_connection = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.running = False
        self.client_threads = client_threads
        self.arp_table_mac = arp_table_mac
        self.client_data = client_data
                
    def run(self, server_ip):
        self.running = True
        self.connected = False

        # connect to router
        connected = self.client_go_online(server_ip)

        if(connected is True):
            while self.running is True:
                self.listen_packets()

            self.client_go_offline(server_ip)
        
        # exit procedure
        print(self.client_threads)
        del self.client_threads[self]
        
    """
    Tells the client to go offline and consequently close its connection to the 
    network.
    """
    def stop_listening(self):
        self.running = False
        
    """
    Sends packets to other clients.
    """    
    def send_message(self, recipient_ip, message):

        gateway_ip = self.client_data.get("gateway_ip")

        packet = utils.write_packet(
            self.client_data["ip_address"],
            recipient_ip,
            self.client_data.get["mac_address"],
            self.arp_table_mac[gateway_ip],
            message
        )
        check.socket_send(
            self.client_connection,
            packet,
            "Requested message could not be sent"
        )

    """
    Sends a special packet to notify the server it is currently online.
    """ 
    def client_go_online(self, server_ip):
        
        router_address = self.client_data.get("router_address")
        gateway_ip = self.client_data.get("gateway_ip")

        connected = check.socket_connect(
            self.client_connection, 
            router_address,
            "Terminating thread"
        )

        if(connected is False):
            return False  
        else:
            print("client going online...")

            greeting_packet = utils.write_packet(
                self.client_data.get("ip_address"),
                server_ip,
                self.client_data.get("mac_address"),
                self.arp_table_mac[gateway_ip],
                "{going online}"
            )

            check.socket_send(
                self.client_connection,
                greeting_packet,
                "Greeting packet could not be sent"
            )

            return True

    """
    Sends a special packet to notify the server it is currently offline.
    """ 
    def client_go_offline(self, server_ip):
        
        print("client going offline...")
        gateway_ip = self.client_data.get("gateway_ip")

        leave_packet = utils.write_packet(
            self.client_data.get("ip_address"),
            server_ip,
            self.client_data.get("mac_address"),
            self.arp_table_mac[gateway_ip],
            "{going offline}"
        )

        check.socket_send(
            self.client_connection,
            leave_packet,
            "Leave packet could not be sent"
        )

        self.client_connection.close()

    """
    Listens for packets from the server.
    """
    def listen_packets(self):

            received_message = check.socket_recv(
                self.client_connection,
                "Requested message could not be sent"
            ) 

            parsed_message = utils.read_packet(received_message)     
            utils.report(parsed_message)
