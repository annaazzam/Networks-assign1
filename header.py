HEADER_SIZE = 14

class STPHeader:
	def __init__(self, seq_num=0, ack_num=0, ack=0, syn=0, fin=0, data=0, isCopyConstructor=True):
		if isCopyConstructor: # Workaround for  2 constructors
			header = seq_num

			self._seq_num = int(header[0:4])
			self._ack_number = int(header[4:9])

			self._ack = (1 if header[10] != '-' else 0)
			self._syn = (1 if header[11] != '-' else 0)
			self._fin = (1 if header[12] != '-' else 0)
			self._data = (1 if header[13] != '-' else 0)
		else:
			self._seq_num = int(seq_num)
			self._ack_number = int(ack_num)

			# FLAGS
			self._ack = ack
			self._syn = syn
			self._fin = fin
			self._data = data

	def isAck(self):
		return self._ack

	def ackNum(self):
		return self._ack_number

	def seqNum(self):
		return self._seq_num

	def isFin(self):
		return self._fin

	def isSyn(self):
		return self._syn

	# TODO(anna): add number padding to even out widths
	def __str__(self):
		ret_string = ""

		ret_string += '{0:04d}'.format(self._seq_num) + " " + '{0:04d}'.format(self._ack_number) + " "

		ret_string += ("A" if self._ack else "-")
		ret_string += ("S" if self._syn else "-")
		ret_string += ("F" if self._fin else "-")
		ret_string += ("D" if self._data else "-")

		return ret_string

	def getType(self):
		ret_string = ""
		ret_string += ("A" if self._ack else "")
		ret_string += ("S" if self._syn else "")
		ret_string += ("F" if self._fin else "")
		ret_string += ("D" if self._data else "")
		return ret_string

def extractHeader(packet):
	packet = str(packet)
	return packet[:HEADER_SIZE]

def extractContent(packet):
	packet = str(packet)
	return packet[HEADER_SIZE:]

