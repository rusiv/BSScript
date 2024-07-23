import sublime
import re

SECTION_FIELDS = '[FIELDS]'

class EifAssistant:
	def __init__(self, view):
		self.view = view
		self.fields = []

		self.parseFile(view.file_name(), self.getEncoding(view))
		print(self.fields)

	def getEncoding(self, view):		
		enc = view.encoding()
		if (enc == 'UTF-8'):
			return 'utf-8'
		elif (enc == 'UTF-8 with BOM'):
			return 'utf-8-sig'
		else:
			return 'cp1251'

	def parseFile(self, fileName, enc):		
		file = open(fileName, 'rb')
		sectionName = ''
		for line in file:
			txt = line.rstrip().decode(enc, 'ignore')
			sectionName = re.search(r'\[(.*?)\]', txt)
			print(sectionName)

