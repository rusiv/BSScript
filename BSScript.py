import sublime
import sublime_plugin
import os
from ctypes import *
import time
import shutil
from Default.exec import ExecCommand

errorMessages = dict(projectPathNotDefined = "Project path not defined")

def getVersion(bsccPath):
	bscc = open(bsccPath, "rb")
	data = bscc.read().decode("utf-8", "ignore")
	bscc.close()
	strVersionBegin = data.find('http://bss.bssys.com/code/')
	if strVersionBegin < 0:
		return "0"
	fullVersion = data[strVersionBegin + 26:data.find('/bscc.exe')]
	return fullVersion.split('.')[1]

def getWorkingDir():
	projectPath = sublime.active_window().extract_variables().get("file_path")
	sepIdx = projectPath.rfind('\\')
	while sepIdx != -1:
		projectPath = projectPath[:sepIdx]
		if os.path.exists(projectPath + "\\exe") and os.path.exists(projectPath + "\\user"):
			return projectPath
		sepIdx = projectPath.rfind('\\')
	return None

def getUserPaths(workingDir):
	result = []
	if os.path.basename(workingDir).upper() == 'BANK':
		parent = os.path.dirname(workingDir)
		for dir in os.listdir(parent):
			userDir = parent + "\\" + dir + "\\user"
			if os.path.exists(userDir):
				result.append(userDir)
	return result

def getSettings():
	activeWindow = sublime.active_window()
	projectPath = activeWindow.extract_variables().get("project_path")
	workingDir = getWorkingDir()
	if workingDir == None:
		workingDir = projectPath
	if os.path.exists(workingDir + "\\bank"):
		workingDir = workingDir + "\\bank"
	fileFullPath = activeWindow.extract_variables()["file"]
	global_settings = sublime.load_settings("BSScript.sublime-settings")
	version = getVersion(workingDir + "\\exe\\bscc.exe")
	protectServer = global_settings.get("protect_server_" + version, "")	
	protectServerAlias = global_settings.get("protect_server_alias_" + version, "")
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"fileFullPath": fileFullPath,
		"userPaths": getUserPaths(workingDir),
		"bllFullPath": workingDir + "\\user\\" + activeWindow.extract_variables()["file_base_name"] + ".bll",
		"version": version,
		"protect_server": protectServer,
		"protect_server_alias": protectServerAlias
	}

def copyBllsInUserPaths(settings):
	if settings.get("version", "") == "15":
		activeWindow = sublime.active_window()
		bllFullPath = activeWindow.extract_variables()["file_path"] + "\\" + activeWindow.extract_variables()["file_base_name"] + '.bll'
		if os.path.exists(bllFullPath):
			for userPath in settings.get("userPaths", []):
				shutil.copy2(bllFullPath, userPath)		
			os.remove(bllFullPath)
		
class bsscriptCompileCommand(sublime_plugin.WindowCommand):
	def run(self):		
		activeWindow = sublime.active_window()
		activeWindow.run_command("save")

class myExecCommand(ExecCommand):
	def on_data(self, proc, data):
		ExecCommand.on_data(self, proc, data)
		settings = getSettings()
		copyBllsInUserPaths(settings)

class bsscriptCompileEventListeners(sublime_plugin.EventListener):
	def on_post_save(self, view):
		activeWindow = sublime.active_window()
		fileExt = activeWindow.extract_variables()["file_extension"].upper()
		if fileExt != 'BLS' :
			return
		settings = getSettings()
		workingDir = settings.get("working_dir", "")
		if workingDir == None:
			print('BSScript: ' + errorMessages.get("projectPathNotDefined"))
			return
		activeWindow.run_command("my_exec", {
			"working_dir": workingDir,
			"encoding": "cp1251",
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