import os
import pickle
import socket
import sys
import time
from turtle import onclick
from PIL import Image
import numpy
import threading

# function to check port number assignment
def check_args():
	if len(sys.argv) != 3:
		print("ERROR: Must supply port number \nUSAGE: py dfs1.py 10001")

check_args()

def get_client_and_message():
	client_num = input("Please enter client_number:")
	msg = input("Please enter your message:")
	return (client_num,msg)


# RUN DFS -------------------------------------------------	
server_name = sys.argv[1]
server_port = int(sys.argv[2])

# define socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_name, server_port))
server_socket.listen(5)
print('Server Connected...')
def recieve_client_message(client_socket):
	while True:
		global T
		# print("Recieving message.")
		full_chunk =b''
		new_msg = True
		HEADERSIZE = 10
		Client_id_header = 50
		recieved = False
		counter = 0
		got_new_msg = True
		while not recieved:
			print("In loop")
			try:
				chunk = client_socket.recv(1024)
				if new_msg:
					# print("here in new msg now.")
					chunk_len = int(chunk[:HEADERSIZE])
					sndr_client_id = int(chunk[HEADERSIZE:Client_id_header])
					# print("Length of chunk is : "+str(chunk_len),"\n Sender Client id is : "+str(sndr_client_id))
					new_msg = False
					
				full_chunk+=chunk
				if len(full_chunk)-(HEADERSIZE+Client_id_header) == chunk_len:
					try:
						full_chunk = pickle.loads(full_chunk[HEADERSIZE+Client_id_header:])
						recieved = True
					except Exception as e:
						print(e)
			except:
				got_new_msg = False
				recieved = True
		if got_new_msg:
			# print("here out now.")
			# chunk = 'Recieved msg from Client' +str(sndr_client_id)
			# print(chunk)
			print(full_chunk)
			T.insert(END,full_chunk+'\n')
			chunk = pickle.dumps(chunk)
			# print("Recieved message.")

def send_client_msg():
	global client_text
	global msg_text
	global T
	client_id = int(client_text.get("1.0", "end-1c"))
	msg = msg_text.get("1.0", "end-1c")
	T.insert(END,"Client"+str((server_port%10000)-1)+": "+msg+"\n")

	try:
		HEADERSIZE = 10
		FILENAME_HEADER = 50
		msg = pickle.dumps(msg)
		msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+bytes(f"{str(client_id):<{FILENAME_HEADER}}", 'utf-8')+msg
		client_socket.send(msg)
	except OSError:
		pass


try:
	client_socket, client_address = server_socket.accept()
	print("This is client "+str(server_port))
	rcv_thread = threading.Thread(target=recieve_client_message, args=(client_socket,))
	rcv_thread.start()
	# while True:
	# 	client_id =-10
	# 	msg = ''
		
	# 	snd_thread = threading.Thread(target=send_client_msg)
	# 	snd_thread.start()
	# 	snd_thread.join()
	# rcv_thread.join()
		
except Exception as e:
	print("Client Error: ",e)
	time.sleep(10)        



from tkinter import *
master = Tk()
master.geometry('400x500')
master.title("Client "+str((server_port%10000)-1))
Label(master, text='Messages').place(x =10,y =10)
T = Text(master)
T.place(x =10,y =30, height=300, width=350)
Label(master, text='Client ID').place(x =10,y =330)
client_text = Text(master)
client_text.place(x =10,y =350, height=20, width=350)
Label(master, text='Message').place(x =10,y =370)
msg_text = Text(master)
msg_text.place(x = 10,y = 390, height = 50, width = 350)
redbutton = Button(master, text = 'Send', fg ='red',command = send_client_msg)
redbutton.place(x = 10,y = 450,)
# recvbutton = Button(master, text = 'Recieve', fg ='blue',command = send_client_msg)
# recvbutton.pack()

mainloop()
# rcv_thread = threading.Thread(target=recieve_client_message, args=(client_socket,))
# rcv_thread.start()
	
