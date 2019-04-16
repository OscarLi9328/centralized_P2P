import socket, threading, time
import os, sys
import json

port = 12345
myPath = './'
# print(os.listdir(myPath))
Files = [f for f in os.listdir(myPath) if os.path.isfile(os.path.join(myPath, f))]
cFile = [[f, os.path.getsize(f)] for f in Files]

fileNum = len(cFile)

buff_size = 1024

# create peer-server socket
def makePeerServSock(addr, peer_port): 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print('socket created')
	localIP = sock.getsockname()[0]
	sock.bind((addr, peer_port))
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.listen(5)
	print('Listening...')

	return sock

# create socket to server
def makeServSock(addr):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((addr, port))

	return sock

# operations that deals with peers
def ToPeer(addr, peer_port):
	PeerSock = makePeerServSock(addr, peer_port)
	while True:
		peer_client_sock, peer_client_addr = connection(PeerSock)
		t = threading.Thread(target = fileTransmit, args = [peer_client_sock])
		t.start()
	sys.exit(0)

def ToServ(addr, peer_port):
	ServSock = makeServSock(addr)
	print(ServSock.recv(buff_size).decode()) # welcome to P2P connection!
	peer_info = [addr, peer_port]
	j_peer_info = json.dumps(peer_info)
	ServSock.send(j_peer_info.encode())

	while True:
		request = input('Enter your request: ')
		ServSock.send(request.encode())
		time.sleep(0.1)
		if request == 'register':
			# print(fileNum) 
			ServSock.send(str(fileNum).encode()) # send the server the number of files I have
			print(ServSock.recv(buff_size).decode()) # info acquired
			for f in cFile:
				j_file = json.dumps(f)
				ServSock.send(j_file.encode())
				time.sleep(0.1)
			print(ServSock.recv(buff_size).decode()) # the server reply

		elif request == 'list':
			print('num of files: ', ServSock.recv(buff_size).decode()) # receive the file list

			j_fLen = ServSock.recv(buff_size).decode() 
			fLen = json.loads(j_fLen)
			print(fLen)

		elif request == 'location':
			print(ServSock.recv(buff_size).decode()) # receive the file list from server
			fileName = input('Enter the file you want to download: ') 
			ServSock.send(fileName.encode()) # send the file name to server
			j_p_info = ServSock.recv(buff_size).decode()
			p_info = json.loads(j_p_info)
			print(p_info)
			p_addr = p_info[0]
			time.sleep(0.1)
			p_download = threading.Thread(target = download, args = [p_addr, fileName])
			p_download.start()

			print('File', fileName, 'has been downloaded.')

		elif request == 'leave':
			print(request)
			ServSock.close()
			os._exit(1)
		else:
			print(ServSock.recv(buff_size).decode())
			continue
		time.sleep(0.1)

def download(peer_info, fileName):
	newPath = './receiving'
	if not os.path.exists(newPath):
		os.makedirs(newPath)
	os.chdir(newPath)
	peer_addr = peer_info[0]
	peer_port = peer_info[1]
	print('Start downloading...')
	peerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	peerSock.connect((peer_addr, peer_port))

	file_path = newPath + '/' + fileName
	print(file_path)
	while True:
		data = peerSock.recv(buff_size)
		if not data:
			print('No more data')
			break
		with open(fileName, 'ab') as f:
			f.write(data)

	cFile.append([fileName, os.path.getsize('./' + fileName)])
	# print(cFile)

	peerSock.close()
	os.chdir('../')
	return 

def fileTransmit(clientPeer_sock):
	# addr = clientPeer_sock.getsockname()
	fn = clientPeer_sock.recv(buff_size).decode()
	print(fn)
	fp = './' + fn
	print(fp)
	while True:
		with open(fp, 'rb') as f:
			chunk = f.read(buff_size)
		clientPeer_sock.send(chunk.encode())
		if not chunk:
			break
		
	print(fn, 'has transmitted')
	clientPeer_sock.close()
	print('Connection closed')
	return 

def connection(socket):
	client, addr = socket.accept()
	ipport = client.getsockname()
	# print('Successfully connect to ', ipport)
	client.send('Welcome to P2P community!'.encode())
	return client, addr


if __name__ == '__main__':
	addr = input('Enter the address: ') # address to the server
	peer_port = int(input("Enter the port number: "))
	server_thread = threading.Thread(target = ToServ, args = [addr, peer_port])
	server_thread.start()
	client_thread = threading.Thread(target = ToPeer, args = [addr, peer_port])
	client_thread.start()






