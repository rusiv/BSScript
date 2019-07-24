import sublime
import os
import shutil
import subprocess
import re
from .. import Helper

SUBLIME_STATUS_SPINNER = '1'
SUBLIME_STATUS_LOG = '2'
SUBLIME_STATUS_COMPILE_PROGRESS = '3'

def getWorkingDir(projectPath, fileInProject):
	if projectPath and fileInProject:
		for root, dirs, files in os.walk(projectPath):
			if Helper.isDirWorking(root):
				return root
	else:
		return Helper.getWorkingDirForFile(sublime.active_window().extract_variables().get("file_path"))

def getSettings():
	activeWindow = sublime.active_window()
	variables = activeWindow.extract_variables()
	projectPath = variables.get("project_path")
	filePath = variables.get("file_path")
	fileInProject = False
	if projectPath:
		fileInProject = projectPath in filePath
	workingDir = getWorkingDir(projectPath, fileInProject)
	if workingDir == None:
		workingDir = projectPath
	if os.path.exists(workingDir + "\\bank"):
		workingDir = workingDir + "\\bank"
	version = ''
	bllVersion = ''
	if fileInProject:
		bsccSettings = activeWindow.project_data().get('bscc')
		if bsccSettings:
			bllVersion = bsccSettings.get('bllVersion')
			buildVersion = bsccSettings.get('buildVersion')
			if buildVersion:
				version = buildVersion.split('.')[1]
	if not version:
		version = Helper.getVersion(workingDir + "\\exe\\bscc.exe")
	global_settings = sublime.load_settings("BSScript.sublime-settings")
	srcPath = workingDir + '\\SOURCE'
	if not os.path.exists(srcPath):
		srcPath = ''
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"srcPath": srcPath,
		"userPaths": Helper.getUserPaths(workingDir, filePath),
		"bllFullPath": workingDir + "\\user\\" + variables.get("file_base_name") + ".bll",
		"version": version,
		"compileAllToTempFolder": global_settings.get("compileAll_to_temp_Folder", True),
		"compileAllFastMode": global_settings.get("compileAll_fast_mode", True),
		"protect_server": global_settings.get("protect_server_" + version, ""),
		"protect_server_alias": global_settings.get("protect_server_alias_" + version, ""),
		"bllVersion": bllVersion
	}	

def getBLLFullPath(blsFullPath, compilerVersion, workingDir):
	if blsFullPath:
		bllDir = os.path.dirname(blsFullPath)
		bllFileName = os.path.splitext(os.path.basename(blsFullPath))[0]
	else:
		activeWindow = sublime.active_window()
		bllDir = activeWindow.extract_variables()["file_path"]
		bllFileName = activeWindow.extract_variables()["file_base_name"]

	if compilerVersion == '15':
		return bllDir + "\\" + bllFileName + Helper.BLL_EXT
	else:
		mainUserPath = workingDir + "\\user\\"
		return mainUserPath + bllFileName + Helper.BLL_EXT