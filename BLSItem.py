import sublime
import os
import re
from . import CommonFunctions

check_Strong_Dependency_Result = {
	'blsName': None,
	'result': None,
	'errorChains': None
}

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

	def __checkOnStrongDependencyIteration(self, checkedBlsName, chain):
		def getBlsFullPath(srcDir, fileBaseName):			
			for root, dirs, files in os.walk(srcDir):
				for name in files:					
					if name.lower() == fileBaseName.lower():
						return os.path.join(root, name)
			return None		
		iterationChain = chain.copy()
		iterationChain.append(self.name)		
		if not self.dependence:			
			return
		
		for dependence in self.dependence:			
			if dependence == self.name:
				check_Strong_Dependency_Result['errorChains'].append(iterationChain)
				return
		
		for dependence in self.dependence:
			nextBLSItem = BLSItem(getBlsFullPath(self.srcDir, dependence + '.bls'), None)
			if checkedBlsName == dependence:
				check_Strong_Dependency_Result['errorChains'].append(iterationChain)
				return
			nextBLSItem.__checkOnStrongDependencyIteration(checkedBlsName, iterationChain)		

	def checkOnStrongDependency(self):
		check_Strong_Dependency_Result['blsName'] = self.name
		check_Strong_Dependency_Result['result'] = True
		check_Strong_Dependency_Result['errorChains'] = []
		self.__checkOnStrongDependencyIteration(check_Strong_Dependency_Result['blsName'], [])
		if len(check_Strong_Dependency_Result['errorChains']) > 0:
			check_Strong_Dependency_Result['result'] = False
		return check_Strong_Dependency_Result
		

