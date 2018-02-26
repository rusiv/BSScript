import sublime
import os
import shutil
import subprocess
from .BLSItem import BLSItem
from . import CommonFunctions
from .Spinner import Spinner

class BSSCompiler:
	MODE_SUBLIME = 0
	MODE_SUBPROCESS = 1

	BLS_LIST_FILE_NAME = 'blsList.txt'
	DLL_LIST_FILE_NAME = 'dllList.txt'

	RESULT_STR_SUCCESS = 'Compiled succesfully'
	RESULT_STR_WARNINGS = 'Compiled with warnings'

	def __init__(self, settings, mode):
		if (settings != None):
			self.workingDir = settings.get('working_dir', '')
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.version = settings.get('version', '')
			self.userPaths = settings.get("userPaths", [])
			self.srcPath = settings.get("srcPath", '')
			if  settings.get("compileAllToTempFolder", True):
				self.BLLTempDir = self.workingDir + '\\TempBLL'
			else:
				self.BLLTempDir = self.workingDir + '\\user'
			self.mode = mode
			self.compileAllFastMode = settings.get('compileAllFastMode', True)

	@staticmethod
	def compileBLS(workingDir, blsPath, path, protectServer, protectServerAlias, onFinishFuncDesc, mode):
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
				'quiet': True,
				'on_finished_func_desc': onFinishFuncDesc, #при использовании колбэка sublime.py выбрасывает ошибку
				'need_spinner': True
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
		activeView = sublime.active_window().active_view()
		activeView.erase_status(CommonFunctions.SUBLIME_STATUS_LOG)
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
		dublicates = []
		count = 0
		for root, dirs, files in os.walk(srcPath):
			for name in files:
				if name.upper().endswith('.BLS'):
					fullname = os.path.join(root, name)
					blsItem = BLSItem(fullname)
					if blsItemsMap.get(blsItem.name):
						dublicates.append(blsItem.name)
					blsItemsMap[blsItem.name] = blsItem
		if dublicates:
			print('BSScript: ' + blsItem.name + ' have dublicates: ' + str(dublicates) + '.')
			return None
		isSorted = False
		sortedBlsList = []
		MAX_SORT_ATTEMPT = 100
		i = 0	
		while not isSorted:
			if i >= MAX_SORT_ATTEMPT:
				print('BSScript: reached the maximum number of sort attempts for BLSList.')
				break
			for blsPath, blsItem in blsItemsMap.items():
				blsName = blsItem.name
				if blsItem.addedToCompile:
					continue
				if not blsItem.dependence:
					sortedBlsList.append(blsName)
					blsItem.addedToCompile = True
				else:
					# allowAdd = False					
					# for dependence in blsItem.dependence:
					# 	if not (dependence in sortedBlsList):
					# 		break
					# 	allowAdd = True
					
					allowAdd = True
					for dependence in blsItem.dependence:
						if (dependence in sortedBlsList):
							allowAdd = True
						else:
							allowAdd = False
							break

					if allowAdd:
						sortedBlsList.append(blsName)
						blsItem.addedToCompile = True
			isSorted = len(blsItemsMap) == len(sortedBlsList)
			i = i + 1		
		
		if isSorted:
			sortedBlsPathList = []
			for bls in sortedBlsList:
				sortedBlsPathList.append(blsItemsMap.get(bls).blsFullName)
			return sortedBlsPathList
		else:
			print('BSScript: Not sorted BLSList, last BLS ' + blsName)
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
			print('BSSCompiler: AllCompile complited.')
			return
		nextBlsPath = sortedBlsPathList.pop()
		functionParams['blsPath'] = nextBlsPath
		BSSCompiler.compileBLS(workingDir, nextBlsPath, path, protectServer, protectServerAlias, 
			{'compileAllCallBack': functionParams}, BSSCompiler.MODE_SUBLIME)

	@staticmethod
	def __getDllList__(srcPath):
		if not srcPath:
			return None
		dllList = []
		for root, dirs, files in os.walk(srcPath):
			for name in files:
				if name.upper().endswith('.DLL'):
					dllList.append(os.path.join(root, name))					
		return dllList

	@staticmethod
	def compileAllBLS(version, workingDir, protectServer, protectServerAlias, srcPath, destPath, mode, fastMode):		
		activeWindow = sublime.active_window()
		activeView = activeWindow.active_view()
		activeView.erase_status(CommonFunctions.SUBLIME_STATUS_COMPILE_PROGRESS)
		spinner = Spinner(Spinner.SYMBOLS_SQUARE, sublime.active_window().active_view(), 'BSScript: ', '')
		spinner.start()
		print('BSSCompiler: Compiled all bls begin.')
		sortedBlsPathList = BSSCompiler.__getSortedBlsPathList__(srcPath)
		if sortedBlsPathList == None:
			return
		if os.path.exists(destPath):
			shutil.rmtree(destPath)
		os.makedirs(destPath)
		blsCount = len(sortedBlsPathList)
		spinner.stop()
		if fastMode:
			if not CommonFunctions.listToFile(sortedBlsPathList, workingDir + '\\' + BSSCompiler.BLS_LIST_FILE_NAME):
				print('BSSCompiler: Not created BLS list file.')
				return
			dllList = BSSCompiler.__getDllList__(workingDir + '\\' + 'SYSTEM')
			if not CommonFunctions.listToFile(dllList, workingDir + '\\' + BSSCompiler.DLL_LIST_FILE_NAME):
				print('BSSCompiler: Not created DLL list file.')
				return		
			args = {
				'working_dir': workingDir,
				'encoding': 'cp1251',
				'path': 'exe;system;' + destPath,
				'cmd': ['bscc.exe ', '-L' + workingDir + '\\' + BSSCompiler.BLS_LIST_FILE_NAME, '-S' + protectServer, '-A' + protectServerAlias, '-U' + destPath, '-T' + destPath, '-C' + workingDir + '\\' + BSSCompiler.DLL_LIST_FILE_NAME],
				'quiet': True,
				'need_spinner': True,
				'on_finished_func_desc': {
					'deleteFiles': {
						'files': [workingDir + '\\' + BSSCompiler.BLS_LIST_FILE_NAME, workingDir + '\\' + BSSCompiler.DLL_LIST_FILE_NAME]
					},
					'compareCountBlsAndBLL': {
						'blsFolder': srcPath,
						'bllFolder': destPath
					}
				}
			}
			activeWindow.run_command('my_exec', args)			
		elif mode == BSSCompiler.MODE_SUBLIME:
			sortedBlsPathList.reverse()
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
			
			spinner = Spinner(Spinner.SYMBOLS_SQUARE, sublime.active_window().active_view(), 'BSScript: ', '')
			spinner.start()
			blsCompiled = 0
			sortedBlsPathList.reverse()
			activeView.set_status(CommonFunctions.SUBLIME_STATUS_COMPILE_PROGRESS, getStatusStr(blsCount, blsCompiled, 50))
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
					activeView.set_status(CommonFunctions.SUBLIME_STATUS_COMPILE_PROGRESS, getStatusStr(blsCount, blsCompiled, 50))
					if blsCompiled == blsCount:
						activeView.erase_status(CommonFunctions.SUBLIME_STATUS_COMPILE_PROGRESS)
						print('BSSCompiler: Compiled all bls successfully completed.')
				else:
					activeView.erase_status(CommonFunctions.SUBLIME_STATUS_COMPILE_PROGRESS)
					activeView.set_status(CommonFunctions.SUBLIME_STATUS_LOG, 'BSSCompiler: ' + blsPath + ' not compiled!')
					break
			spinner.stop()
		
	def compileAll(self):
		BSSCompiler.compileAllBLS(self.version, self.workingDir, self.protectServer, self.protectServerAlias, self.srcPath, self.BLLTempDir, self.mode, self.compileAllFastMode)