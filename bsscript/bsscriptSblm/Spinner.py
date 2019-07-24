import sublime

from . import SblmCmmnFnctns

class Spinner:
	SYMBOLS_ROW = u'←↑→↓'
	SYMBOLS_BOX = u'⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
	
	def __init__(self, symbols, view, startStr, endStr):
		self.symbols = symbols
		self.length = len(symbols)
		self.position = 0
		self.stopFlag = False
		self.view = view
		self.startStr = startStr
		self.endStr = endStr

	def __next__(self):
		self.position = self.position + 1
		return self.startStr + self.symbols[self.position % self.length] + self.endStr		

	def start(self):	
		if not self.stopFlag:
			self.view.set_status(SblmCmmnFnctns.SUBLIME_STATUS_SPINNER, self.__next__())
			sublime.set_timeout(lambda: self.start(), 300)

	def stop(self):
		self.view.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_SPINNER)
		self.stopFlag = True
