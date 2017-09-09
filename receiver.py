from socket import *
import sys
from header import HEADER_SIZE

class Receiver():
	def __init__(self, receiver_port, filename):
		self._receiver_port = receiver_port
		self._filename = filename

		self.beginCommunication()
		# create filename file.txt
			# all incoming data should be stored in this file
			# - extract STP packet from UDP datagram
			# - extract the data (i.e. payload) from STP packet
			# - can examine header of UDP datagram to determine
				# udp port & IP addr. that sender is using


	# 3-way handshake
	def beginCommunication(self):
		# make the UDP listening socket on the receiver_port
		# while loop waiting for a SYN
			# wait
		# on SYN, reply SYNACK segment

		self._receiver_socket = socket(AF_INET, SOCK_DGRAM)
		self._receiver_socket.bind(("127.0.0.1", self._receiver_port))

		while True:
			UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
			print (str(UDP_segment))

	def retrieveHeader(self, packet):
		pass

	# Receives packets from the UDP socket
	# -- called when recieved? orr.... 
	def receivePacket(self):
		# call STP protocol
			# write received data to a file
			# send ACK 
			#
		pass


	# applies STP protocol & retrieves the STP segment from UDP packet
	def STPProtocol(self):
		pass

	# creates an ACK and sends it via the UDP socket
	def transmitACKPacket(self):
		pass



receiver_port = int(sys.argv[1])
filename = sys.argv[2]
receiver = Receiver(receiver_port, filename)