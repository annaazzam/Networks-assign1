from socket import *
import sys
from header import STPHeader, extractHeader, extractContent
from packet import STPPacket

class Receiver():
	global current_ack_num

	def __init__(self, receiver_port, filename):
		self._receiver_port = receiver_port
		self._file = open(filename, "w")

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
		self._receiver_socket = socket(AF_INET, SOCK_DGRAM)
		self._receiver_socket.bind(("127.0.0.1", self._receiver_port))
		
		UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
		# check if syn
		print ("syn received")
		self.transmitACKPacket(1, True, addr)
		print("syn-ack sent")
		UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
		# check if ack
		print("ack received")

	def communicate(self):
		self._receiver_socket.setblocking(0)
		while True:
			try:
				UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
				print("received:", UDP_segment)
				self.writePacketData(UDP_segment.decode('utf-8'))
			except:
				pass

	def writePacketData(self, packet):
		print ("extracting: " + str(packet))
		contentToWrite = extractContent(str(packet))
		self._file.write(contentToWrite)


	# creates an ACK and sends it via the UDP socket
	def transmitACKPacket(self, ack_number, isSyn, clientAddress):
		ackHeader = STPHeader(0, ack_number, 1, isSyn, 0, 0, False)
		ackPacket = STPPacket(ackHeader, "")
		self._receiver_socket.sendto(str(ackPacket).encode(), clientAddress)


Receiver.current_ack_num = 0

receiver_port = int(sys.argv[1])
filename = sys.argv[2]
receiver = Receiver(receiver_port, filename)