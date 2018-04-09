import sublime
import sublime_plugin
import os
from ctypes import *
from . import CommonFunctions
from . import MyExecCommand
from .BSSCompiler import BSSCompiler
from .StarTeam import StarTeam
from .Spinner import Spinner

class bsscriptCompileCommand(sublime_plugin.WindowCommand):
	def run(self):
		activeWindow = sublime.active_window()
		activeWindow.run_command("save")

class bsscriptCompileEventListeners(sublime_plugin.EventListener):
	def on_post_save(self, view):
		activeWindow = sublime.active_window()
		fileExt = activeWindow.extract_variables()["file_extension"].upper()
		if fileExt != 'BLS' :
			return
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBLIME)
		blsFullPath = activeWindow.extract_variables()["file"]
		compiler.compile(blsFullPath)		
		activeWindow.find_output_panel("exec").set_syntax_file("BSScript-compile.sublime-syntax")

class bsscriptCompileAllCommand(sublime_plugin.WindowCommand):
	def run(self):
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBPROCESS)
		compiler.compileAll()

class bsscriptCompileAndTestCommand(sublime_plugin.WindowCommand):
	#not working
	def run(self):
		activeWindow = sublime.active_window()
		activeWindow.run_command("save")
		settings = CommonFunctions.getSettings()
		activeWindow.run_command("exec", {
			"working_dir": settings.get("projectPath", ""),
			"path": "exe;system;user",
			"cmd": ["execBLL.exe ", settings.get("bllFullPath", ""), "__test__execute"],
			"quiet": True
		})

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
			if not bsccSettings.get('protectServer'):
				bsccSettings['protectServer'] = ''
			if not bsccSettings.get('protectServerAlias'):
				bsccSettings['protectServerAlias'] = ''
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