import os
import shutil
import getpass
import sys
import fnmatch
from .Dependencer import Dependencer
from .BLSItem import BLSItem
from .BSSCompiler import BSSCompiler
from .StarTeam import StarTeam
from . import Helper

class BSSBuilder:
	BLS_LIST_FILE_NAME = 'blsList.txt'
	DLL_LIST_FILE_NAME = 'dllList.txt'
	
	PATCH_BANK_FOLDER   = 'Bank'
	PATCH_CLIENT_FOLDER = 'Client'
	PATCH_TEMP          = 'Temp'
	PATCH_OUT_COMMON    =   'Common'
	PATCH_OUT_BLS       =     'BLS'
	PATCH_OUT_USER      =     'USER'
	TEMPLATES_PATH = '.\\templates'		
	
	def __init__(self, fastMode, compilerSettings = None, starteamSettigs = None):
		self.fastMode = fastMode
		self.error = []
		self.cycles = []
		self.blsCompiled = 0
		self.compilerSettings = compilerSettings
		self.starteamSettigs = starteamSettigs

		self.patchRootPath = ''
		self.patchBankPath = ''
		self.patchClientPath = ''
		self.patchTempPath = ''
		self.patchOutCommon = ''
		self.patchOutBls = ''

	def __initPatchPaths(self, patchFolder, patchVersion):
		self.patchRootPath = os.path.join(patchFolder, patchVersion)
		if not os.path.exists(self.patchRootPath):
			os.makedirs(self.patchRootPath)	
		self.patchBankPath = os.path.join(self.patchRootPath, BSSBuilder.PATCH_BANK_FOLDER)
		self.patchClientPath = os.path.join(self.patchRootPath, BSSBuilder.PATCH_CLIENT_FOLDER)
		self.patchTempPath = os.path.join(self.patchRootPath, BSSBuilder.PATCH_TEMP)		
		self.patchOutCommon = os.path.join(self.patchTempPath, BSSBuilder.PATCH_OUT_COMMON)
		self.patchOutBls = os.path.join(self.patchOutCommon, BSSBuilder.PATCH_OUT_BLS)
		self.patchOutUser = os.path.join(self.patchOutCommon, BSSBuilder.PATCH_OUT_USER)

	def __createTargetPath(self, targetPath, clear = True):		
		if not targetPath:
			targetPath = self.workingDir + '\\user'
		if os.path.exists(targetPath):
			if clear:
				shutil.rmtree(targetPath)
				os.makedirs(targetPath)
		else:
			os.makedirs(targetPath)

	def getSortedBlsPathList(self, srcPath):
		dependencer = Dependencer(srcPath);		
		
		blsItemsMap = {}
		dublicates = []
		
		if dependencer.blsDublicates:
			self.error.append('Have dublicates: ' + str(dependencer.blsDublicates) + '.')
			return None		

		if len(dependencer.missingFiles):
			self.error.append('Files: ' + str(dependencer.missingFiles) + ' not founded in folder ' + srcPath + ', but this files uses in modules.')
			return None;		

		self.cycles = dependencer.getCycles()
		if self.cycles:
			self.error.append('Sources have cycles.')
			return None

		sortedBlsList = dependencer.getOrder();

		if sortedBlsList:
			return sortedBlsList
		else:
			self.error.append('Not sorted BLSList.')
			return None

	def getDllList(self, systemPath):
		if not systemPath:
			return None
		dllList = []
		for root, dirs, files in os.walk(systemPath):
			for name in files:
				if name.upper().endswith('.DLL'):
					dllList.append(os.path.join(root, name))
		return dllList

	def compileAllBls(self, srcPath, destPath):
		if not self.compilerSettings:
			self.error.append('No compilerSettings.')
		if len(self.error):
			return None
		blsList = []
		if not srcPath:
			srcPath = self.compilerSettings.get('srcPath', '')
		sortedBlsPathList = self.getSortedBlsPathList(srcPath);
		if not sortedBlsPathList:
			self.error.append('Not created BLS list.')
			return None
		compiler = BSSCompiler(self.compilerSettings)
		self.__createTargetPath(destPath)		
		if self.fastMode:
			if not Helper.listToFile(sortedBlsPathList, compiler.workingDir + '\\' + BSSBuilder.BLS_LIST_FILE_NAME):
				self.error.append('Not created BLS list file.')
				return None
			dllList = self.getDllList(compiler.workingDir + '\\' + 'SYSTEM')			
			if not Helper.listToFile(dllList, compiler.workingDir + '\\' + BSSBuilder.DLL_LIST_FILE_NAME):
				self.error.append('Not created DLL list file.')
				return None
			compiler.compileBlsListFileName(compiler.workingDir + '\\' + BSSBuilder.BLS_LIST_FILE_NAME, compiler.workingDir + '\\' + BSSBuilder.DLL_LIST_FILE_NAME, destPath)
		else:
			sortedBlsPathList.reverse()
			compiler.userPaths = [destPath]
			def __onCompiled(copiedBlls):				
				self.blsCompiled += 1
				if len(sortedBlsPathList) > 0:
					compiler.compile(sortedBlsPathList.pop())
				else:
					print('Compiled ' + str(self.blsCompiled) + ' bls.')
			def __onNoCompiled(compiler):
				print(blsPath + ' not compiled!')
			while sortedBlsPathList:
				blsPath = sortedBlsPathList.pop()				
				bllFullPath = Helper.getBllPathByBlsPath(blsPath, compiler.version, compiler.workingDir)
				compiler.em.connect(BSSCompiler.EVENT_BLL_COPIED, __onCompiled, compiler)
				compiler.em.connect(BSSCompiler.EVENT_NOT_COMPILED, __onNoCompiled, compiler)
				compiler.compile(blsPath)

	def getStPsw(self):
		if not self.starteamSettigs.get('stPassword', ''):			
			if sys.stdin.isatty():
				psw = getpass.getpass('StarTeam password: ')
			else:
				print('StarTeam password:')
				psw = sys.stdin.readline().rstrip()
			self.starteamSettigs.update({'stPassword': psw})

	def build(self):
		print('Develope it!!!')

	def __getBcFileList(self, blsList):
		result = []
		baseDir = os.path.join(self.patchOutCommon, 'BASE', 'CLIENT')
		if os.path.exists(baseDir):
			eifFiles = []
			eifFiles.extend(Helper.getFileLis(baseDir, '*.eif'))
			result.extend(eifFiles)
		if blsList:
			for fullFilePath in blsList:	
				if fnmatch.fnmatch(fullFilePath, '*\\?c*.bls'):
					result.append(fullFilePath)
					filePath, fileName = os.path.split(fullFilePath)
					fileName, fileExtension = os.path.splitext(fileName)
					result.append(os.path.join(self.patchOutUser, fileName) + '.bll')
					continue
				if fnmatch.fnmatch(fullFilePath, '*\\?a*.bls'):
					result.append(fullFilePath)
					filePath, fileName = os.path.split(fullFilePath)
					fileName, fileExtension = os.path.splitext(fileName)
					result.append(os.path.join(self.patchOutUser, fileName) + '.bll')
					continue
		return result

	def __getIcFileLilst(self):
		result = []

	def __copyToPatchFolder(self, fileList, patchFolder):		
		dataFolderPath = os.path.join(patchFolder, 'DATA')
		if not os.path.exists(dataFolderPath):
			os.makedirs(dataFolderPath)
		userFolderPath = os.path.join(patchFolder, 'LIBFILES', 'USER')
		if not os.path.exists(userFolderPath):
			os.makedirs(userFolderPath)
		for fullFilePath in fileList:
			fileName, fileExtension = os.path.splitext(fullFilePath)			
			fileExtension = fileExtension.lower()
			if fileExtension == '.eif':
				shutil.copy2(fullFilePath, dataFolderPath)
			elif fileExtension == '.bll':
				print(fullFilePath)
				shutil.copy2(fullFilePath, userFolderPath)


	def createPatch(self, patchFolder, patchVersion, labels):
		self.__initPatchPaths(patchFolder, patchVersion)			
		
		self.getStPsw()
		st = StarTeam(self.starteamSettigs)
		# checkoutDirs = []
		# for label in labels:
		# 	checkoutPath = os.path.join(self.patchTempPath, label)
		# 	st.checkOutByLabel(label, checkoutPath)
		# 	checkoutDirs.append(checkoutPath)
		
		checkoutDirs = ['D:\\MyPatch\\200123_RSHB_017_9_580\\Temp\\BIQ1', 'D:\\MyPatch\\200123_RSHB_017_9_580\\Temp\\BIQ2'] #temp
		Helper.mergeDirs(checkoutDirs, self.patchOutCommon)
		if os.path.exists(self.patchOutBls):
			blsList = []
			for root, dirs, files in os.walk(self.patchOutBls):
				for name in files:
					if name.upper().endswith('.BLS'):
						blsList.append(os.path.join(root, name))
			shutil.rmtree(self.patchOutBls)
			st.checkOutByFileFilter('BLS/SOURCE', '*.bls', self.patchOutBls)
			self.compileAllBls(self.patchOutBls, self.patchOutUser)

		bcFileList = self.__getBcFileList(blsList)
		if len(bcFileList) > 0:			
			self.__copyToPatchFolder(bcFileList, self.patchClientPath)
			Helper.fullCopy(os.path.join(BSSBuilder.TEMPLATES_PATH, self.compilerSettings.get('version', '')), self.patchClientPath)
		
		