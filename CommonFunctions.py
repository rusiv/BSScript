import sublime
import os
import shutil
import subprocess
import re

SUBLIME_STATUS_SPINNER = '1'
SUBLIME_STATUS_LOG = '2'
SUBLIME_STATUS_COMPILE_PROGRESS = '3'
BLL_EXT = '.bll'
BLL_TYPE_CLIENT = 'c'
BLL_TYPE_BANK = 'b'
BLL_TYPE_ALL = 'a'
BLL_TYPE_RTS = 'rt_'
TEST_FUNCTION = '__test__execute'

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

def isDirWorking(path):
	return os.path.exists(path + "\\exe") and os.path.exists(path + "\\user") and (path.lower().find("\\instclnt\\") == -1) and (path.lower().find("client") == -1)

def getWorkingDirForFile(path):
	sepIdx = path.rfind('\\')
	while sepIdx != -1:
		path = path[:sepIdx]
		if isDirWorking(path):
			return path
		sepIdx = path.rfind('\\')
	return None


def getWorkingDir(projectPath, fileInProject):
	if projectPath and fileInProject:
		for root, dirs, files in os.walk(projectPath):
			if isDirWorking(root):
				return root
	else:
		return getWorkingDirForFile(sublime.active_window().extract_variables().get("file_path"))

def getPathcDirForFile(filePath):
	result = ''
	if filePath:
		filePath = filePath.lower()
		parts = filePath.partition("\\bank\\upgrade\\");
		if (parts[2]):
			result = parts[0] + parts[1] + parts[2][:parts[2].find("\\")]
	return result

def isBllForClient(filePath):
	if not filePath:
		return False	
	fileName, fileExtension = os.path.splitext(filePath)
	if not (fileExtension.lower() == BLL_EXT):
		return False
	bllType = fileName[1:2]
	if (bllType == BLL_TYPE_BANK):
		return False
	bllType = fileName[0:3]
	if (bllType == BLL_TYPE_RTS):
		return False
	return True

def getUserPaths(workingDir, filePath):
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
	patchDir = getPathcDirForFile(filePath)
	if (patchDir):
		patchUserDir = getPathcDirForFile(filePath) + "\\libfiles\\user"
		if os.path.exists(patchUserDir):
			result.append(patchUserDir)

	return result

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
		version = getVersion(workingDir + "\\exe\\bscc.exe")
	global_settings = sublime.load_settings("BSScript.sublime-settings")
	srcPath = workingDir + '\\SOURCE'
	if not os.path.exists(srcPath):
		srcPath = ''
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"srcPath": srcPath,
		"userPaths": getUserPaths(workingDir, filePath),
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
				print('BLL copyed in ' + userPath + '.')
			os.remove(bllFullPath)
		else:
			for userPath in userPaths:
				if not os.path.samefile(mainUserPath, userPath):
					shutil.copy2(bllFullPath, userPath)
					print('BLL copyed in ' + userPath + '.')

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

def execBll(workingDir, bllFullPath, functionName):
	def createExecBllCfg(workingDir):		
		SHOW_LOGIN = str.encode('ShowLoginWindow')
		SHOW_LOGIN_OFF = str.encode('ShowLoginWindow =0\r\n')
		result = False
		if not os.path.exists(workingDir + '\\exe\\default.cfg'):
			return result
		fDefCfg = open(workingDir + '\\exe\\default.cfg', 'rb')
		fExecCfg = open(workingDir + '\\exe\\execbll.cfg', 'wb')
		try:
			for line in fDefCfg:
				if line.find(SHOW_LOGIN) > -1:
					line = SHOW_LOGIN_OFF
				fExecCfg.write(line)
			print('execbll.cfg successfully created!')
			result = True
		finally:
			fDefCfg.close()
			fExecCfg.close()
			return result
	
	if not os.path.exists(workingDir + '\\exe\\execBLL.exe'):
		print(workingDir + '\\exe\\execBLL.exe not found!')
		return
	if not os.path.exists(workingDir + '\\exe\\execbll.cfg'):
		if not createExecBllCfg(workingDir):
			print('Not created execbll.cfg.')
	print('Start runTest for ' + bllFullPath);
	oldPath = os.environ['PATH']
	os.environ['PATH'] = os.path.expandvars('exe;system;user')
	os.chdir(workingDir)
	runStr = 'execBLL.exe ' + bllFullPath + ' ' + functionName
	process = subprocess.Popen(runStr, shell = True, stdout = subprocess.PIPE)			
	out, err = process.communicate()
	process.stdout.close()
	os.environ['PATH'] = oldPath
	print('End runTest for ' + bllFullPath);

def copyFileToDir(srcDirPath, dstDirPath, length = 16 * 1024):	
	fsrc = open(srcDirPath, 'rb')
	fdst = open(dstDirPath + '\\' + os.path.basename(srcDirPath), 'wb')
	copied = 0
	while True:
		buf = fsrc.read(length)
		if not buf:
			break
		fdst.write(buf)
		copied += len(buf)

def runTest(functionParams):
	workingDir = functionParams.get('workingDir')
	bllFullPath = functionParams.get('bllFullPath')
	execBll(workingDir, bllFullPath, TEST_FUNCTION)

def getExportFunctions(blsFullName):
	if (blsFullName == ''):
		print('BSScript: getExportFunctions no fullBLSFileName.')
		return None
	blsFile = open(blsFullName, "rb")
	data = blsFile.read().decode("cp1251", "ignore")
	blsFile.close()
	data = re.sub(r'{[\S\s]*?}', '', data, flags = re.IGNORECASE)
	data = re.sub(r'\(\*[\S\s]*?\*\)', '', data, flags = re.IGNORECASE)
	data = re.sub(r'//.*', '', data, flags = re.IGNORECASE)
	matcher = re.search(r'\bexports\b([\s\S][^;]*);', data, flags = re.IGNORECASE)
	strExports = ''
	if (matcher):
		strExports = matcher.group(1)		
		strExports = re.sub(r'\s', '', strExports, flags = re.IGNORECASE)		
		strExports = strExports.lower()		
	if (strExports != ''):
		return strExports.split(',')
	else:
		return None

def getFullBlsName(blsName, srcDir):
	result = []
	blsName = blsName + '.bls'
	for root, dirs, files in os.walk(srcDir):		
		for file in files:
			if blsName.lower() == file.lower():
				result.append(os.path.join(root, file))
	return result