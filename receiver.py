from socket import *
import sys
from header import HEADER_SIZE

class Receiver():
	global current_ack_num

	def __init__(self, receiver_port, filename):
		self._receiver_port = receiver_port
		self._filename = filename

		self._received_buffer = []

		self.beginCommunication()
		self.communicate()

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

		
		UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
		# check if syn
		# return syn-ack
		# wait for ack
		# return

			# create return segment for 3-way handshake


	def communicate(self):
		self._receiver_socket.setblocking(0)
		while True:
			UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
			print("hello", UDP_segment)


	# creates an ACK and sends it via the UDP socket
	def transmitACKPacket(self, ack_number, isSyn):
		ackHeader = STPHeader(0, ack_number, 1, isSyn, 0, 0, False)
		ackPacket = STPPacket(ackHeader, "")
		self._sender_socket.sendto(str(ackPacket).encode(), (self._receiver_host_ip, self._receiver_port))


Receiver.current_ack_num = 0

receiver_port = int(sys.argv[1])
filename = sys.argv[2]
receiver = Receiver(receiver_port, filename)