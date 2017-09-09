from socket import *
import sys
from header import STPHeader
from packet import STPPacket

class Sender:
	global current_seq_number

	def __init__(self, receiver_host_ip, receiver_port, filename, MWS, MSS, timeout, pdrop, seed):
		self._receiver_host_ip = receiver_host_ip
		self._receiver_port = receiver_port
		self._filename = filename
		self._MWS = MWS
		self._MSS = MSS
		self._timeout = timeout
		self._pdrop = pdrop
		self._seed = seed

		self.initSenderSocket()

	def initSenderSocket(self):
		# create a UDP server socket
		self._sender_socket = socket(AF_INET, SOCK_DGRAM)

		# ACK num 0 indicates no ack...
		firstHeader = STPHeader(current_seq_number, 0, 0, 1, 0, 0)
		firstPacket = STPPacket(firstHeader, "")

		self._sender_socket.sendto(str(firstPacket), (self._receiver_host_ip, self._receiver_port))
		

	# Reads the file and creates an STP segment
	def createSTPPackets(self):
		data = ""
		with open(self._filename,'r') as f:
			for line in f.read():
				data += line

		# split all the data up into packets
		stp_packets = []
		i = 0
		while i < data.length:
			curr_packet_data = [i:i+self._MSS]
			header = STPHeader(current_seq_number, 0, 0, 0, 0, 1)
			stp_packet = STPPacket(header, curr_packet_data)
			stp_packets.append(stp_packet)
			current_seq_number += 1
			i += self._MSS


	# applies STP protocol for reliable data transfer
	def STPProtocol(self):
		pass


	# Simulates packet loss
	def PLDModule(self):
		pass

	# creates a UDP packet, where the "data" in the packet
	# is the STP packet
	def createUDPDatagram(self):
		pass


	# sends the UDP packet to receiver
	def sendToReceiver(self):
		pass


#MAIN "FUNCTION":

current_seq_number = 0


receiver_host_ip = sys.argv[1]
receiver_port = int(sys.argv[2])
filename = sys.argv[3]
MWS = int(sys.argv[4])
MSS = int(sys.argv[5])
timeout = int(sys.argv[6])
pdrop = float(sys.argv[7])
seed = float(sys.argv[8])

sender = Sender(receiver_host_ip, receiver_port, filename, MWS, MSS, timeout, pdrop, seed)