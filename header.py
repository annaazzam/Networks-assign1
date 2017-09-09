HEADER_SIZE = 0

class STPHeader:
	def __init__(self, seq_num, ack_num, ack, syn, fin, data):
		self._seq_num = seq_num
		self._ack_number = ack_num

		# FLAGS
		self._ack = ack
		self._syn = syn
		self._fin = fin
		self._data = data


	# TODO(anna): add number padding to even out widths
	def __str__(self):
		ret_string = ""
		ret_string += str(self._seq_num) + " " + str(self._ack_number) + " "

		ret_string += ("A" if self._ack else "-")
		ret_string += ("S" if self._syn else "-")
		ret_string += ("F" if self._fin else "-")
		ret_string += ("D" if self._data else "-")

		return ret_string