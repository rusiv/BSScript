import sublime
import os
import shutil

SUBLIME_STATUS_SPINNER = '1'
SUBLIME_STATUS_LOG = '2'
SUBLIME_STATUS_COMPILE_PROGRESS = '3'

def getVersion(bsccPath):
	PRUDUCT_VERSION = b'\x50\x00\x72\x00\x6F\x00\x64\x00\x75\x00\x63\x00\x74\x00\x56\x00\x65\x00\x72\x00\x73\x00\x69\x00\x6F\x00\x6E\x00'
	PRODUCT_HTTP = 'http://bss.bssys.com/code/'
	bscc = open(bsccPath, "rb")	
	data = bscc.read()
	bscc.close()	
	dataStr = data.decode("utf-8", "ignore")
	strVersionBegin = dataStr.find(PRODUCT_HTTP)
	if strVersionBegin < 0:
		strVersionBegin = data.find(PRUDUCT_VERSION)
		if strVersionBegin < 0:
			return '0'		
		versionByte = data[strVersionBegin:]
		versionByte = versionByte[:versionByte.find(b'\x01\x00')]
		fullVersion = ''
		fullVersionByte = bytearray(b'')
		for b in versionByte:		
			if b != 0:
				fullVersionByte.append(b)
		fullVersion = str(fullVersionByte)
		if fullVersion == '':
			return '0'
		else:
			return fullVersion.split('.')[1]
	else:
		fullVersion = dataStr[strVersionBegin + 26:dataStr.find('/bscc.exe')]
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
	workingDirName = os.path.basename(workingDir).upper()
	result = []
	if (workingDirName == 'BANK') or (workingDirName == 'BSSYSTEMS'):
		parent = os.path.dirname(workingDir)
		for dir in os.listdir(parent):			
			userDir = parent + "\\" + dir + "\\user"
			if os.path.exists(userDir):
				result.append(userDir)
			userDir = parent + "\\" + dir + "\\BS-Client\\user"
			if os.path.exists(userDir):
				result.append(userDir)
	return result

def getSettings():
	activeWindow = sublime.active_window()
	variables = activeWindow.extract_variables()
	projectPath = variables.get("project_path")
	filePath = variables.get("file_path")
	fileInProject = False
	if projectPath:
		fileInProject = projectPath in filePath
	workingDir = getWorkingDir()
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
		version = getVersion(workingDir + "\\exe\\bscc.exe")
	global_settings = sublime.load_settings("BSScript.sublime-settings")
	srcPath = workingDir + '\\SOURCE'
	if not os.path.exists(srcPath):
		srcPath = ''
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"srcPath": srcPath,
		"userPaths": getUserPaths(workingDir),
		"bllFullPath": workingDir + "\\user\\" + variables.get("file_base_name") + ".bll",
		"version": version,
		"compileAllToTempFolder": global_settings.get("compileAll_to_temp_Folder", True),
		"compileAllFastMode": global_settings.get("compileAll_fast_mode", True),
		"protect_server": global_settings.get("protect_server_" + version, ""),
		"protect_server_alias": global_settings.get("protect_server_alias_" + version, ""),
		"bllVersion": bllVersion
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

def deleteFiles(functionParams):
	files = functionParams.get('files')
	for file in files:
		os.remove(file)

def compareCountBlsAndBLL(functionParams):
	def getFilesCount(path, filter):
		result = 0
		for root, dirs, files in os.walk(path):
			for name in files:
				if name.upper().endswith(filter):
					result = result + 1
		return result	
	
	result = False
	blsFolder = functionParams.get('blsFolder')
	bllFolder = functionParams.get('bllFolder')
	blsCount = getFilesCount(blsFolder, '.BLS')
	bllCount = getFilesCount(bllFolder, '.BLL')
	result = blsCount == bllCount
	if result:
		print('BSScript: AllCompiled succesfull (' + str(bllCount) + ')')
	else:
		print('BSScript: AllCompile not completely (' + str(bllCount) + ' of ' + str(blsCount) + ')')	
	return result