from socket import *
import sys

class Sender:
	#global current_seq_number

	def __init__(self, receiver_host_ip, receiver_port, filename, MWS, MSS, timeout, pdrop, seed):
		self._receiver_host_ip = receiver_host_ip
		self._receiver_port = receiver_port
		self._filename = filename
		self._MWS = MWS
		self._MSS = MSS
		self._timeout = timeout
		self._pdrop = pdrop
		self._seed = seed

		initSenderSocket()

	def initSenderSocket(self):
		# create a UDP server socket
		self._sender_socket = socket(AF_INET, SOCK_DGRAM)
		self._sender_socket.bind(('127.0.0.1', port)) # ?????


	def sendFileContents(self):
		data = ""
		with open(self._filename,'r') as f:
    		data = f.read()

    	header = Header()



#current_seq_number = 0
receiver_host_ip = sys.argv[1]
receiver_port = int(sys.argv[2])
filename = sys.argv[3]
MWS = int(sys.argv[4])
MSS = int(sys.argv[5])
timeout = int(sys.argv[6])
pdrop = float(sys.argv[7])
seed = float(sys.argv[8])

sender = Sender(receiver_host_ip, receiver_port, filename, MWS, MSS, timeout, pdrop, seed)