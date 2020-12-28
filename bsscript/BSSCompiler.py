# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import codecs
from . import Helper
from .Events import Event, EventManager
from .BllExecuter import BllExecuter

class BSSCompiler:
	RESULT_STR_SUCCESS = 'Compiled succesfully'
	RESULT_STR_WARNINGS = 'Compiled with warnings'

	MSG_TYPE_SCS = 0
	MSG_TYPE_INFO = 1
	MSG_TYPE_ERR = 2

	EVENT_COMPILE_START = 'compile_start'
	EVENT_COMPILED = 'compiled'
	EVENT_NOT_COMPILED = 'not_compiled'
	EVENT_BLL_COPIED = 'bll_copied'
	EVENT_START_TEST = 'start_test'
	EVENT_END_TEST = 'start_test'

	TEST_FUNCTION = '__test__execute'

	def __init__(self, settings):
		if (settings != None):
			self.workingDir = settings.get('working_dir', '')
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.version = settings.get('version', '')
			self.userPaths = settings.get("userPaths", [])
			self.srcPath = settings.get("srcPath", '')
			self.bllVersion = settings.get('bllVersion', '')		
		self.resultCompileStr = ''
		self.errors = []
		self.em = EventManager()
		self.em.add_event(Event(BSSCompiler.EVENT_COMPILE_START))
		self.em.add_event(Event(BSSCompiler.EVENT_COMPILED))
		self.em.add_event(Event(BSSCompiler.EVENT_NOT_COMPILED))
		self.em.add_event(Event(BSSCompiler.EVENT_BLL_COPIED))
		self.em.add_event(Event(BSSCompiler.EVENT_START_TEST))
		self.em.add_event(Event(BSSCompiler.EVENT_END_TEST))
		self.blsPath = ''

	def __compileBLS(self, path = 'exe;system;user'):
		if (self.blsPath == ''):
			self.errors.append('No bls for compile.')
			self.em.signal(BSSCompiler.EVENT_NOT_COMPILED)
			return False		
		if (self.workingDir == '') or (self.protectServer == '') or (self.protectServerAlias == ''):
			self.errors.append('Not all settings are filled out.')	
			self.em.signal(BSSCompiler.EVENT_NOT_COMPILED)
			return False
		self.em.signal(BSSCompiler.EVENT_COMPILE_START)
		oldPath = os.environ['PATH']
		os.environ['PATH'] = os.path.expandvars(path)
		os.chdir(self.workingDir)
		runStr = 'bscc.exe' + ' "{}" -S{} -A{} -Tuser'.format(self.blsPath, self.protectServer, self.protectServerAlias)
		if self.bllVersion:
			runStr = runStr + ' -V"' + self.bllVersion + '"'
		process = subprocess.Popen(runStr, shell = True, stdout = subprocess.PIPE)		
		out, err = process.communicate()
		process.stdout.close()
		os.environ['PATH'] = oldPath
		out = out.replace(b'\x0d', b'')
		# decoder = codecs.getdecoder('utf-8')
		# self.resultCompileStr = decoder(out)[0]
		self.resultCompileStr = out.decode('utf-8', 'ignore')
		if BSSCompiler.RESULT_STR_SUCCESS not in self.resultCompileStr and \
			BSSCompiler.RESULT_STR_WARNINGS not in self.resultCompileStr:
			self.em.signal(BSSCompiler.EVENT_NOT_COMPILED)
			return False
		else:			
			self.em.signal(BSSCompiler.EVENT_COMPILED)
			return True
	
	def __copyBllsInUserPaths(self, bllFullPath):		
		copiedBlls = Helper.copyBllsInUserPaths(self.version, self.workingDir, self.userPaths, bllFullPath)
		self.em.signal(BSSCompiler.EVENT_BLL_COPIED, copiedBlls)

	def __runTest(self, bllFullPath):
		executer = BllExecuter(self.workingDir, bllFullPath)
		if len(executer.errors) > 0:
			for error in executer.errors:
				self.errors.append(error)
			return
		self.em.signal(BSSCompiler.EVENT_START_TEST)
		if executer.execFunction(BSSCompiler.TEST_FUNCTION):
			self.em.signal(BSSCompiler.EVENT_END_TEST)

	def compile(self, blsPath):
		bllFullPath = Helper.getBllPathByBlsPath(blsPath, self.version, self.workingDir)
		self.blsPath = blsPath
		if self.__compileBLS():
			self.__copyBllsInUserPaths(bllFullPath)
	
	def compileAndTest(self, blsPath):
		bllFullPath = Helper.getBllPathByBlsPath(blsPath, self.version, self.workingDir)
		self.blsPath = blsPath
		if self.__compileBLS():
			self.__copyBllsInUserPaths(bllFullPath)
			self.__runTest(bllFullPath)

	def compileBlsListFileName(self, blsListFileName, dllListFileName, targetPath):
		if not os.path.exists(blsListFileName):
			self.errors.append('File with sortedBlsList ' + blsListFileName + ' does not exists.')
			return
		if not os.path.exists(dllListFileName):
			self.errors.append('File with dllList ' + dllListFileName + ' does not exists.')
			return		
		oldPath = os.environ['PATH']
		path = 'exe;system;user'
		os.environ['PATH'] = os.path.expandvars(path)
		os.chdir(self.workingDir)
		runStr = 'bscc.exe' + ' -L"{}" -S{} -A{} -U"{}" -T"{}" -C"{}"'.format(blsListFileName, self.protectServer, self.protectServerAlias, targetPath, targetPath, dllListFileName)		
		if self.bllVersion:
			runStr = runStr + ' -V"' + self.bllVersion + '"'		
		process = subprocess.Popen(runStr, shell = True, stdout = subprocess.PIPE)		
		out, err = process.communicate()
		process.stdout.close()
		os.environ['PATH'] = oldPath
		out = out.replace(b'\x0d', b'')