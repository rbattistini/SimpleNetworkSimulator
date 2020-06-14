#!/usr/bin/env python3

""" Script che legge il file network.yml e lancia la simulazione di un
network formato da un certo numero di server, router e clients"""

# Who choses the client to send to the router to create the arp table?

# Is needed a configuration run?
import server
# import client
# import router
import logging
import subprocess
import yaml
import time
import sys

""" Set up a simple logger which outputs to info.log """
logging.basicConfig(
    format='%(asctime)s %(message)s',
    filename='info.log',
    level=logging.INFO
)

""" Open the file network.yml and load its content on three dictionaries """
def load_network():
    try:
        with open('network.yml', "r") as file:
            logging.info("file loaded successfully")
            cfg = yaml.safe_load(file)
            server_info = cfg["server"]
            routers_info = cfg["routers"]
            clients_info = cfg["clients"]
    except yaml.YAMLError as msg:
        print("File loading failed. Error Code : " + str(msg[0]) + " Message " 
        + msg[1])
        sys.exit()
        

def print_countdown(string):
    print("starting",string, "in:")
    for x in [3,2,1]:
        time.sleep(1)
        print(str(x) + "...")
    time.sleep(1)
    print(string,"online")

def start_server():
    server.init()
    print_countdown("server")
    logging.info("server started successfully")
    subprocess.run("./server.py", timeout=10)


"""def start_client(args, x):
    args.append(x)
    print("[client",x, "]:" + "starting")
    logging.info("client started")
    for y in users_dict[x]:
        args.append(y)
    print(args)
    client.initialize(args[0], args[1], args[2], args[3])
    cmd = "./client" + str(x) + ".py" 
    print(cmd)
    subprocess.run(cmd)

def start_clients():
    args = {}
    for x in range(number_of_clients):
        start_client(args, x)
        args.clear()

def start_router():
    for x in range(number_of_routers):
        print("[router",x, "]:" + "starting")
        logging.info("router started")
        subprocess.run("./router.py")"""

if __name__ == "__main__":
    # this file is executed as script
    proc = start_server()
    # start_router()
    # start_clients()

