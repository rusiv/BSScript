import sublime
import os
import re
from . import CommonFunctions

class BLSItem:
	def __init__(self, blsName, srcDir):
		if srcDir:
			self.srcDir = srcDir
			self.name = os.path.splitext(blsName.lower())[0]
			self.blsFullName = os.path.join(srcDir, blsName)
		else:
			self.srcDir = CommonFunctions.getWorkingDirForFile(blsName) + '\\SOURCE'
			self.name = os.path.splitext(os.path.basename(blsName).lower())[0]
			self.blsFullName = blsName
		self.addedToCompile = False
		self.dependence = self.__getDependence__()

	def __getDependence__(self):
		if (self.blsFullName == ''):
			print('BSScript: __getDependence__ no fullBLSFileName.')
			return None
		blsFile = open(self.blsFullName, "rb")
		data = blsFile.read().decode("cp1251", "ignore")
		blsFile.close()
		data = re.sub(r'{[\S\s]*?}', '', data, flags = re.IGNORECASE)
		data = re.sub(r'\(\*[\S\s]*?\*\)', '', data, flags = re.IGNORECASE)
		data = re.sub(r'//.*', '', data, flags = re.IGNORECASE)
		expr = re.compile(r'[^\']\buses\b([\s\S][^;]*);', flags = re.IGNORECASE)
		matcher = expr.search(data)
		strUses = ''
		while matcher:
			strUses = strUses + matcher.group(1) + ','
			strUses = re.sub(r'\s', '', strUses, flags = re.IGNORECASE)
			matcher = expr.search(data, matcher.end(1))
		if (strUses != ''):
			return strUses[:-1].split(',')
		else:
			return None