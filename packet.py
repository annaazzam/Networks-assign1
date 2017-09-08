class STPPacket:
	def __init__(self, header, data):
		self._header = header
		self._data = data

	def __str__(self):
		return ""