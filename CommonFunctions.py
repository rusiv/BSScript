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
	compileAllToTempFolder = global_settings.get("compileAll_to_temp_Folder", True)
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
		"compileAllToTempFolder": compileAllToTempFolder,
		"protect_server": protectServer,
		"protect_server_alias": protectServerAlias
	}	

def getBLLFullPath(blsFullPath, compilerVersion, workingDir):
	BLL_EXT = '.bll'
	if blsFullPath:
		bllDir = os.path.dirname(blsFullPath)
		bllFileName = os.path.splitext(os.path.basename(blsFullPath))[0]
	else:
		activeWindow = sublime.active_window()
		bllDir = activeWindow.extract_variables()["file_path"]
		bllFileName = activeWindow.extract_variables()["file_base_name"]

	if compilerVersion == '15':
		return bllDir + "\\" + bllFileName + BLL_EXT
	else:
		mainUserPath = workingDir + "\\user\\"
		return mainUserPath + bllFileName + BLL_EXT

def copyBllsInUserPaths(functionParams):
	version = functionParams.get('version')
	workingDir = functionParams.get('workingDir')
	userPaths = functionParams.get('userPaths')
	mainUserPath = workingDir + "\\user\\"
	bllFullPath = functionParams.get('bllFullPath')
	if not bllFullPath:
		print('No BLL for copy!')
		return
	if os.path.exists(bllFullPath):
		if version == '15':
			for userPath in userPaths:
				shutil.copy2(bllFullPath, userPath)
			os.remove(bllFullPath)
		else:
			for userPath in userPaths:
				if not os.path.samefile(mainUserPath, userPath):
					shutil.copy2(bllFullPath, userPath)

def listToFile(list, filePath):	
	if not list:
		return False
	file = open(filePath, 'w')
	for item in list:
		file.write("%s\n" % item)
	return True