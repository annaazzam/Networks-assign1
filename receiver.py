from socket import *
import sys
from header import STPHeader, extractHeader, extractContent
from packet import STPPacket
import time

class Receiver():
	global current_ack_num

	def __init__(self, receiver_port, filename):
		self._receiver_port = receiver_port
		self._file = open(filename, "w")
		self._received_buffer = []
		self._log = open("Receiver_log.txt", "w")

		#REPORT DATA:
		self._dataReceived = 0
		self._numSegmentsReceived = 0
		self._numDupSegmentsReceived = 0

		self.beginCommunication()
		self.communicate()

	# 3-way handshake
	def beginCommunication(self):
		self._receiver_socket = socket(AF_INET, SOCK_DGRAM)
		self._receiver_socket.bind(("127.0.0.1", self._receiver_port))
		
		# Receive SYN
		UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
		self._startTime = getTime() # start timer once communication begins
		receivedHeader = STPHeader(extractHeader(UDP_segment))
		self.writeToLog("rcv", getTime() - self._startTime, receivedHeader.getType(), receivedHeader.seqNum(), len(extractContent(UDP_segment)), receivedHeader.ackNum())

		# Send SYN ACK
		self.transmitACKPacket(1, True, addr)

		# Receive ACK
		UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
		receivedHeader = STPHeader(extractHeader(UDP_segment))
		self.writeToLog("rcv", getTime() - self._startTime, receivedHeader.getType(), receivedHeader.seqNum(), len(extractContent(UDP_segment)), receivedHeader.ackNum())
		
	def communicate(self):
		self._receiver_socket.setblocking(0)
		received_packets = {} # Buffer for out-of-order received packets
		next_expected = 1
		while True:
			# tries to get a packet - either DATA or FIN
			try:
				UDP_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
				receivedHeader = STPHeader(extractHeader(UDP_segment))
				self.writeToLog("rcv", getTime() - self._startTime, receivedHeader.getType(), receivedHeader.seqNum(), len(extractContent(UDP_segment)), receivedHeader.ackNum())

				header = STPHeader(extractHeader(UDP_segment))

				if header.isFin(): # Connection terminating!
					self.terminateConnection(addr)
					break

				seqNum = header.seqNum()
				if (seqNum in received_packets.keys()):
					self._numDupSegmentsReceived += 1
				else:
					self._dataReceived += len(extractContent(UDP_segment))
				received_packets[seqNum] = UDP_segment

				#self._dataReceived += len(extractContent(UDP_segment))
				self._numSegmentsReceived += 1

				if (seqNum == next_expected):
					next_expected = int(seqNum) + int(len(extractContent(UDP_segment)))
					while next_expected in received_packets.keys():
						next_expected += int(len(extractContent(received_packets[next_expected])))

				self.transmitACKPacket(next_expected, 0, addr)
			except:
				pass

		self.writeAllPackets(received_packets)

	def writeAllPackets(self, received_packets):
		for k in sorted(received_packets.keys()):
			UDP_segment = received_packets[k]
			self.writePacketData(UDP_segment.decode('utf-8'))

	def writePacketData(self, packet):
		contentToWrite = extractContent(str(packet))
		self._file.write(contentToWrite)

	# creates an ACK and sends it via the UDP socket
	def transmitACKPacket(self, ack_number, isSyn, clientAddress):
		ackHeader = STPHeader(Receiver.current_ack_num, ack_number, 1, isSyn, 0, 0, False)
		ackPacket = STPPacket(ackHeader, "")
		self._receiver_socket.sendto(str(ackPacket).encode(), clientAddress)
		self.writeToLog("snd", getTime() - self._startTime, ackHeader.getType(), ackHeader.seqNum(), 0, ackHeader.ackNum())
		Receiver.current_ack_num += 1

	def terminateConnection(self, addr):
		# send ack
		self.transmitACKPacket(0, 0, addr)

		# send fin
		finHeader = STPHeader(0, 0, 0, 0, 1, 0, False)
		finPacket = STPPacket(finHeader, "")
		self._receiver_socket.sendto(str(finPacket).encode(), addr)
		self.writeToLog("snd", getTime() - self._startTime, finHeader.getType(), finHeader.seqNum(), 0, finHeader.ackNum())
		# receive ACK
		self._receiver_socket.setblocking(1)
		ack_segment, addr = self._receiver_socket.recvfrom(self._receiver_port)
		receivedHeader = STPHeader(extractHeader(ack_segment))
		self.writeToLog("rcv", getTime() - self._startTime, receivedHeader.getType(), receivedHeader.seqNum(), len(extractContent(ack_segment)), receivedHeader.ackNum())

		self._log.write("Amount of (original) Data Received: " + str(self._dataReceived) + "\n")
		self._log.write("Number of Data Segments Received: " + str(self._numSegmentsReceived) + "\n")
		self._log.write("Number of duplicate segments received " + str(self._numDupSegmentsReceived) + "\n")
		

	def writeToLog(self, sendRcv, time, packetType, seqNum, numBytes, ackNum):
		contentToWrite = sendRcv + " " + str(round(time, 2)) + " " + packetType + " " 
		contentToWrite += str(seqNum) + " " + str(numBytes) + " " + str(ackNum) + "\n"
		self._log.write(contentToWrite)

def getTime():
	return time.time() * 1000


Receiver.current_ack_num = 0

receiver_port = int(sys.argv[1])
filename = sys.argv[2]
receiver = Receiver(receiver_port, filename)