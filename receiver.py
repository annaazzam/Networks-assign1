from socket import *
import sys

class Receiver():
	def __init__(self, receiver_port, filename):
		self._receiver_port = receiver_port
		self._filename = filename
		
		# set up receiver socket


receiver_port = sys.argv[1]
filename = sys.argv[2]
receiver = Receiver(receiver_port, filename)