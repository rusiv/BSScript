import sublime
import re

SECTION_START = '[SECTION]'
SECTION_END = '[END]'
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
		isStart = False
		for line in file:
			txt = line.strip().decode(enc, 'ignore')			
			matcher = re.search(r'^\[(.*?)\]', txt)
			if matcher != None:				
				sectionName = matcher.group(0)
				if (isStart == False) and (sectionName == SECTION_START):
					isStart = True
					continue
				if (sectionName == SECTION_END):
					isStart = False
					continue				
			else:
				if (sectionName == SECTION_FIELDS):
					self.fields.append(txt)

			
			