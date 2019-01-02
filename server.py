import socket, threading, time
import json
# import

port = 12345
addr = '127.0.0.1'
buff_size = 1024

fList = {} # store the files and their sizes
fLoc = {} # store the files and the peers keep them
curr_client = [] # clients that currently connect to the server 

# make the server sockets for the clients to make connection
def makeServSock():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', port))
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	print(sock.getsockname())
	sock.listen(5)
	print('listening...')

	return sock

def helper(client_sock):
	j_info = client_sock.recv(buff_size).decode()
	info = json.loads(j_info)
	addr = info[0]
	while True:
		request = client_sock.recv(buff_size).decode()
		time.sleep(0.1)
		if request == 'register':
			register(client_sock, info)
		elif request == 'list':
			listing(client_sock)

		elif request == 'location':
			location(client_sock)

		# elif request == 'Chunk register':

		elif request == 'leave':
			leave(client_sock, info)
			break

		else:	
			client_sock.send('Invalid request.'.encode())

# register function: 
def register(client_sock, info):
	print('Registering...')
	# print(info)
	info = tuple(info)
	fileNum = client_sock.recv(buff_size).decode()
	client_sock.send('Info acquired'.encode())

	time.sleep(0.1)
	for i in range(int(fileNum)):
		j_file = client_sock.recv(buff_size).decode()
		file = tuple(json.loads(j_file))
		fName = file[0]
		print(file)
		# print(fList)
		if file[0] not in fLoc:
			fLoc[file[0]] = []
		if inList(fName, info):
			continue
		fList[file[0]] = file[1]
		fLoc[file[0]].append(info)
		# fLoc[file].append(info) 
	print(fList, fLoc)
	time.sleep(0.1)
	server_reply = 'File registered'
	print(server_reply)
	client_sock.send(server_reply.encode())

	return 

def listing(client_sock):
	print('Sending the list...')
	file_len = len(fList)
	client_sock.send(str(file_len).encode())
	time.sleep(0.1)
	j_fList = json.dumps(str(fLoc))
	client_sock.send(j_fList.encode())
	print('File list sent')
	return 

def location(client_sock):
	j_fList = json.dumps(str(fLoc))
	client_sock.send(j_fList.encode()) # send the file list to the clients
	fileName = client_sock.recv(buff_size).decode() # receive the files that the client asked
	print("Transmitting location...")
	if fileName in fLoc:
		j_loc = json.dumps(fLoc[fileName])
		client_sock.send(j_loc.encode())
		return 
	client_sock.send('Not found!'.encode())
	print("Location transmitted")
	return 

def leave(client_sock, info):
	print(info, ' has left the connection.')
	addr = info[0]
	fList.pop(str(info), None) # need to change into checking the values to remove from the list
	print(fList)
	curr_client.remove(str(addr))
	time.sleep(0.1)
	client_sock.close()
	return 

def inList(fileName, info):
	for client_Info in fLoc[fileName]:
		if info == client_Info:
			return True
	return False

def connect(server_sock):
	client, addr = server_sock.accept()
	ipport = client.getsockname()
	print('Successfully connect to ', ipport[0])
	client.send('Welcome to P2P community! What can I get for you?'.encode())
	return client, addr


Server_sock = makeServSock()
while True:
	client, client_addr = connect(Server_sock)
	print(client_addr)
	curr_client.append(client_addr[0])
	print('current clients: ', curr_client)

	t = threading.Thread(target = helper, args = [client])
	t.start()
	

client.close()
Server_sock.close()


