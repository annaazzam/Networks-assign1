from socket import *
import sys
from header import STPHeader, extractHeader, extractContent
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
		self._timer = time.time() + 99999999 # fix dis

		random.seed(seed)

		self.initSenderSocket()
		stp_packets = self.createSTPPackets()
		self._not_yet_acked_packets = stp_packets[:]

		self.sendPackets(stp_packets)

		self.terminateConnection()

		
	def initSenderSocket(self):
		# create a UDP server socket
		self._sender_socket = socket(AF_INET, SOCK_DGRAM)

		# ACK num 0 indicates no ack...
		firstHeader = STPHeader(Sender.current_seq_number, 0, 0, 1, 0, 0, False)
		Sender.current_seq_number += 1
		firstPacket = STPPacket(firstHeader, "")

		# THREE WAY HANDSHAKE:
		# send syn
		self.createUDPDatagram(firstPacket)
		# wait for a syn-ack
		message, addr = self._sender_socket.recvfrom(self._receiver_port)
		# send ack
		ackHeader = STPHeader(0, 0, 1, 0, 0, 0, False)
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
			Sender.current_seq_number += self._MSS
			i += self._MSS

		return stp_packets


	def sendPackets(self, stp_packets):
		sendbase = 0 # earliest not acked packet
		next_seq_num = 0 # earliest not sent packet

		while next_seq_num < len(stp_packets) * self._MSS:
			# when window finished, send all packets in this new window
			if sendbase >= next_seq_num:
				for i in range(0,(self._MWS / self._MSS)):
					if self.PLDModule():
						self.createUDPDatagram(stp_packets[sendbase + i])
					else:
						pass #is dropped!! ??
					#next_seq_num += len(extractContent(stp_packets[index]))
					next_seq_num += 1

			# try to get an ACK:
			self._sender_socket.setblocking(0)
			isAck = False
			ackNum = 0
			try:
				message, addr = self._sender_socket.recvfrom(self._receiver_port)
				header = STPHeader(extractHeader(message))
				isAck = header.isAck()
				ackNum = header.ackNum()
			except:
				# no packet right now
				pass

			currTimePassed = time.time() - self._timer

			if isAck: # received an ack
				print("ack got")
				if (ackNum > sendbase):
					i = 0
					for packet in stp_packets:
						if packet._header.seqNum() == ackNum:
							sendbase = i
							break
						i += 1
					#sendbase = ackNum
					if (sendbase < next_seq_num):
					 	self._timer = time.time() 
			elif currTimePassed >= self._timeout: # if timeout
				print("timeout happened")
				if self.PLDModule():
					self.createUDPDatagram(stp_packets[sendbase])
				else:
					pass # is dropped!! ??
				self._timer = time.time() 


	# Simulates packet loss
	def PLDModule(self):
		rand_num = random.random()
		if (rand_num >= self._pdrop):
			return True
		return False


	# creates a UDP packet, where the "data" in the packet
	# is the STP packet
	def createUDPDatagram(self, stp_packet):
		self._sender_socket.sendto(str(stp_packet).encode(), (self._receiver_host_ip, self._receiver_port))

	def terminateConnection(self):
		print ("made it boys")
		pass


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