import sublime
import os
from .BLSItem import BLSItem


class BSSCompiler:
	def __init__(self, settings):		
		if (settings != None):
			self.workingDir = settings.get("working_dir", "")
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.copyBLLs = True

	def __compile__(self, workingDir, blsPath, path, protectServer, protectServerAlias, copyBLLs):
		if (blsPath == ''):
			print('BSScript: No bls for compile.')
			return		
		if (workingDir == '') or (protectServer == '') or (protectServerAlias == ''):
			print('BSScript: Not all settings are filled out.')
			return
		if path == '':
			path = 'exe;system;user'
		activeWindow = sublime.active_window()
		onFinishedFunctionName = "copyBllsInUserPaths" if copyBLLs else ""
		args = {
			"working_dir": workingDir,
			"encoding": "cp1251",
			"path": path,
			"cmd": ["bscc.exe ", blsPath, "-S" + protectServer, "-A" + protectServerAlias, "-Tuser"],
			"file_regex": "Program\\s(.*)\\s*.*\\s*.*line is (\\d*)",
			"quiet": True,
			"on_finished_function_name": onFinishedFunctionName #при использовании колбэка sublime.py выбрасывает ошибку
		}
		activeWindow.run_command('my_exec', args)

	def compile(self, blsPath):
		self.__compile__(self.workingDir, blsPath, '', self.protectServer, self.protectServerAlias, self.copyBLLs)

	compileBLS = staticmethod(__compile__)

	def __getSortedBlsPathList__(self, srcPath):
		if (srcPath == ''):
			print('BSScript: Source path not detected.')
		
		blsItemsMap = {}
		for root, dirs, files in os.walk(srcPath):
			for name in files:
				if name.upper().endswith('.BLS'):
					fullname = os.path.join(root, name)
					blsItem = BLSItem(fullname)
					blsItemsMap[blsItem.name] = blsItem

		isSorted = False
		sortedBlsList = []
		MAX_SORT_ATTEMPT = 100
		i = 0
		while not isSorted:
			if i >= MAX_SORT_ATTEMPT:
				print('BSScript: reached the maximum number of sort attempts for BLSList.')
				break
			for blsPath, blsItem in blsItemsMap.items():
				if blsItem.addedToCompile:
					continue				
				dependenceCount = 0
				if blsItem.dependence:
					dependenceCount = len(blsItem.dependence)
				if dependenceCount == 0:
					sortedBlsList.append(blsItem.name)
					blsItem.addedToCompile = True
					continue
				elif dependenceCount > 0:
					allowAdd = False
					for dependence in blsItem.dependence:
						if not dependence in sortedBlsList:
							break
						allowAdd = True
					if allowAdd:
						sortedBlsList.append(blsItem.name)
						blsItem.addedToCompile = True
			isSorted = len(blsItemsMap) == len(sortedBlsList)
			i = i + 1
		if isSorted:
			sortedBlsPathList = []
			for bls in sortedBlsList:
				sortedBlsPathList.append(blsItemsMap.get(bls).blsFullName)
			return sortedBlsPathList
		else:
			return None

	def __compileAll__(self, workingDir, protectServer, protectServerAlias, srcPath, destPath):
		sortedBlsPathList = self.__getSortedBlsPathList__(srcPath)
		if sortedBlsPathList == None:
			print('BSScript: BLS not sorted.')
		for blsPath in sortedBlsPathList:
			self.__compile__(workingDir, blsPath, 'exe;system;' + destPath, protectServer, protectServerAlias, true)

	compileAllBLS = staticmethod(__compileAll__)