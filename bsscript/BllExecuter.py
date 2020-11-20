# -*- coding: utf-8 -*-
import os
import subprocess

class BllExecuter:
	SHOW_LOGIN = str.encode('ShowLoginWindow')
	SHOW_LOGIN_OFF = str.encode('ShowLoginWindow =0\r\n')	

	def __init__(self, workingDir, bllFullPath):
		self.workingDir = workingDir
		self.exeDir = self.workingDir + '\\exe\\'
		self.bllFullPath = bllFullPath		
		self.errors = []
		self.log = []
		self.appFileName = 'execBLL.exe'
		self.cfgFileName = 'execbll.cfg'
		self.defCfgFileName = 'default.cfg'	
		self.inited = False
		
		if not os.path.exists(self.exeDir + self.appFileName):
			self.errors.append(self.exeDir + self.appFileName + ' not found!')
		else:
			self.inited = True
			if not os.path.exists(self.exeDir + self.cfgFileName):
				self.log.append(self.cfgFileName + ' not found!')
				if not createExecBllCfg(workingDir):
					self.inited = False
					self.errors.append('Not created ' + self.cfgFileName + '.')					
				else:
					self.log.append(self.cfgFileName + ' successfully created!')					
	
	def __createExecBllCfg(self):
		result = False
		if not os.path.exists(self.exeDir + self.defCfgFileName):
			self.errors.append("Can't created " + self.cfgFileName + " because " + self.defCfgFileName + " not found.")
			return result
		fDefCfg = open(self.exeDir + self.defCfgFileName, 'rb')
		fExecCfg = open(self.exeDir + self.cfgFileName, 'wb')
		try:
			for line in fDefCfg:
				if line.find(BllExecuter.SHOW_LOGIN) > -1:
					line = BllExecuter.SHOW_LOGIN_OFF
				fExecCfg.write(line)			
			result = True
		finally:
			fDefCfg.close()
			fExecCfg.close()
			return result

	def execFunction(self, functionName):
		if not self.inited:
			return False
		self.log.append('Exec ' + functionName + ' from ' + self.bllFullPath + '.');
		oldPath = os.environ['PATH']
		os.environ['PATH'] = os.path.expandvars('exe;system;user')
		os.chdir(self.workingDir)
		runStr = 'execBLL.exe ' + self.bllFullPath + ' ' + functionName
		process = subprocess.Popen(runStr, shell = True, stdout = subprocess.PIPE)			
		out, err = process.communicate()
		process.stdout.close()
		os.environ['PATH'] = oldPath
		self.log.append('End exec ' + functionName + ' from ' + self.bllFullPath + '.');
		return True