import sublime
import sublime_plugin
import os
from ctypes import *
from . import CommonFunctions
from . import MyExecCommand
from .BSSCompiler import BSSCompiler

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
		compiler = BSSCompiler(settings)
		blsFullPath = activeWindow.extract_variables()["file"]
		compiler.compile(blsFullPath)
		activeWindow.find_output_panel("exec").set_syntax_file("BSScript-build.sublime-syntax")		

class bsscriptCompileAllCommand(sublime_plugin.WindowCommand):
	def run(self):
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings)
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