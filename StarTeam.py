import sublime
import os
import re
import subprocess

class StarTeam:
	def __init__(self, projectData):
		if not projectData:
			return
		
		if not projectData.get('stCmd'):
			return
		self.stCmd = projectData['stCmd']
		
		if not projectData.get('stLogin'):
			return
		self.stLogin = projectData['stLogin']

		if not projectData.get('stPassword'):
			return
		self.stPassword = projectData['stPassword']

		if not projectData.get('stServer'):
			return
		self.stServer = projectData['stServer']

		if not projectData.get('stPort'):
			return
		self.stPort = projectData['stPort']

		if not projectData.get('stProject'):
			return
		self.stProject = projectData['stProject']

		if not projectData.get('stView'):
			return
		self.stView = projectData['stView']

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
