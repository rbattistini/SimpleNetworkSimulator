"""
Functions to handle errors with sockets.

A specific message of error, in addition to a standard error message, 
can be printed if specified.
"""

import socket

default_error_message = "\n Socket error occurred:"

def socket_connect(connection, address, additional_error_message = ""):
    try:
        connection.connect(address)
    except socket.error as msg:
        print(default_error_message, msg)
        print(additional_error_message)
        return False
    return True

def socket_send(connection, packet, additional_error_message = ""):
    try:
        connection.send(bytes(packet, "utf-8"))
    except socket.error as msg:
        print(default_error_message, msg)
        print(additional_error_message)

def socket_recv(connection, additional_error_message = "", buffer_size = 1024):
    try:
        received_message = connection.recv(buffer_size).decode("utf-8")
    except socket.error as msg:
        print(default_error_message, msg)
        print(additional_error_message)
        return None
    return received_message

def socket_accept(socket, additional_error_message = ""):
    try:
        connection, address = socket.accept()
    except socket.error as msg:
        print(default_error_message, msg)
        print(additional_error_message)
        return None
    return connection, address