class STPPacket:
	def __init__(self, header, data):
		self._header = header
		self._data = data

	def __str__(self):
		ret_string = str(self._header) + "\n"
		ret_string += self._data

		return ret_string