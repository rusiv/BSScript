import sublime
import re

SECTION_START = '[SECTION]'
SECTION_END = '[END]'
SECTION_FIELDS = '[FIELDS]'

class _EifAssistant:
	def __init__(self):		
		self.view = None
		self.fields = []
				
	def initForView(self, view):
		self.view = view
		self.parseFile(view.file_name(), self.getEncoding(view))		

	def getEncoding(self, view):		
		enc = view.encoding()
		if (enc == 'UTF-8'):
			return 'utf-8'
		elif (enc == 'UTF-8 with BOM'):
			return 'utf-8-sig'
		else:
			return 'cp1251'

	def parseFile(self, fileName, enc):			
		self.fields.clear()
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

	def checkScope(self, scopes):
		result = False
		if (len(self.fields) == 0):
			return result
		if (scopes):
			arr = scopes.split(' ')
			if 'entity.name.section.record' in arr:
				result = True
		return result

	def _makePopup(self, fldName):
		return """
			<body id="FieldInfo">
				<style>
					html {
						margin: 0;
						padding: 0;
						border: 0;
					}
					body {
						margin: 0;
						padding: 6px 12px;
						border: 1px solid;
					}
					h1 {
						font-size: 1.1rem;
						font-weight: 500;						
						font-family: system;
					}
				</style>
				<h1>%s</h1>
			</body>
		""" % (fldName)

	def getCurrentFieldName(self, line, pos):		
		num = 0		
		for i, char in enumerate(line):
			if i > pos - 1: 
				break			
			if char == '|':
				num = num + 1				
		return self.fields[num]

	def showFieldName(self, line, pos):		
		fldName = self.getCurrentFieldName(line, pos)
		if (len(fldName) > 0):
			self.view.show_popup(self._makePopup(fldName), max_width = 512, max_height = 512)

			
eifAssistant = _EifAssistant()