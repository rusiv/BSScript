import os
import shutil
import subprocess
import re
import fnmatch

BLL_EXT = '.bll'
CI_EXT = '.classinfo'
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
	if (filePath) and (os.path.isfile(filePath)):
		patchDir = getPathcDirForFile(filePath)
		if (patchDir):
			patchUserDir = getPathcDirForFile(filePath) + "\\libfiles\\user"
			if os.path.exists(patchUserDir):
				result.append(patchUserDir)

	return result

def samefile(file1, file2): 
	return os.stat(file1) == os.stat(file2) 

def copyBllsInUserPaths(version, workingDir, userPaths, bllFullPath): 
	mainUserPath = workingDir + "\\user\\"
	result = []
	if not bllFullPath:
		print('No BLL for copy!')
		return result
	if os.path.exists(bllFullPath):
		if version == '15':
			for userPath in userPaths:
				shutil.copy2(bllFullPath, userPath)
				result.append(userPath + "\\" + os.path.basename(bllFullPath))
			os.remove(bllFullPath)
		else:
			for userPath in userPaths:				
				# if not os.path.samefile(mainUserPath, userPath):
				if not samefile(mainUserPath, userPath):
					shutil.copy2(bllFullPath, userPath)
					result.append(userPath + "\\" + os.path.basename(bllFullPath))
	return result

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

def getBllPathByBlsPath(blsFullPath, compilerVersion, workingDir):
	if not blsFullPath:
		return False
	bllDir = os.path.dirname(blsFullPath)
	bllFileName = os.path.splitext(os.path.basename(blsFullPath))[0]
	if compilerVersion == '15':
		return bllDir + "\\" + bllFileName + BLL_EXT
	else:
		mainUserPath = workingDir + "\\user\\"
		return mainUserPath + bllFileName + BLL_EXT

def fullCopy(root_src_dir, root_dst_dir):
	if not root_src_dir:
		return
	for src_dir, dirs, files in os.walk(root_src_dir):
		dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
		if not os.path.exists(dst_dir):
			os.makedirs(dst_dir)
		for file_ in files:
			src_file = os.path.join(src_dir, file_)
			dst_file = os.path.join(dst_dir, file_)
			if os.path.exists(dst_file):
				os.remove(dst_file)
			shutil.copy2(src_file, dst_dir)

def getFileLis(path, mask):
    return [os.path.join(d, filename) for d, _, files in os.walk(path) for filename in fnmatch.filter(files, mask)]

def mergeDirs(dirs, target):
	if (len(dirs) == 0) or (not target):
		return
	for dir in dirs:
		fullCopy(dir, target)

def delClassInfoFile(bllFullPath):
	if not bllFullPath:
		return
	fileDir = os.path.dirname(bllFullPath)
	fileName = os.path.splitext(os.path.basename(bllFullPath))[0]
	delFileName = fileDir + "\\" + fileName + CI_EXT		
	if not os.path.exists(delFileName):
		return
	os.remove(delFileName)
	return delFileName;