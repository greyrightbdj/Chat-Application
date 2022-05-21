import glob
import os
import pickle
import socket
import subprocess
import sys
import time
from image_slicer import chunk_image
from image_slicer import combine_image
import threading
from PIL import Image

s_names = list()
s_ports = list()
client_status = list()
subprocesses = list() 
clients = [
    ('127.0.0.1','10001'),
    ('127.0.0.1','10002'),
    ('127.0.0.1','10003'),
    ('127.0.0.1','10004'),
    # ('127.0.0.1','10005'),
    # ('127.0.0.1','10006'),
    # ('127.0.0.1','10007'),
]
num_clients = len(clients)

def start_client(ip,port):
    try:
        p = subprocess.Popen('start python dfs_client.py '+ip+" "+port, shell=True)
        subprocesses.append(p)
        print("Client at port: "+port+" started.")
    except:
        print("Error starting the client at port: "+port)

client_sockets = list()
def client():
    global client_status
    global client_sockets
    for client in clients:
        start_client(client[0],client[1])
    
    for client in clients:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((client[0],int(client[1])))
            client_sockets.append(client_socket)
            print("Connected to server at Host:"+client[0]+" and Port:"+client[1])
            client_status.append("Connected")
            time.sleep(1)
        except ConnectionRefusedError:
            client_sockets.append(None)
            client_status.append("Failed")
            print("Failed to connect at Host:"+client[0]+" and Port:"+client[1])

client()

if len([1 for x in client_status if x == 'Connected']) == 0:
    print("No Active Client.\nExiting.")
    time.sleep(2)
    sys.exit()


def send_message(msg,sender,reciever,client_socket):
    print("Sending Message to : client"+str(reciever+1)+" "+str(client_sockets[reciever]))
    try:
        HEADERSIZE = 10
        FILENAME_HEADER = 50
        msg = pickle.dumps(msg)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+bytes(f"{str(sender):<{FILENAME_HEADER}}", 'utf-8')+msg
        client_sockets[reciever].send(msg)
        print("Sent.")
    except Exception as e :
        print(e)
        time.sleep(10)

def recieve_message(idx,client_socket):
    print("Listening from client "+str(idx))
    full_chunk =b''
    new_msg = True
    HEADERSIZE = 10
    Client_id_header = 50
    recieved = False
    # print('Client',str(idx)," started.")
    try:
        while not recieved:
            chunk = client_socket.recv(1024)
            if new_msg:
                chunk_len = int(chunk[:HEADERSIZE])
                rcvr_client_id = int(chunk[HEADERSIZE:Client_id_header])
                print("Length of chunk is : "+str(chunk_len),"\n Reciever Client id is : "+str(rcvr_client_id))
                new_msg = False
                
            full_chunk+=chunk
            if len(full_chunk)-(HEADERSIZE+Client_id_header) == chunk_len:
                try:
                    full_chunk = pickle.loads(full_chunk[HEADERSIZE+Client_id_header:])
                    recieved = True
                except Exception as e:
                    print(e)
        print((full_chunk))
        # chunk = 'Recieved msg from Client' +str(idx)
        # print(chunk)
        chunk = pickle.dumps(chunk)
        send_message("Client"+str(idx)+": "+full_chunk,idx,rcvr_client_id,client_socket)
        # print('Client',str(idx)," finished.")
    except Exception as e:
        print("Error Master Listener.")
        print(e)


done = False
while not done:
    recieve_file_threads = []
    for idx,client_socket in zip(range(0,len(client_sockets)),client_sockets):
        thread = threading.Thread(target=recieve_message, args=(idx,client_socket))
        thread.start()
        recieve_file_threads.append(thread)
    for thread in recieve_file_threads:
        thread.join()


