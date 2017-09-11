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
		received_packets = {}
		next_expected = 0
		while True:
			UDP_segment = False
			try:
				UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
				print("received:", UDP_segment)


				header = STPHeader(extractHeader(UDP_segment))

				if header.isFin(): # Connection terminating!
					break

				seqNum = header.seqNum()
				received_packets[seqNum] = UDP_segment

				ackNum = self.getNewestACKNum(received_packets)

				self.transmitACKPacket(ackNum, 0, addr)
			except:
				pass

		self.writeAllPackets(received_packets)

	def getNewestACKNum(self, received_packets):
		highestSeqNum = max(received_packets.keys())
		return int(highestSeqNum) + int(len(extractContent(received_packets[highestSeqNum])))

	def writeAllPackets(self, received_packets):
		for k in sorted(received_packets.keys()):
			UDP_segment = received_packets[k]
			self.writePacketData(UDP_segment.decode('utf-8'))

	def writePacketData(self, packet):
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