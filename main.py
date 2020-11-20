import sys
import os
import json

packageDir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.append(packageDir)
import bsscript

#python main.py compileFile "D:\BSS\GPB20_PROM(441)" "D:\BSS\GPB20_PROM(441)\BANK" 20 "10.1.7.91" "default" "1.1" "D:\BSS\GPB20_PROM(441)\BANK\SOURCE\BLS\ABS\ASVKB_GPB (200)\abDPOut.bls"
#python main.py compileFileAndTest "D:\BSS\GPB20_PROM(441)" "D:\BSS\GPB20_PROM(441)\BANK" 20 "10.1.7.91" "default" "1.1" "D:\BSS\GPB20_PROM(441)\BANK\SOURCE\BLS\ABS\ASVKB_GPB (200)\abDPOut.bls"
#python main.py getSortedBlsList "D:\BSS\GPB20_PROM(441)\BANK\SOURCE\BLS" "C:\blsList.txt"
#python main.py compileAll "D:\BSS\GPB20_PROM(441)" "D:\BSS\GPB20_PROM(441)\BANK" 20 "10.1.7.91" "default" "1.1" 1 "D:\BSS\GPB20_PROM(441)\BANK\TempBll"
#python main.py compileAll "D:\BSS\GPB20_PROM(441)" "D:\BSS\GPB20_PROM(441)\BANK" 20 "10.1.7.91" "default" "1.1" 0 "D:\BSS\GPB20_PROM(441)\BANK\TempBll"

#python main.py compileAll "D:\BSS\STAND_FOR_BUILDER" "D:\BSS\STAND_FOR_BUILDER\BANK" 17 "LGServer" "otd-2ps" "1.1" 0 "D:\BSS\STAND_FOR_BUILDER\TempBll"
#python main.py createPatch 1 "D:\MyPatch" "200123_RSHB_017_9_580"

def onNotCompiled(compiler):
	print(str(compiler.errors))

def onCompiled(compiler):
	print('BLS successfully compiled!')

def onBllCopied(copiedBlls):
	print('Copied bll list: ' + str(copiedBlls))

def getCompilerSettingsByArgs(args, operation = 'compileFile'):	
	projectPath = args[2]
	workingDir = args[3]
	version = args[4]
	protectServer = args[5]
	protectServerAlias = args[6]
	bllVersion = args[7]
	sourcePath = workingDir + '\\SOURCE'
	if operation.upper() == 'COMPILEALL':
		fileFullPath = args[8]	
		userPaths = bsscript.Helper.getUserPaths(workingDir, fileFullPath)
	return {
		"projectPath": projectPath,
		"working_dir": workingDir,
		"srcPath": sourcePath,
		"userPaths": userPaths,
		"version": version,
		"protect_server": protectServer,
		"protect_server_alias": protectServerAlias,
		"bllVersion": bllVersion
	}	

def getCompilerByArgs(args):
	return bsscript.BSSCompiler(getCompilerSettingsByArgs(args))

def getSortedBlsList(args):
	l = len(args)
	if (l != 3) and (l != 4):
		print('Wrong number of parameters')
		return
	sourcePath = args[2]
	if (l == 4):
		expFileName = args[3]
	if not os.path.exists(sourcePath):
		print('Folder ' + sourcePath + ' not found.')
		return
	fastMode = False
	builder = bsscript.BSSBuilder(fastMode)
	sortedBlsList = builder.getSortedBlsPathList(sourcePath)
	if (len(sortedBlsList) == 0):
		print(builder.error)
		if (len(builder.cycles) > 0):
			print('\n'.join(builder.cycles))
	else:
		if expFileName:
			file = open(expFileName, 'w')
			for item in sortedBlsList:
				file.write("%s\n" % item)
			print('SortedBlsList saved to ' + expFileName)
		else:
			print('\n'.join(sortedBlsList))

def compileFile(args):
	compiler = getCompilerByArgs(args)
	fileFullPath = args[8]
	compiler.em.connect(bsscript.BSSCompiler.EVENT_NOT_COMPILED, onNotCompiled, compiler)
	compiler.em.connect(bsscript.BSSCompiler.EVENT_COMPILED, onCompiled, compiler)
	compiler.em.connect(bsscript.BSSCompiler.EVENT_BLL_COPIED, onBllCopied)
	compiler.compile(fileFullPath)

def compileFileAndTest(args):
	compiler = getCompilerByArgs(args)
	fileFullPath = args[8]
	compiler.em.connect(bsscript.BSSCompiler.EVENT_NOT_COMPILED, onNotCompiled, compiler)
	compiler.em.connect(bsscript.BSSCompiler.EVENT_COMPILED, onCompiled, compiler)
	compiler.em.connect(bsscript.BSSCompiler.EVENT_BLL_COPIED, onBllCopied)
	compiler.compileAndTest(fileFullPath)

def compileAll(args):
	compillerSettings = getCompilerSettingsByArgs(args, 'COMPILEALL')
	cmplAllFastMode = True
	if args[8]:
		cmplAllFastMode = bool(int(args[8]))
	if args[9]:
		destPath = args[9]	
	builder = bsscript.BSSBuilder(cmplAllFastMode, compillerSettings)
	builder.compileAllBls(None, destPath)

def createPatch(args):
	cmplAllFastMode = bool(int(args[2]))
	patchPath = args[3]	
	patchVersion = args[4]
	cfgFileFullPath = '.\\patchCfg.json'
	if (len(args) == 6):
		cfgFileFullPath = args[5]
	cfgFile = open(cfgFileFullPath, 'r')
	data = json.load(cfgFile)
	compillerSettings = data.get('compiller', None)
	starteamSettigs = data.get('st', None)
	labels = data.get('labels', None)
	if (not compillerSettings) or (not starteamSettigs) or (not labels):
		print('Cfg file ' + cfgFileFullPath + ' is incorrect!')
		return
	builder = bsscript.BSSBuilder(cmplAllFastMode, compillerSettings, starteamSettigs)
	builder.createPatch(patchPath, patchVersion, labels)

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print('There must be help!')
	else:
		operation = sys.argv[1]
		operation = operation.upper()

		if (operation == 'GETSORTEDBLSLIST'):
			getSortedBlsList(sys.argv)
		elif (operation == 'COMPILEFILE'):
			compileFile(sys.argv)
		elif (operation == 'COMPILEFILEANDTEST'):
			compileFileAndTest(sys.argv)
		elif (operation == 'COMPILEALL'):
			compileAll(sys.argv)
		elif (operation == 'CREATEPATCH'):
			createPatch(sys.argv)
		else:
			print('Operation ' + operation + ' not supported.')