import sublime
import sublime_plugin
import os
from ctypes import *
from . import CommonFunctions
from . import MyExecCommand
from .BSSCompiler import BSSCompiler
from .StarTeam import StarTeam
from .Spinner import Spinner
from .BLSItem import BLSItem
from datetime import datetime

class bsscriptCompileCommand(sublime_plugin.WindowCommand):
	def run(self):
		activeWindow = sublime.active_window()
		activeWindow.active_view().settings().set('operationName', 'compile')
		activeWindow.run_command("save")

class bsscriptCompileEventListeners(sublime_plugin.EventListener):
	def on_post_save(self, view):		
		activeWindow = sublime.active_window()
		fileExt = activeWindow.extract_variables()["file_extension"].upper()
		awSettings = activeWindow.active_view().settings()
		if fileExt != 'BLS' :
			return
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBLIME)
		blsFullPath = activeWindow.extract_variables()["file"]
		if awSettings.get('operationName') == 'compileAndTest':
			exportFunctions = CommonFunctions.getExportFunctions(blsFullPath)
			if not exportFunctions:
				print('Not found ' + CommonFunctions.TEST_FUNCTION + '!')
				awSettings.set('operationName', '')
				activeWindow.active_view().set_status(CommonFunctions.SUBLIME_STATUS_LOG, 'Not found ' + CommonFunctions.TEST_FUNCTION + '!')
				return
			if exportFunctions.count(CommonFunctions.TEST_FUNCTION.lower()) == 0:
				print('Not found ' + CommonFunctions.TEST_FUNCTION + '!')
				awSettings.set('operationName', '')
				activeWindow.active_view().set_status(CommonFunctions.SUBLIME_STATUS_LOG, 'Not found ' + CommonFunctions.TEST_FUNCTION + '!')
				return
			compiler.compileAndTest(blsFullPath)			
		else:
			compiler.compile(blsFullPath)			
		awSettings.set('operationName', '')
		activeWindow.find_output_panel("exec").set_syntax_file("BSScript-compile.sublime-syntax")

class bsscriptCompileAllCommand(sublime_plugin.WindowCommand):
	def run(self):
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBPROCESS)
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
		# settings = CommonFunctions.getSettings()
		# compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBLIME)
		# blsFullPath = activeWindow.extract_variables()["file"]
		# compiler.compileAndTest(blsFullPath)		
		# activeWindow.find_output_panel("exec").set_syntax_file("BSScript-compile.sublime-syntax")

class bsscriptAddProjectSettingsCommand(sublime_plugin.WindowCommand):	
	def run(self):
		activeWindow = sublime.active_window()		
		if os.path.exists(activeWindow.project_file_name()):
			projectSettings = activeWindow.project_data()
			
			if not projectSettings.get('stCmd'):
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
			
			if not projectSettings.get('stCmd'):
				projectSettings['bscc'] = {}
			bsccSettings = projectSettings.get('bscc')
			if not bsccSettings.get('buildVersion'):
				bsccSettings['buildVersion'] = ''
			if not bsccSettings.get('bllVersion'):
				bsccSettings['bllVersion'] = ''

			activeWindow.set_project_data(projectSettings)
			sublime.message_dialog('BSScript settings added!')
		else:
			sublime.error_message('No project file. Create and save a project.')


class bsscriptCheckoutByLabelCommand(sublime_plugin.WindowCommand):	
	def run(self):		
		activeWindow = sublime.active_window()
		activeWindow.active_view().erase_status(CommonFunctions.SUBLIME_STATUS_LOG)
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
			activeView.set_status(CommonFunctions.SUBLIME_STATUS_LOG, 'StarTeam: checkout by lable ' + label + '.')
			st = StarTeam(stSettings)
			if not st.checkOutByLabel(label, checkoutPath):
				activeView.set_status(CommonFunctions.SUBLIME_STATUS_LOG, 'StarTeam: error checkout by lable ' + label + '.')
			else:
				activeView.set_status(CommonFunctions.SUBLIME_STATUS_LOG, 'StarTeam: successful checkout by lable ' + label + '.')
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

#from side bar
class bsscriptCompileFilesCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBPROCESS)
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
		sortedBlsPathList = BSSCompiler.getSortedBlsPathList(paths[0])
		if (sortedBlsPathList):			
			activeWindow = sublime.active_window()
			newView = activeWindow.new_file()
			newView.set_name('SortedBlsList')
			newView.run_command('insert', {
				'characters': str(sortedBlsPathList)
				})

#from side bar
class bsscriptCheckOnStrongDependencyCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		def doCheckOnStrongDependency():
			blsList = []		
			startTime = datetime.now()
			for path in paths:
				if os.path.isdir(path):
					for root, dirs, files in os.walk(path):
						for name in files:
							if name.upper().endswith('.BLS'):
								blsList.append(os.path.join(root, name))
				else:
					if path.upper().endswith('.BLS'):
						blsList.append(path)
			outputPanel = sublime.active_window().create_output_panel('CheckOnStrongDependency')
			outputPanel.settings().set('color_scheme', sublime.active_window().active_view().settings().get('color_scheme'))
			outputPanel.set_syntax_file('BSScript-checkOnStrongDependency.sublime-syntax')
			sublime.active_window().run_command('show_panel', {
				'panel': 'output.CheckOnStrongDependency'
				})
			if blsList:			
				count = 0
				errCount = 0
				outputPanel.run_command('insert', {
					'characters': 'Start Check On Strong Dependency.\n'
					})
				while blsList:
					count = count + 1
					blsPath = blsList.pop()
					blsItem = BLSItem(blsPath, None)
					oneResult = blsItem.checkOnStrongDependency()
					if not oneResult['result']:
						errCount = errCount + 1
						outputPanel.run_command('insert', {
							'characters': blsPath + ' has strong dependency. Info: ' + str(oneResult) + '\n'
							})
					else:
						outputPanel.run_command('insert', {
							'characters': blsPath + ' no strong dependency.' + '\n'
							})
				spentTime = datetime.now() - startTime
				if errCount > 0:
					resultStr = 'Check failed. Checked ' + str(count) + ' bls, with strong dependency ' + str(errCount) +' bls. Time spent: ' + str(spentTime)
				else:
					resultStr = 'Check completed successfully. Checked ' + str(count) + ' bls. Time spent: ' + str(spentTime)
				outputPanel.run_command('insert', {
					'characters': resultStr
					})	
			else:
				outputPanel.run_command('insert', {
					'characters': 'No bls for check.'
					})			
			
		sublime.set_timeout_async(doCheckOnStrongDependency, 0)