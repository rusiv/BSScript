import sublime
import os
import re
import subprocess

class StarTeam:
	def __init__(self, stSettings):
		if not stSettings:
			return
			
		if not stSettings.get('stCmd'):
			return
		self.stCmd = stSettings['stCmd']
		
		if not stSettings.get('stLogin'):
			return
		self.stLogin = stSettings['stLogin']

		if not stSettings.get('stPassword'):
			return
		self.stPassword = stSettings['stPassword']

		if not stSettings.get('stServer'):
			return
		self.stServer = stSettings['stServer']

		if not stSettings.get('stPort'):
			return
		self.stPort = stSettings['stPort']

		if not stSettings.get('stProject'):
			return
		self.stProject = stSettings['stProject']

		if not stSettings.get('stView'):
			return
		self.stView = stSettings['stView']

		loginStr = self.stLogin + ':' + self.stPassword + '@' + self.stServer + ':' + self.stPort + '/' + self.stProject + '/' + self.stView
		self.runStrPrefix = '"' + self.stCmd + '"' + ' co -nologo -stop -q -x -o -is' + ' -p "' + loginStr + '"'

	def checkOutByLabel(self, label = '' , checkOutPath = ''):
		if (not label) or (not checkOutPath):
			return
		if not os.path.exists(checkOutPath):
			os.makedirs(checkOutPath)
		runStr = self.runStrPrefix + ' -rp "' + checkOutPath + '"' + ' -vl "' + label + '"'		
		process = subprocess.Popen(runStr, shell = True, stderr = subprocess.PIPE)
		out, err = process.communicate()
		process.stderr.close()
		errStr = err.decode('windows-1251')
		if (errStr != ''):
			print('BSScript: StarTeam checkout error: ' + errStr)
		return errStr == ''
