import sublime
import os
import shutil

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
	global_settings = sublime.load_settings("BSScript.sublime-settings")
	version = getVersion(workingDir + "\\exe\\bscc.exe")
	protectServer = global_settings.get("protect_server_" + version, "")	
	protectServerAlias = global_settings.get("protect_server_alias_" + version, "")
	srcPath = workingDir + '\\SOURCE'
	if not os.path.exists(srcPath):
		srcPath = ''
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"srcPath": srcPath,
		"userPaths": getUserPaths(workingDir),
		"bllFullPath": workingDir + "\\user\\" + activeWindow.extract_variables()["file_base_name"] + ".bll",
		"version": version,
		"protect_server": protectServer,
		"protect_server_alias": protectServerAlias
	}

def copyBllsInUserPaths():
	activeWindow = sublime.active_window()
	settings = getSettings()
	version = settings.get("version", "")
	if version == "15":			
		bllFullPath = activeWindow.extract_variables()["file_path"] + "\\" + activeWindow.extract_variables()["file_base_name"] + '.bll'
		if os.path.exists(bllFullPath):
			for userPath in settings.get("userPaths", []):
				shutil.copy2(bllFullPath, userPath)
			os.remove(bllFullPath)
	elif (version == "17") or (version == "20"):
		mainUserPath = settings.get("working_dir", "") + "\\user\\"
		bllFullPath = mainUserPath + activeWindow.extract_variables()["file_base_name"] + '.bll'
		if os.path.exists(bllFullPath):
			for userPath in settings.get("userPaths", []):
				if not os.path.samefile(mainUserPath, userPath):
					shutil.copy2(bllFullPath, userPath)