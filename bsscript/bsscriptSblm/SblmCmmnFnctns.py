import sublime
import os
import shutil
import subprocess
import re
from .. import Helper
from ..BllExecuter import BllExecuter

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
		"delClassInfo": global_settings.get("del_class_info", True),
		"protect_server": global_settings.get("protect_server_" + version, ""),
		"protect_server_alias": global_settings.get("protect_server_alias_" + version, ""),
		"bllVersion": bllVersion
	}	

def getBllPathByBlsSblmWin(compilerVersion, workingDir):
	activeWindow = sublime.active_window()
	bllDir = activeWindow.extract_variables()["file_path"]
	bllFileName = activeWindow.extract_variables()["file_base_name"]
	if compilerVersion == '15':
		return bllDir + "\\" + bllFileName + Helper.BLL_EXT
	else:
		mainUserPath = workingDir + "\\user\\"
		return mainUserPath + bllFileName + Helper.BLL_EXT

def copyBllsInUserPaths(functionParams): 
	version = functionParams.get('version')	
	workingDir = functionParams.get('workingDir')	
	userPaths = functionParams.get('userPaths')
	bllFullPath = functionParams.get('bllFullPath')
	copiedBlls = Helper.copyBllsInUserPaths(version, workingDir, userPaths, bllFullPath)
	print('Copied bll list: ' + str(copiedBlls))

def runTest(functionParams):
	workingDir = functionParams.get('workingDir')
	bllFullPath = functionParams.get('bllFullPath')
	executer = BllExecuter(workingDir, bllFullPath)
	if len(executer.errors) > 0:
		for error in executer.errors:
			print('Error: ' + error)
		return
	TEST_FUNCTION = '__test__execute'

	print('Start runTest for ' + bllFullPath);
	executer.execFunction(TEST_FUNCTION)
	print('End runTest for ' + bllFullPath);

def delClassInfoFile(functionParams): 
	bllFullPath = functionParams.get('bllFullPath')	
	fileName = Helper.delClassInfoFile(bllFullPath)
	if fileName:
		print('ClassInfo file ' + fileName + ' deleted')
