import sublime
import os
import shutil
import subprocess
from .BLSItem import BLSItem
from . import CommonFunctions

class BSSCompiler:
	MODE_SUBLIME = 0
	MODE_SUBPROCESS = 1

	RESULT_STR_SUCCESS = 'Compiled succesfully'
	RESULT_STR_WARNINGS = 'Compiled with warnings'
	STATUS_COMPILE_PROGRESS = 'compileProgress'
	STATUS_LOG = 'log'

	def __init__(self, settings, mode):
		if (settings != None):
			self.workingDir = settings.get('working_dir', '')
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.version = settings.get('version', '')
			self.userPaths = settings.get("userPaths", [])
			self.srcPath = settings.get("srcPath", '')
			self.BLLTempDir = self.workingDir + '\\TempBLL'
			self.mode = mode

	@staticmethod
	def compileBLS(workingDir, blsPath, path, protectServer, protectServerAlias, onFinishFuncDesc, mode):
		sublime.active_window().active_view().erase_status(BSSCompiler.STATUS_LOG)
		if (blsPath == ''):
			print('BSScript: No bls for compile.')
			return		
		if (workingDir == '') or (protectServer == '') or (protectServerAlias == ''):
			print('BSScript: Not all settings are filled out.')
			return
		if path == '':
			path = 'exe;system;user'

		if mode == BSSCompiler.MODE_SUBLIME:
			activeWindow = sublime.active_window()
			args = {
				'working_dir': workingDir,
				'encoding': 'cp1251',
				'path': path,
				'cmd': ['bscc.exe ', blsPath, '-S' + protectServer, '-A' + protectServerAlias, '-Tuser'],
				'file_regex': 'Program\\s(.*)\\s*.*\\s*.*line is (\\d*)',
				'quiet': True,
				'on_finished_func_desc': onFinishFuncDesc #при использовании колбэка sublime.py выбрасывает ошибку
			}
			activeWindow.run_command('my_exec', args)
		elif mode == BSSCompiler.MODE_SUBPROCESS:
			oldPath = os.environ['PATH']
			os.environ['PATH'] = os.path.expandvars(path)
			os.chdir(workingDir)
			runStr = 'bscc.exe' + ' "{}" -S{} -A{} -Tuser'.format(blsPath, protectServer, protectServerAlias)
			process = subprocess.Popen(runStr, shell = True, stdout = subprocess.PIPE)
			out, err = process.communicate()
			process.stdout.close()
			os.environ['PATH'] = oldPath
			processResultStr = out.decode('windows-1251')
			if BSSCompiler.RESULT_STR_SUCCESS not in processResultStr and \
				BSSCompiler.RESULT_STR_WARNINGS not in processResultStr:
				print('BSScript: ' + blsPath + ' not compiled!')
				return False
			else:
				return True


	def compile(self, blsPath):
		bllFullPath = CommonFunctions.getBLLFullPath(blsPath, self.version, self.workingDir)
		BSSCompiler.compileBLS(self.workingDir, blsPath, '', self.protectServer, self.protectServerAlias, 
			{
				'copyBllsInUserPaths': {
					'version': self.version, 
					'workingDir' : self.workingDir, 
					'userPaths': self.userPaths,
					'bllFullPath': bllFullPath
				}
			}, 
			self.mode)

	@staticmethod
	def __getSortedBlsPathList__(srcPath):
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
	
	@staticmethod
	def compileAllCallBack(functionParams):
		workingDir = functionParams.get('workingDir')
		path = functionParams.get('path')
		protectServer = functionParams.get('protectServer')
		protectServerAlias = functionParams.get('protectServerAlias')
		destPath = functionParams.get('destPath')
		version = functionParams.get('version')
		bllFullPath = CommonFunctions.getBLLFullPath(functionParams.get('blsPath'), version, workingDir)
		CommonFunctions.copyBllsInUserPaths({
			'version': version, 
			'workingDir' : workingDir, 
			'userPaths': [destPath], 
			'bllFullPath': bllFullPath
		})
		
		sortedBlsPathList = functionParams.get('sortedBlsPathList')
		if len(sortedBlsPathList) == 0:
			print('AllCompile complited')
			return
		nextBlsPath = sortedBlsPathList.pop()
		functionParams['blsPath'] = nextBlsPath
		BSSCompiler.compileBLS(workingDir, nextBlsPath, path, protectServer, protectServerAlias, 
			{'compileAllCallBack': functionParams}, BSSCompiler.MODE_SUBLIME)

	@staticmethod
	def compileAllBLS(version, workingDir, protectServer, protectServerAlias, srcPath, destPath, mode):		
		activeView = sublime.active_window().active_view()
		activeView.erase_status(BSSCompiler.STATUS_COMPILE_PROGRESS)
		sortedBlsPathList = BSSCompiler.__getSortedBlsPathList__(srcPath)
		if sortedBlsPathList == None:
			print('BSScript: BLS not sorted.')
		sortedBlsPathList.reverse()
		blsCount = len(sortedBlsPathList)
		if mode == BSSCompiler.MODE_SUBLIME:
			blsPath = sortedBlsPathList.pop()
			BSSCompiler.compileBLS(workingDir, blsPath, 'exe;system;' + destPath, protectServer, protectServerAlias, 
				{
					'compileAllCallBack': {
						'workingDir': workingDir, 
						'sortedBlsPathList': sortedBlsPathList,
						'blsPath' : blsPath,
						'path': 'exe;system;' + destPath, 
						'protectServer': protectServer, 
						'protectServerAlias': protectServerAlias,
						'destPath': destPath,
						'version': version
					}
				},
				mode)
		elif mode == BSSCompiler.MODE_SUBPROCESS:
			def getStatusStr(blsCount, blsCompiled, barLength):
				compiledBarLength = round(barLength * blsCompiled/blsCount)
				if blsCompiled == 0:
					return 'BSSCompiler: Compiled all bls begin.'
				elif blsCompiled == blsCount:
					return 'BSSCompiler: Compiled all bls successfully completed.'
				else:
					return 'BSSCompiler: [' + '\u2588' * compiledBarLength + '\u2591' * (barLength - compiledBarLength) + ']' + ' ' + str(blsCompiled) + '/' + str(blsCount)
			
			blsCompiled = 0			
			print('BSSCompiler: Compiled all bls begin.')
			activeView.set_status(BSSCompiler.STATUS_COMPILE_PROGRESS, getStatusStr(blsCount, blsCompiled, 50))
			while sortedBlsPathList:
				blsPath = sortedBlsPathList.pop()
				bllFullPath = CommonFunctions.getBLLFullPath(blsPath, version, workingDir)
				if BSSCompiler.compileBLS(workingDir, blsPath, '', protectServer, protectServerAlias, {}, mode):
					CommonFunctions.copyBllsInUserPaths({
						'version': version, 
						'workingDir' : workingDir, 
						'userPaths': [destPath], 
						'bllFullPath': bllFullPath
					})
					blsCompiled = blsCompiled + 1
					activeView.set_status(BSSCompiler.STATUS_COMPILE_PROGRESS, getStatusStr(blsCount, blsCompiled, 50))
					if blsCompiled == blsCount:
						activeView.erase_status(BSSCompiler.STATUS_COMPILE_PROGRESS)
						print('BSSCompiler: Compiled all bls successfully completed.')
				else:
					activeView.erase_status(BSSCompiler.STATUS_COMPILE_PROGRESS)
					activeView.set_status(BSSCompiler.STATUS_LOG, 'BSSCompiler: ' + blsPath + ' not compiled!')

	def compileAll(self):
		if os.path.exists(self.BLLTempDir):
			shutil.rmtree(self.BLLTempDir)
		os.makedirs(self.BLLTempDir)
		BSSCompiler.compileAllBLS(self.version, self.workingDir, self.protectServer, self.protectServerAlias, self.srcPath, self.BLLTempDir, self.mode)