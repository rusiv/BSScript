import sublime
import sublime_plugin
import os
from ctypes import *
import time

def getVersion(bsccPath):
	bscc = open(bsccPath, "rb")
	data = bscc.read().decode("utf-8", "ignore")
	bscc.close()
	fullVersion = data[data.find('http://bss.bssys.com/code/') + 26:data.find('/bscc.exe')]
	return fullVersion.split('.')[1]

def getSettings():
	activeWindow = sublime.active_window()
	projectPath = activeWindow.extract_variables()["project_path"]
	workingDir = projectPath
	if os.path.exists(projectPath + "\\bank"):
		workingDir = projectPath + "\\bank"
	fileFullPath = activeWindow.extract_variables()["file"]
	global_settings = sublime.load_settings("BSScript.sublime-settings")
	version = getVersion(workingDir + "\\exe\\bscc.exe")
	protectServer = global_settings.get("protect_server_" + version, "")
	protectServerAlias = global_settings.get("protect_server_alias_" + version, "")
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"fileFullPath": fileFullPath,
		"bllFullPath": projectPath + "\\user\\" + activeWindow.extract_variables()["file_base_name"] + ".bll",
		"protect_server": protectServer,
		"protect_server_alias": protectServerAlias
	}

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
		settings = getSettings()		
		activeWindow.run_command("exec", {
			"working_dir": settings.get("working_dir", ""),
			"path": "exe;system;user",
			"cmd": ["bscc.exe ", settings.get("fileFullPath", ""), "-S" + settings.get("protect_server", ""), "-A" + settings.get("protect_server_alias", ""), "-Tuser"],
			"file_regex": "Program\\s(.*)\\s*.*\\s*.*line is (\\d*)",
			"quiet": True
		})
		activeWindow.find_output_panel("exec").set_syntax_file("BSScript-build.sublime-syntax")

class bsscriptCompileAndTestCommand(sublime_plugin.WindowCommand):
	#not working
	def run(self):
		activeWindow = sublime.active_window()
		activeWindow.run_command("save")
		settings = getSettings()
		activeWindow.run_command("exec", {
			"working_dir": settings.get("projectPath", ""),
			"path": "exe;system;user",
			"cmd": ["execBLL.exe ", settings.get("bllFullPath", ""), "__test__execute"],
			"quiet": True
		})