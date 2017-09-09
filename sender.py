from socket import *
import sys
from header import STPHeader
from packet import STPPacket
import random

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

		random.seed(seed)

		self.initSenderSocket()
		stp_packets = self.createSTPPackets()

		self.sendPackets(stp_packets)

		
	def initSenderSocket(self):
		# create a UDP server socket
		self._sender_socket = socket(AF_INET, SOCK_DGRAM)

		# ACK num 0 indicates no ack...
		firstHeader = STPHeader(Sender.current_seq_number, 0, 0, 1, 0, 0)
		Sender.current_seq_number += 1
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
		while i < len(data):
			curr_packet_data = data[i:i+self._MSS]
			header = STPHeader(Sender.current_seq_number, 0, 0, 0, 0, 1)
			stp_packet = STPPacket(header, curr_packet_data)
			stp_packets.append(stp_packet)
			Sender.current_seq_number += self._MSS
			i += self._MSS

		return stp_packets


	def sendPackets(self, stp_packets):
		# if timeout occurred:
			# retransmit not-yet-acknowledged segment with smallest
				# sequence number
			# start timer
		# elseif ACK received, with ACK field value of y
			# sendbase = y
			# if (there are currently any not-yet-acked segments) {
				# start timer
			# }
		# else:
			# for A packet in stp_packets:
			# 	if self.PLDModule():
			# 		self.createUDPDatagram(packet)
			# 	else:
			# 		pass #is dropped!! ??

	# Simulates packet loss
	def PLDModule(self):
		rand_num = random.random()
		if (rand_num < self._pdrop):
			return True
		return False


	# applies STP protocol for reliable data transfer
	def STPProtocol(self):
		pass

	# creates a UDP packet, where the "data" in the packet
	# is the STP packet
	def createUDPDatagram(self, stp_packet):
		self._sender_socket.sendto(str(stp_packet), (self._receiver_host_ip, self._receiver_port))


#MAIN "FUNCTION":

Sender.current_seq_number = 0


receiver_host_ip = sys.argv[1]
receiver_port = int(sys.argv[2])
filename = sys.argv[3]
MWS = int(sys.argv[4])
MSS = int(sys.argv[5])
timeout = int(sys.argv[6])
pdrop = float(sys.argv[7])
seed = float(sys.argv[8])

sender = Sender(receiver_host_ip, receiver_port, filename, MWS, MSS, timeout, pdrop, seed)