# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from . import Helper

class BSSCompiler:
	BLS_LIST_FILE_NAME = 'blsList.txt'
	DLL_LIST_FILE_NAME = 'dllList.txt'

	RESULT_STR_SUCCESS = 'Compiled succesfully'
	RESULT_STR_WARNINGS = 'Compiled with warnings'

	TEMP_BLL_FOLDER_NAME = 'TempBLL'

	MSG_TYPE_SCS = 0
	MSG_TYPE_INFO = 1
	MSG_TYPE_ERR = 2

	def __init__(self, settings):
		if (settings != None):
			self.workingDir = settings.get('working_dir', '')
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.version = settings.get('version', '')
			self.userPaths = settings.get("userPaths", [])
			self.srcPath = settings.get("srcPath", '')
			if settings.get("compileAllToTempFolder", True):
				self.BLLTempDir = self.workingDir + '\\' + BSSCompiler.TEMP_BLL_FOLDER_NAME
			else:
				self.BLLTempDir = self.workingDir + '\\user'
			self.compileAllFastMode = settings.get('compileAllFastMode', True)
			self.bllVersion = settings.get('bllVersion', '')
			self.errors = []

	def compileBLS(self, blsPath, path, onAfterFinish):
		if (blsPath == ''):
			self.errors.append('No bls for compile.')
			return False		
		if (self.workingDir == '') or (self.protectServer == '') or (self.protectServerAlias == ''):
			self.errors.append('Not all settings are filled out.')			
			return False
		if path == '':
			path = 'exe;system;user'

		oldPath = os.environ['PATH']
		os.environ['PATH'] = os.path.expandvars(path)
		os.chdir(self.workingDir)
		runStr = 'bscc.exe' + ' "{}" -S{} -A{} -Tuser'.format(blsPath, self.protectServer, self.protectServerAlias)
		if self.bllVersion:
			runStr = runStr + ' -V"' + self.bllVersion + '"'
		process = subprocess.Popen(runStr, shell = True, stdout = subprocess.PIPE)			
		out, err = process.communicate()
		process.stdout.close()
		os.environ['PATH'] = oldPath
		processResultStr = out.decode('windows-1251')
		if BSSCompiler.RESULT_STR_SUCCESS not in processResultStr and \
			BSSCompiler.RESULT_STR_WARNINGS not in processResultStr:
			self.errors.append(blsPath + ' not compiled!')
			return False
		else:
			if callable(onAfterFinish):
				onAfterFinish()
			return True
	
	def compile(self, blsPath):
		bllFullPath = Helper.getBLLFullPath(blsPath, self.version, self.workingDir)
		self.compileBLS(blsPath, '', lambda: copyBllsInUserPaths(self.version, self.workingDir, self.userPaths, bllFullPath))
	
	def compileAndTest(self, blsPath):
		bllFullPath = Helper.getBLLFullPath(blsPath, self.version, self.workingDir)
		self.compileBLS(blsPath, '', lambda: [copyBllsInUserPaths(self.version, self.workingDir, self.userPaths, bllFullPath),
			runTest(self.workingDir, bllFullPath)])