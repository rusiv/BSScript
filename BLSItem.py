import sublime
import os
import re

class BLSItem:
	def __init__(self, blsFullName):
		self.name = os.path.splitext(os.path.basename(blsFullName).lower())[0]
		self.blsFullName = blsFullName
		self.addedToCompile = False
		self.dependence = self.__getDependence__(blsFullName)

	def __getDependence__(self, blsFullName):
		if (blsFullName == ''):
			print('BSScript: __getDependence__ no fullBLSFileName.')
			return None
		blsFile = open(blsFullName, "rb")
		data = blsFile.read().decode("cp1251", "ignore")
		blsFile.close()
		data = re.sub(r'{[\S\s]*?}', '', data, flags = re.IGNORECASE)
		data = re.sub(r'\(\*[\S\s]*?\*\)', '', data, flags = re.IGNORECASE)
		data = re.sub(r'//.*', '', data, flags = re.IGNORECASE)
		matcher = re.search(r'\buses\b([\s\S][^;]*);', data, flags = re.IGNORECASE)
		strUses = ''
		if (matcher):
			strUses = matcher.group(0)
			strUses = re.sub(r'\s', '', strUses, flags = re.IGNORECASE)
			strUses = strUses.lower()[4:-1]
		if (strUses != ''):
			return strUses.split(',')
		else:
			return None