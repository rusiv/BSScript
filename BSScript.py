import sublime
import sublime_plugin
import os
from ctypes import *
from datetime import datetime

from . import MyExecCommand
from .bsscript.Dependencer import Dependencer
from .bsscript.Dependencer import getDependenciesWOGraph
from .bsscript.BLSItem import BLSItem
from .bsscript.bsscriptSblm import SblmCmmnFnctns, SblmBSSCompiler, Spinner
from .bsscript import Helper, StarTeam, FnDoc, EifAssistant, Git

PACKAGES_DIR = 'packages'

def showPanel(panelName, syntax):
	outputPanel = sublime.active_window().create_output_panel(panelName)
	outputPanel.settings().set('color_scheme', sublime.active_window().active_view().settings().get('color_scheme'))
	if syntax:
		outputPanel.set_syntax_file(syntax)
	sublime.active_window().run_command('show_panel', {
		'panel': 'output.' + panelName
		})
	return outputPanel

class bsscriptViewEventListeners(sublime_plugin.EventListener):
	def on_activated(self, view):		
		fileName = view.file_name()
		if (fileName == None):
			return
		name, ext = os.path.splitext(fileName)	
		if ext.upper() != '.EIF':
			return
		assistant = EifAssistant(view)

class bsscriptCompileCommand(sublime_plugin.WindowCommand):
	def run(self):
		activeWindow = sublime.active_window()
		blsFullPath = activeWindow.extract_variables()["file"]
		settings = SblmCmmnFnctns.getSettings()
		compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_DEFAULT)		
		compiler.compile(blsFullPath)

class bsscriptCompileEventListeners(sublime_plugin.EventListener):
	def on_post_save(self, view):		
		activeWindow = sublime.active_window()
		fileExt = activeWindow.extract_variables()["file_extension"].upper()
		awSettings = activeWindow.active_view().settings()
		if fileExt != 'BLS' :
			return
		settings = SblmCmmnFnctns.getSettings()
		compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_SUBLIME)
		blsFullPath = activeWindow.extract_variables()["file"]
		if awSettings.get('operationName') == 'compileAndTest':
			exportFunctions = Helper.getExportFunctions(blsFullPath)
			if not exportFunctions:
				print('Not found ' + Helper.TEST_FUNCTION + '!')
				awSettings.set('operationName', '')
				activeWindow.active_view().set_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG, 'Not found ' + Helper.TEST_FUNCTION + '!')
				return
			if exportFunctions.count(Helper.TEST_FUNCTION.lower()) == 0:
				print('Not found ' + Helper.TEST_FUNCTION + '!')
				awSettings.set('operationName', '')
				activeWindow.active_view().set_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG, 'Not found ' + Helper.TEST_FUNCTION + '!')
				return
			compiler.compileAndTest(blsFullPath)			
		else:
			compiler.compile(blsFullPath)
		awSettings.set('operationName', '')
		activeWindow.find_output_panel("exec").set_syntax_file("BSScript-compile.sublime-syntax")

class bsscriptCompileAllCommand(sublime_plugin.WindowCommand):
	def run(self):		
		settings = SblmCmmnFnctns.getSettings()
		compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_SUBPROCESS)
		compiler.compileAll()

class bsscriptCompileAndTestCommand(sublime_plugin.WindowCommand):
	def run(self):
		activeWindow = sublime.active_window()
		activeWindow.active_view().settings().set('operationName', 'compileAndTest')
		activeWindow.run_command("save")
		# activeWindow = sublime.active_window()
		# fileExt = activeWindow.extract_variables()["file_extension"].upper()
		# if fileExt != 'BLS' :
		# 	return
		# settings = SblmCmmnFnctns.getSettings()
		# compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_SUBLIME)
		# blsFullPath = activeWindow.extract_variables()["file"]
		# compiler.compileAndTest(blsFullPath)		
		# activeWindow.find_output_panel("exec").set_syntax_file("BSScript-compile.sublime-syntax")

class bsscriptAddProjectSettingsCommand(sublime_plugin.WindowCommand):	
	def run(self):
		activeWindow = sublime.active_window()		
		if os.path.exists(activeWindow.project_file_name()):
			projectSettings = activeWindow.project_data()
			
			if not projectSettings.get('st'):
				projectSettings['st'] = {}
			stSettings = projectSettings.get('st')
			if not stSettings.get('stCmd'):
				stSettings['stCmd'] = ''
			if not stSettings.get('stLogin'):
				stSettings['stLogin'] = ''
			if not stSettings.get('stPassword'):
				stSettings['stPassword'] = ''
			if not stSettings.get('stServer'):
				stSettings['stServer'] = ''
			if not stSettings.get('stPort'):
				stSettings['stPort'] = ''
			if not stSettings.get('stProject'):
				stSettings['stProject'] = ''
			if not stSettings.get('stView'):
				stSettings['stView'] = ''
			
			if not projectSettings.get('bscc'):
				projectSettings['bscc'] = {}
			bsccSettings = projectSettings.get('bscc')
			if not bsccSettings.get('buildVersion'):
				bsccSettings['buildVersion'] = ''
			if not bsccSettings.get('bllVersion'):
				bsccSettings['bllVersion'] = ''

			if not projectSettings.get('git'):
				projectSettings['git'] = {}
			gitSettings = projectSettings.get('git')				
			if not gitSettings.get('repoPath'):
				gitSettings['repoPath'] = ''
			if not gitSettings.get('gitPath'):
				gitSettings['gitPath'] = ''

			activeWindow.set_project_data(projectSettings)
			sublime.message_dialog('BSScript settings added!')
		else:
			sublime.error_message('No project file. Createsave a project.')


class bsscriptCheckoutByLabelCommand(sublime_plugin.WindowCommand):	
	def run(self):		
		activeWindow = sublime.active_window()
		activeWindow.active_view().erase_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG)
		activeWindow.show_input_panel(
			'Enter StarTeam label name for checkout: ', 
			'', 
			lambda label: self.__checkout__(label, ''), 
			None, 
			None)

	def __checkout__(self, label, password):
		
		def asyncCheckout():
			activeView = sublime.active_window().active_view()
			spinner = Spinner(Spinner.SYMBOLS_BOX, activeWindow.active_view(), 'BSScript: ', '')
			spinner.start()
			activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG, 'StarTeam: checkout by lable ' + label + '.')
			st = StarTeam(stSettings)
			if not st.checkOutByLabel(label, checkoutPath):
				activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG, 'StarTeam: error checkout by lable ' + label + '.')
			else:
				activeView.set_status(SblmCmmnFnctns.SUBLIME_STATUS_LOG, 'StarTeam: successful checkout by lable ' + label + '.')
			spinner.stop()

		CHECKOUT_DIR_NAME = 'ST_CheckOut'
		if not label:
			return
		activeWindow = sublime.active_window()
		projectSettings = activeWindow.project_data()
		stSettings = projectSettings.get('st')
		if password: 
			stSettings['stPassword'] = password
		if not stSettings.get('stPassword'):
			activeWindow.show_input_panel(
				'Enter password for StarTeam: ', 
				'', 
				lambda psw: self.__checkout__(label, psw), 
				None, 
				None)
			return		
		checkoutPath = activeWindow.extract_variables().get("project_path") + '\\' + CHECKOUT_DIR_NAME + '\\' + label
		sublime.set_timeout_async(asyncCheckout, 0)

class bsscriptGitGetFilesSince(sublime_plugin.WindowCommand):	
	settings = sublime.active_window().project_data().get('git')	
	git = Git(settings)	

#from side bar
class bsscriptCompileFilesCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		settings = SblmCmmnFnctns.getSettings()
		compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_SUBPROCESS)
		sublime.set_timeout_async(lambda: compiler.compileBLSList(paths), 0)

#from side bar
class bsscriptSortedBlsListCommand(sublime_plugin.WindowCommand):
	def is_visible(self, paths = []):
		if (len(paths) > 1):
			return False
		if (not os.path.isdir(paths[0])):
			return False
		return True
	
	def run(self, paths = []):
		# Делать через set_timeout_async нет особого смысла, так как создается новый файл и вкладка, и основная часть времени уходит на newView.run_command 
		settings = SblmCmmnFnctns.getSettings()
		compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_SUBPROCESS)
		sortedBlsPathList = compiler.getSortedBlsPathList(paths[0])
		if (sortedBlsPathList):			
			activeWindow = sublime.active_window()
			newView = activeWindow.new_file()
			newView.set_name('SortedBlsList')
			newView.run_command('insert', {
				'characters': str(sortedBlsPathList)
				})


#from side bar
class bsscriptCheckOnStrongDependencyCommand(sublime_plugin.WindowCommand):
	def is_visible(self, paths = []):
		if (len(paths) > 1):
			return False
		if (not os.path.isdir(paths[0])):
			return False
		return True
	def run(self, paths = []):
		def doCheckOnStrongDependency():
			def onBlsChecked(vertex):				
				if len(vertex.cycles) > 0:
					outputPanel.run_command('insert', {
						'characters': vertex.fullPath + ' has strong dependency. Info: ' + str(vertex.cycles) + '\n'
						})
				else:
					outputPanel.run_command('insert', {
						'characters': vertex.fullPath + ' no strong dependency.' + '\n'
						})			
			
			startTime = datetime.now()
			for path in paths:
				dependencer = Dependencer(path, onBlsChecked);		
				dublicates = []
				
				if dependencer.blsDublicates:
					outputPanel.run_command('insert', {
						'characters': 'Has dublicate bls in folder ' + path + ', dublicates: ' + str(dependencer.blsDublicates) + '.'
						})
					return

				if len(dependencer.missingFiles):
					outputPanel.run_command('insert', {
						'characters': 'Files: ' + str(dependencer.missingFiles) + ' not founded in folder ' + path + ', but this files uses in modules.'
						})
					return

				outputPanel.run_command('insert', {
					'characters': 'Start Check On Strong Dependency.\n'
					})

				cycles = dependencer.getCycles()
				checkedBlsCount = len(dependencer.graph.vertexes)
				blsWithCycles = len(cycles)
				spentTime = datetime.now() - startTime
				if checkedBlsCount == 0:
					outputPanel.run_command('insert', {
						'characters': 'No bls for check.'
						})
					return
				if blsWithCycles > 0:
					outputPanel.run_command('insert', {
						'characters': 'Check failed. Checked ' + str(checkedBlsCount) + ' bls, with strong dependency ' + str(blsWithCycles) +' bls. Time spent: ' + str(spentTime)
						})
				else:
					outputPanel.run_command('insert', {
						'characters': 'Check completed successfully. Checked ' + str(checkedBlsCount) + ' bls. Time spent: ' + str(spentTime)
						})

		outputPanel = showPanel('CheckOnStrongDependency', 'BSScript-checkOnStrongDependency.sublime-syntax')
		sublime.set_timeout_async(doCheckOnStrongDependency, 0)

#from side bar
class bsscriptGetDependencyListCommand(sublime_plugin.WindowCommand):
	def is_visible(self, paths = []):
		if (len(paths) > 1):
			return False
		if (not os.path.isfile(paths[0])):
			return False
		fileName, fileExtension = os.path.splitext(paths[0])
		if (fileExtension.lower() != '.bls'):
			return False
		return True
	def run(self, paths = []):
		useGrpah = True #если граф не сходится, то выставить в false
		err = ''		
		checkedBlsPath = paths[0]
		srcDir = Helper.getWorkingDirForFile(checkedBlsPath) + '\\SOURCE'		

		outputPanel = showPanel('DependencyList', None)
		outputPanel.run_command('insert', {
			'characters': 'Start geting dependency list for ' + checkedBlsPath + '. Sorce path: ' + srcDir + '. UseGrpah = ' + str(useGrpah) + '.'
			})

		if useGrpah:			
			dependencer = Dependencer(srcDir);
			vertex = dependencer.getVertexByPath(checkedBlsPath);			
			dependencer.dfs(vertex);
			if (len(dependencer.cycles) > 0):
				err = 'Graph has cycles: ' + str(dependencer.cycles)
			else:
				sortedList = dependencer.compileOrder				
				sortedList.pop() #последняя заивисимость это проверяемый модуль
				dependencies = []				
				for blsFullName in sortedList:
					fileName, fileExtension = os.path.splitext(blsFullName)
					dependencies.append(fileName + fileExtension)
		else:
			try:
				dependencies = getDependenciesWOGraph(checkedBlsPath)
			except Exception as e:
				err = str(e)

		msg = ''
		if err:
			msg = err
		else:
			l = len(dependencies)
			if l <= 0:
				msg = 'No dependency.'
			else:
				msg = str(dependencies)

		outputPanel.run_command('insert', {
			'characters': '\n' + msg
			})

#from side bar
class bsscriptGetFolderDependencyCommand(sublime_plugin.WindowCommand):
	def is_visible(self, paths = []):
		if (len(paths) > 1):
			return False
		if (not os.path.isdir(paths[0])):
			return False
		return True
	
	def run(self, paths = []):		
		checkedPath = paths[0].lower()
		srcDir = Helper.getWorkingDirForFile(checkedPath) + '\\SOURCE'
		srcDir = srcDir.lower()
		dependencer = Dependencer(srcDir)
		dependencyFolders = [];
		err = ''
		outputPanel = showPanel('FolderDependency', None)
		outputPanel.run_command('insert', {
			'characters': 'Start geting folder dependency for ' + checkedPath + '. Sorce path: ' + srcDir + '.'
			})
		for root, dirs, files in os.walk(checkedPath):
			if err != '':
				break;
			for file in files:
				blsFullPath = os.path.join(root, file)				
				vertex = dependencer.getVertexByPath(blsFullPath);
				dependencer.dfs(vertex);
				if (len(dependencer.cycles) > 0):
					err = 'Graph has cycles: ' + str(dependencer.cycles)
					break
				else:								
					sortedList = dependencer.compileOrder				
					sortedList.pop() #последняя заивисимость это проверяемый модуль					
					for blsFullName in sortedList:						
						dir = os.path.dirname(blsFullName);
						if dir == checkedPath:
							continue
						if (dependencyFolders.count(dir) == 0):
							dependencyFolders.append(dir)
		msg = ''
		if err:
			msg = err
		else:
			l = len(dependencyFolders)
			if l <= 0:
				msg = 'No dependency.'
			else:
				for folder in dependencyFolders:
					if msg != '':
						msg = msg + ';'
					msg = msg + folder.lower().replace(srcDir, '').replace('\\', '/')
		outputPanel.run_command('insert', {
			'characters': '\n' + msg
			})

#from side bar
class bsscriptGetFolderDependencyOneCommand(sublime_plugin.WindowCommand):
	def is_visible(self, paths = []):
		if (len(paths) > 1):
			return False
		if (not os.path.isdir(paths[0])):
			return False
		return True
	
	def run(self, paths = []):		
		settings = sublime.load_settings('BSScript.sublime-settings')
		noPackages = settings.get('folder_dependency_no_packages', False)
		checkedPath = paths[0].lower()	
		srcDir = Helper.getWorkingDirForFile(checkedPath) + '\\SOURCE'
		srcDir = srcDir.lower()		
		dependencyFolders = [];		
		outputPanel = showPanel('FolderDependency1', None)
		outputPanel.run_command('insert', {
			'characters': 'Start geting folder dependency for ' + checkedPath + '. Sorce path: ' + srcDir + '.'
			})
		for root, dirs, files in os.walk(checkedPath):
			for file in files:
				blsFullPath = os.path.join(root, file)				
				blsDependencies = BLSItem(blsFullPath, srcDir).dependence
				if not blsDependencies:
					continue
				for dependency in blsDependencies:
					blsFullName = Helper.getFirstFullBlsName(dependency, srcDir)					
					dir = os.path.dirname(blsFullName).lower();					
					if dir == checkedPath:
						continue					
					if noPackages and dir.find(PACKAGES_DIR) > -1:
						continue
					if (dependencyFolders.count(dir) == 0):
						dependencyFolders.append(dir)		
		msg = ''
		if len(dependencyFolders) <= 0:
			msg = 'No dependency.'
		else:
			for folder in dependencyFolders:
				if msg != '':
					msg = msg + ';'
				msg = msg + folder.lower().replace(srcDir, '').replace('\\', '/')
		outputPanel.run_command('insert', {
			'characters': '\n' + msg
			})

class bsscriptAddFnDoc(sublime_plugin.WindowCommand):
	def run(self):		
		view = sublime.active_window().active_view()
		if view.settings().get('syntax').lower().find('bsscript') == -1:
			return False		
		fnDoc = FnDoc(view)
		fnDoc.makeBelowDescription()		