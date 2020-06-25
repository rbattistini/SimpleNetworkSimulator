"""
Functions to handle errors with sockets.

A specific message of error, in addition to a standard error message, 
can be printed if specified.
"""
import socket
import logging
import commands as cmd
import utilities as utils
from cli import entities_threads

default_error_message = "\n Socket error occurred:"
default_exit_message = "\n Forcing shutdown "

def socket_create(address, backlog = 0, timeout = 0, reuse_address = False, additional_error_message = ""):
    try:
        connection = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        
        if(reuse_address == True):
            connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        connection.bind(address)

        if(backlog != 0):
            connection.listen(backlog)
        if(timeout != 0):
            connection.settimeout(timeout)
        
    except socket.error as error_msg:
        message = "[" + id + "]: " + default_error_message + error_msg \
        + "\n" + additional_error_message
        logging.error(message)
        return None
    
    return connection

def socket_connect(connection, address, id, additional_error_message = ""):
    try:
        connection.connect(address)
    except socket.error as msg:
        msg = default_exit_message + str(msg) + "\n" + additional_error_message
        msg = " ".join(["[" + id + "]:", msg])
        logging.error(msg)
        cmd.clean_quit(entities_threads)
        return False
    return True

def socket_send(connection, packet, id, additional_error_message = ""):
    try:
        connection.send(bytes(packet, "utf-8"))
    except socket.timeout as msg:
        return False
    except socket.error as msg:
        msg = default_error_message + str(msg) + "\n" + additional_error_message
        msg = " ".join(["[" + id + "]:", msg])
        logging.error(msg)
        return False
    return True
    
def socket_recv(connection, id, additional_error_message = "",
 buffer_size = 1024):
    try:
        received_message = connection.recv(buffer_size)
        received_message = received_message.decode("utf-8")
    except socket.timeout as msg:
        return None
    except socket.error as msg:
        msg = default_exit_message + str(msg) + "\n" + additional_error_message
        msg = " ".join(["[" + id + "]:", msg])
        logging.error(msg)
        cmd.clean_quit(entities_threads)
        return None
    return received_message

def socket_accept(conn_socket, id, additional_error_message = ""):
    try:
        connection, address = conn_socket.accept()
    except socket.timeout as msg:
        return (None, None)
    except socket.error as msg:
        msg = default_exit_message + str(msg) + "\n" + additional_error_message
        msg = " ".join(["[" + id + "]:", msg])
        logging.error(msg)
        cmd.clean_quit(entities_threads)
    return connection, address