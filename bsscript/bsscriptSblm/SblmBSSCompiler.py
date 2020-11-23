# -*- coding: utf-8 -*-
import sublime
import os
import shutil
import subprocess
from .. import Helper
from . import SblmCmmnFnctns
from .Spinner import Spinner
from ..Dependencer import Dependencer
from ..BLSItem import BLSItem
from ..BSSCompiler import BSSCompiler
from ..BSSBuilder import BSSBuilder

def getBLLFullPath(blsFullPath, compilerVersion, workingDir):
	if blsFullPath:
		return Helper.getBllPathByBlsPath(blsFullPath, compilerVersion, workingDir)
	else:
		return SblmCmmnFnctns.getBllPathByBlsSblmWin(compilerVersion, workingDir)

def getCompilePanel():
	bssCompilePanel = sublime.active_window().find_output_panel('BssCompilePanel')
	if (bssCompilePanel == None):
		bssCompilePanel = sublime.active_window().create_output_panel('BssCompilePanel')
		bssCompilePanel.settings().set('color_scheme', sublime.active_window().active_view().settings().get('color_scheme'))
	sublime.active_window().run_command('show_panel', {
		'panel': 'output.BssCompilePanel'
		})
	bssCompilePanel.set_syntax_file("BSScript-compile.sublime-syntax")
	return bssCompilePanel;

#For default mode
def onCompileStart(compiler):
	bssCompilePanel = getCompilePanel()
	bssCompilePanel.run_command('select_all')
	bssCompilePanel.run_command('right_delete')	
	bssCompilePanel.run_command('append', {
		'characters': 'Start compile: ' + compiler.blsPath + '\n'
		})

def onAfterCompiled(compiler):
	bssCompilePanel = getCompilePanel()
	bssCompilePanel.run_command('append', {
		'characters': compiler.resultCompileStr
		})
	bssCompilePanel.run_command("move_to", {"to": "bof"})

def onBllCopied(compiler, copiedBlls):
	bssCompilePanel = getCompilePanel()
	bssCompilePanel.run_command('append', {
		'characters': 'Copied bll list: ' + str(copiedBlls) + '\n'
		})	
# end default mode

class SblmBSSCompiler:
	MODE_DEFAULT = 0
	MODE_SUBLIME = 1	
	MODE_SUBPROCESS = 2 #надо избавится

	RESULT_STR_SUCCESS = 'Compiled succesfully'
	RESULT_STR_WARNINGS = 'Compiled with warnings'

	TEMP_BLL_FOLDER_NAME = 'TempBLL'

	def __init__(self, settings, mode):
		if (settings != None):
			self.workingDir = settings.get('working_dir', '')
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.version = settings.get('version', '')
			self.userPaths = settings.get("userPaths", [])
			self.srcPath = settings.get("srcPath", '')
			if settings.get("compileAllToTempFolder", True):
				self.BLLTempDir = self.workingDir + '\\' + SblmBSSCompiler.TEMP_BLL_FOLDER_NAME
			else:
				self.BLLTempDir = self.workingDir + '\\user'			
			self.compileAllFastMode = settings.get('compileAllFastMode', True)
			self.bllVersion = settings.get('bllVersion', '')
			self.delClassInfo = settings.get('delClassInfo', False)
		self.mode = mode	
		self.errors = []

	def compileBLS(self, blsPath, path, onFinishFuncDesc):
		if (blsPath == ''):
			print('BSScript: No bls for compile.')
			return		
		if (self.workingDir == '') or (self.protectServer == '') or (self.protectServerAlias == ''):
			print('BSScript: Not all settings are filled out.')
			return
		if path == '':
			path = 'exe;system;user'

		if self.mode == SblmBSSCompiler.MODE_SUBLIME:			
			activeWindow = sublime.active_window()
			cmd = ['bscc.exe ', blsPath, '-S' + self.protectServer, '-A' + self.protectServerAlias, '-Tuser']
			if self.bllVersion:
				cmd.append('-V' + self.bllVersion)
			args = {
				'working_dir': self.workingDir,
				'encoding': 'cp1251',
				'path': path,
				'cmd': cmd,
				'quiet': True,
				'on_finished_func_desc': onFinishFuncDesc, #при использовании колбэка sublime.py выбрасывает ошибку
				'need_spinner': True
			}
			activeWindow.run_command('my_exec', args)
		elif self.mode == SblmBSSCompiler.MODE_SUBPROCESS:			
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
			if SblmBSSCompiler.RESULT_STR_SUCCESS not in processResultStr and \
				SblmBSSCompiler.RESULT_STR_WARNINGS not in processResultStr:				
				return False
			else:
				return True
		elif self.mode == SblmBSSCompiler.MODE_DEFAULT:			
			setting = {
				"working_dir": self.workingDir,
				"srcPath": self.srcPath,
				"userPaths": self.userPaths,
				"bllFullPath": getBLLFullPath(blsPath, self.version, self.workingDir),
				"version": self.version,
				"protect_server": self.protectServer,
				"protect_server_alias": self.protectServerAlias,
				"bllVersion": self.bllVersion
			}
			compiler = BSSCompiler(setting)
			print('-----------------------------')
			compiler.em.connect(BSSCompiler.EVENT_COMPILE_START, onCompileStart, compiler)
			compiler.em.connect(BSSCompiler.EVENT_COMPILED, onAfterCompiled, compiler)
			compiler.em.connect(BSSCompiler.EVENT_NOT_COMPILED, onAfterCompiled, compiler)			
			compiler.em.connect(BSSCompiler.EVENT_BLL_COPIED, onBllCopied, compiler)
			compiler.compile(blsPath)
	
	def compile(self, blsPath):
		activeView = sublime.active_window().active_view()
		activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG)
		bllFullPath = getBLLFullPath(blsPath, self.version, self.workingDir)
		fnshFnsDesc = {
			'copyBllsInUserPaths': {
				'version': self.version, 
				'workingDir' : self.workingDir, 
				'userPaths': self.userPaths,
				'bllFullPath': bllFullPath
			}
		}
		if self.delClassInfo:
			fnshFnsDesc['delClassInfoFile'] = {
				'bllFullPath': bllFullPath
			}
		self.compileBLS(blsPath, '', fnshFnsDesc);
	
	def compileAndTest(self, blsPath):
		activeView = sublime.active_window().active_view()
		activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG)
		bllFullPath = getBLLFullPath(blsPath, self.version, self.workingDir)		
		self.compileBLS(blsPath, '',
			{
				'copyBllsInUserPaths': {
					'version': self.version, 
					'workingDir' : self.workingDir, 
					'userPaths': self.userPaths,
					'bllFullPath': bllFullPath
				},
				'runTest': {
					'workingDir' : self.workingDir, 
					'bllFullPath': bllFullPath
				}
			})

	def __getStatusStr__(self, blsCount, blsCompiled, barLength):
		compiledBarLength = round(barLength * blsCompiled/blsCount)
		if blsCompiled == 0:
			return 'BSSCompiler: Compiled all bls begin.'
		elif blsCompiled == blsCount:
			return 'BSSCompiler: Compiled all bls successfully completed.'
		else:
			return 'BSSCompiler: [' + '\u2588' * compiledBarLength + '\u2591' * (barLength - compiledBarLength) + ']' + ' ' + str(blsCompiled) + '/' + str(blsCount)

	def getSortedBlsPathList(self, srcPath):
		if (srcPath == ''):
			print('BSScript: Source path not detected.')

		dependencer = Dependencer(srcPath);
		
		blsItemsMap = {}
		dublicates = []
		
		if dependencer.blsDublicates:
			print('BSScript: have dublicates: ' + str(dependencer.blsDublicates) + '.')
			return None

		if len(dependencer.missingFiles):
			print('BSScript: Files: ' + str(dependencer.missingFiles) + ' not founded in folder ' + srcPath + ', but this files uses in modules.')
			return None;
		cycles = dependencer.getCycles()
		if cycles:
			print('BSScript: sources have cycles:')
			print('\n'.join(cycles))
			return None

		sortedBlsList = dependencer.getOrder();

		if sortedBlsList:
			return sortedBlsList
		else:
			print('BSScript: Not sorted BLSList')
			return None	

	def compileAllCallBack(self, functionParams):
		path = functionParams.get('path')
		destPath = functionParams.get('destPath')
		bllFullPath = getBLLFullPath(functionParams.get('blsPath'), self.version, self.workingDir)
		Helper.copyBllsInUserPaths(self.version, self.workingDir, [destPath], bllFullPath)
		
		sortedBlsPathList = functionParams.get('sortedBlsPathList')
		if len(sortedBlsPathList) == 0:
			print('BSSCompiler: AllCompile complited.')
			return
		nextBlsPath = sortedBlsPathList.pop()
		functionParams['blsPath'] = nextBlsPath
		self.compileBLS(nextBlsPath, path,
			{'compileAllCallBack': functionParams})

	def __getDllList__(self, srcPath):
		if not srcPath:
			return None
		dllList = []
		for root, dirs, files in os.walk(srcPath):
			for name in files:
				if name.upper().endswith('.DLL'):
					dllList.append(os.path.join(root, name))
		return dllList

	def compileAll(self):				
		destPath = self.BLLTempDir;
		activeWindow = sublime.active_window()
		activeView = activeWindow.active_view()
		activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS)
		spinner = Spinner(Spinner.SYMBOLS_BOX, sublime.active_window().active_view(), 'BSScript: ', '')
		spinner.start()
		print('BSSCompiler: Compiled all bls begin.')
		sortedBlsPathList = self.getSortedBlsPathList(self.srcPath)
		if sortedBlsPathList == None:
			return
		if os.path.exists(destPath):
			shutil.rmtree(destPath)
		os.makedirs(destPath)
		blsCount = len(sortedBlsPathList)
		spinner.stop()
		if self.compileAllFastMode:
			if not Helper.listToFile(sortedBlsPathList, self.workingDir + '\\' + BSSBuilder.BLS_LIST_FILE_NAME):
				print('BSSCompiler: Not created BLS list file.')
				return
			dllList = self.__getDllList__(self.workingDir + '\\' + 'SYSTEM')
			if not Helper.listToFile(dllList, self.workingDir + '\\' + BSSBuilder.DLL_LIST_FILE_NAME):
				print('BSSCompiler: Not created DLL list file.')
				return		
			cmd = ['bscc.exe ', '-L' + self.workingDir + '\\' + BSSBuilder.BLS_LIST_FILE_NAME, '-S' + self.protectServer, '-A' + self.protectServerAlias, '-U' + destPath, '-T' + destPath, '-C' + self.workingDir + '\\' + BSSBuilder.DLL_LIST_FILE_NAME]			
			if self.bllVersion:
				cmd.append('-V' + self.bllVersion)
			args = {
				'working_dir': self.workingDir,
				'encoding': 'cp1251',
				'path': 'exe;system;' + destPath,
				'cmd': cmd,
				'quiet': True,
				'need_spinner': True,
				'on_finished_func_desc': {
					'deleteFiles': {
						'files': [self.workingDir + '\\' + BSSBuilder.BLS_LIST_FILE_NAME, self.workingDir + '\\' + BSSBuilder.DLL_LIST_FILE_NAME]
					},
					'compareCountBlsAndBLL': {
						'blsFolder': self.srcPath,
						'bllFolder': destPath
					}
				}
			}
			activeWindow.run_command('my_exec', args)			
		elif self.mode == SblmBSSCompiler.MODE_SUBLIME:
			sortedBlsPathList.reverse()
			blsPath = sortedBlsPathList.pop()
			self.compileBLS(blsPath, 'exe;system;' + destPath,
				{
					'compileAllCallBack': {
						'sortedBlsPathList': sortedBlsPathList,
						'blsPath' : blsPath,
						'path': 'exe;system;' + destPath, 
						'destPath': destPath
					}
				})
		elif self.mode == SblmBSSCompiler.MODE_SUBPROCESS:			
			spinner = Spinner(Spinner.SYMBOLS_BOX, sublime.active_window().active_view(), 'BSScript: ', '')
			spinner.start()
			blsCompiled = 0
			sortedBlsPathList.reverse()
			activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS, self.__getStatusStr__(blsCount, blsCompiled, 50))
			while sortedBlsPathList:
				blsPath = sortedBlsPathList.pop()
				bllFullPath = getBLLFullPath(blsPath, self.version, self.workingDir)
				if self.compileBLS(blsPath, '', {}):
					Helper.copyBllsInUserPaths(self.version, self.workingDir, [destPath], bllFullPath)
					blsCompiled = blsCompiled + 1
					activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS, self.__getStatusStr__(blsCount, blsCompiled, 50))
					if blsCompiled == blsCount:
						activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS)
						print('BSSCompiler: Compiled all bls successfully completed.')
				else:
					activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS)
					activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG, 'BSSCompiler: ' + blsPath + ' not compiled!')
					break
			spinner.stop()


	def compileBLSList(self, paths):	
		if self.mode != SblmBSSCompiler.MODE_SUBPROCESS:
			print('Function compileBLSList supported only for MODE_SUBPROCESS!')
			return
		if not paths:
			return
		blsList = []
		for path in paths:
			if os.path.isdir(path):
				for root, dirs, files in os.walk(path):
					for name in files:
						if name.upper().endswith('.BLS'):
							blsList.append(os.path.join(root, name))
			else:
				if path.upper().endswith('.BLS'):
					blsList.append(path)
		activeWindow = sublime.active_window()
		activeView = activeWindow.active_view()
		activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS)
		spinner = Spinner(Spinner.SYMBOLS_BOX, sublime.active_window().active_view(), 'BSScript: ', '')
		spinner.start()
		blsCompiled = 0
		blsCount = len(blsList)
		noCompiledBls = []
		activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS, self.__getStatusStr__(blsCount, blsCompiled, 50))
		destPath = self.workingDir + '\\' + SblmBSSCompiler.TEMP_BLL_FOLDER_NAME
		if not os.path.exists(destPath):
			os.makedirs(destPath)
		while blsList:
			blsPath = blsList.pop();
			bllFullPath = getBLLFullPath(blsPath, self.version, self.workingDir)
			if self.compileBLS(blsPath, '', {}):
				Helper.copyBllsInUserPaths(self.version, self.workingDir, [destPath], bllFullPath)
				blsCompiled = blsCompiled + 1				
			else:
				noCompiledBls.append(blsPath)
			activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS, self.__getStatusStr__(blsCount, blsCompiled, 50))
		activeView.erase_status(SblmCmmnFnctns.SUBLIME_STATUS_COMPILE_PROGRESS)
		if blsCompiled == blsCount:						
			print('BSSCompiler: Compiled bls list successfully completed.')
		else:
			print('BSSCompiler: Not compiled bls:' + str(noCompiledBls) + '.')
		if blsCompiled != 0:
			print('BSSCompiler: files copied in ' + self.BLLTempDir + '.')
		spinner.stop()

