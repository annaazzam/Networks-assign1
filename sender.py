from socket import *
import sys
from header import STPHeader, extractHeader, extractContent, HEADER_SIZE
from packet import STPPacket
import random
import time

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
		self._timer = getTime()
		self._startTime = getTime()
		self._log = open("Sender_log.txt", "w")
		self._buffer_size = HEADER_SIZE + MSS


		# REPORT DATA:
		self._dataTransferred = 0 # amount of data transferred in bytes
		self._numSegmentsSent = 0 # excluding retransmissions
		self._numDropped = 0 # num packets dropped by PLD
		self._numRetransmitted = 0 
		self._dupAcksReceived = 0

		random.seed(seed)

		self.initSenderSocket()
		stp_packets = self.createSTPPackets()
		self._not_yet_acked_packets = stp_packets[:]

		self.sendPackets(stp_packets)

		self.terminateConnection()

		
	def initSenderSocket(self):
		# create a UDP server socket
		self._sender_socket = socket(AF_INET, SOCK_DGRAM)

		# THREE WAY HANDSHAKE:
		# send syn
		firstHeader = STPHeader(Sender.current_seq_number, 0, 0, 1, 0, 0, False)
		Sender.current_seq_number += 1
		firstPacket = STPPacket(firstHeader, "")
		self.createUDPDatagram(firstPacket)

		# wait for a syn-ack
		#message, addr = self._sender_socket.recvfrom(self._buffer_size)
		message,addr = self.receive()

		# send ack
		ackHeader = STPHeader(2, 1, 1, 0, 0, 0, False)
		ackPacket = STPPacket(ackHeader, "")
		self.createUDPDatagram(ackPacket)

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

			header = STPHeader(Sender.current_seq_number, 0, 0, 0, 0, 1, False)
			stp_packet = STPPacket(header, curr_packet_data)
			stp_packets.append(stp_packet)
			Sender.current_seq_number += len(curr_packet_data)
			i += self._MSS

		return stp_packets


	def sendPackets(self, stp_packets):
		sendbase = 0 # earliest not acked packet
		next_seq_num = 0 # earliest not sent packet

		dupAcks = {} # To store duplicate ACKs

		while sendbase < len(stp_packets):
			# # when window finished, send all packets in this new window
			if sendbase == next_seq_num:
				for i in range(0,(self._MWS / self._MSS)):
					print ("hey sendin packet", sendbase +i)
					if (sendbase + i >= len(stp_packets)):
						break
					self._dataTransferred += len(stp_packets[sendbase + i]._data)
					self._numSegmentsSent += 1
					self.PLDModule(stp_packets[sendbase + i])
					next_seq_num += 1
					self._timer = getTime()

			# try to get an ACK:
			self._sender_socket.setblocking(0)
			isAck = False
			ackNum = 0
			try:
				#message, addr = self._sender_socket.recvfrom(self._buffer_size)
				message,addr = self.receive()
				header = STPHeader(extractHeader(message))
				isAck = header.isAck()
				ackNum = header.ackNum()
			except:
				# no packet right now
				pass

			if isAck: # received an ack
				print("ack got", ackNum)
				if (ackNum > stp_packets[sendbase]._header.seqNum()):
					i = 0
					found = 0
					dupAcks[ackNum] = 1
					for packet in stp_packets:
						if packet._header.seqNum() == ackNum:
							found = i
						i += 1
					if found != 0:
						sendbase = found

					lastPack = stp_packets[len(stp_packets) - 1]
					if ackNum == lastPack._header.seqNum() + len(lastPack._data):
						print("she did that")
						break

					#self._timer = getTime()
					if (sendbase < next_seq_num):
					 	self._timer = getTime()
				else:
					dupAcks[ackNum] += 1
					self._dupAcksReceived += 1
					if (dupAcks[ackNum] >= 3): # Fast retransmit!
						dupAcks[ackNum] = 0
						print ("fast retransmitting")
						self._numRetransmitted += 1
						for packet in stp_packets: 
							if packet._header.seqNum() == ackNum:
								self.PLDModule(packet)
								self._timer = getTime()

			elif getTime() - self._timer  >= self._timeout: # if timeout
				print("timeout happened")
				self._numRetransmitted += 1
				self.PLDModule(stp_packets[sendbase])
				self._timer = getTime()

	# Simulates packet loss
	def PLDModule(self, packet):
		rand_num = random.random()
		if (rand_num > self._pdrop):
			self.createUDPDatagram(packet)
			self.writeToLog("snd", getTime() - self._startTime, packet._header.getType(), packet._header.seqNum(), len(packet._data), packet._header.ackNum())
		else: #packet is dropped (not sent)
			self._numDropped += 1
			self.writeToLog("drop", getTime() - self._startTime, packet._header.getType(), packet._header.seqNum(), len(packet._data), packet._header.ackNum())
		

	# creates a UDP packet, where the "data" in the packet
	# is the STP packet
	def createUDPDatagram(self, stp_packet):
		self._sender_socket.sendto(str(stp_packet).encode(), (self._receiver_host_ip, self._receiver_port))

	def terminateConnection(self):
		self._sender_socket.setblocking(1)
		print ("made it boys")
		finHeader = STPHeader(Sender.current_seq_number,0, 0, 0, 1, 0, False)
		finPacket = STPPacket(finHeader, "")
		self.createUDPDatagram(finPacket)
		print ("sent FIN")

		# wait for ACK
		#message, addr = self._sender_socket.recvfrom(self._buffer_size)
		message,addr = self.receive()
		print ("recevied ACK")

		# wait for FIN
		#message, addr = self._sender_socket.recvfrom(self._buffer_size)
		message,addr = self.receive()
		print("received FIN")

		# send ACK
		ackHeader = STPHeader(Sender.current_seq_number,0, 0, 1, 0, 0, False)
		ackPacket = STPPacket(finHeader, "")
		self.createUDPDatagram(ackPacket)
		print("sent ack")

		self._log.write("Amount of (original) Data Transferred: " + str(self._dataTransferred) + "\n")
		self._log.write("Number of Data Segments Sent (Excluding retransmissions): " + str(self._numSegmentsSent) + "\n")
		self._log.write("Number of (all) Packets Dropped (by the PLD module): " + str(self._numDropped) + "\n")
		self._log.write("Number of Retransmitted Segments: " + str(self._numRetransmitted) + "\n")
		self._log.write("Number of Duplicate Acknowledgements received: " + str(self._dupAcksReceived) + "\n")

		
	# <snd/rcv/drop> <time> <type of packet> <seq-num> <num-of-bytes> <ack-num>
	# type of packet is S, A, F or D
	def writeToLog(self, sendRcv, time, packetType, seqNum, numBytes, ackNum):
		contentToWrite = sendRcv + " " + str(round(time, 2)) + " " + packetType + " " 
		contentToWrite += str(seqNum) + " " + str(numBytes) + " " + str(ackNum) + "\n"
		self._log.write(contentToWrite)

	def receive(self):
		message, addr = self._sender_socket.recvfrom(self._buffer_size)
		packetHeader = STPHeader(extractHeader(message))
		self.writeToLog("rcv", getTime() - self._startTime, packetHeader.getType(), packetHeader.seqNum(), len(extractContent(message)), packetHeader.ackNum())
		return message, addr

def getTime():
	return time.time() * 1000

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