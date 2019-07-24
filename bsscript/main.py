import sys
import os

# packageDir = os.path.dirname(os.path.abspath(__file__))
# os.sys.path.append(packageDir)
import Helper

ALLOWED_OPERATIONS = ['COMPILEFILE', 'COMPILEALL']
#python main.py compileFile "D:\BSS\GPB20_PROM(441)" "D:\BSS\GPB20_PROM(441)\BANK" 20 "10.1.7.91" "default" "1.1" "D:\BSS\GPB20_PROM(441)\BANK\SOURCE\BLS\ABS\ASVKB_GPB (200)\abDPOut.bls"
if __name__ == "__main__":
	if len(sys.argv) == 1:
		print('There must be help!')
	else:
		operation = sys.argv[1]
		operation = operation.upper()
		if ALLOWED_OPERATIONS.count(operation) == 0:
			print('Operation "' + operation + '" not allowed.')
			sys.exit
		projectPath = sys.argv[2]
		workingDir = sys.argv[3]		
		version = sys.argv[4]
		protectServer = sys.argv[5]
		protectServerAlias = sys.argv[6]
		bllVersion = sys.argv[7]
		sourcePath = workingDir + '\\SOURCE'
		if operation == 'COMPILEFILE':
			cmplAllToTmpFld = False
			cmplAllFastMode = False
			fileFullPath = sys.argv[8]
			fileName = os.path.splitext(os.path.basename(fileFullPath).lower())[0]
			bllFullPath = workingDir + "\\user\\" + fileName + ".bll"
		else:
			cmplAllToTmpFld = True
			if sys.argv[8]:
				cmplAllToTmpFld = bool(sys.argv[8])
			cmplAllFastMode = True
			if sys.argv[9]:
				cmplAllFastMode = bool(sys.argv[9])		
		setting = {
			"projectPath": projectPath,
			"working_dir": workingDir,
			"srcPath": sourcePath,
			"userPaths": Helper.getUserPaths(workingDir, fileFullPath),
			"bllFullPath": bllFullPath,
			"version": version,
			"compileAllToTempFolder": cmplAllToTmpFld,
			"compileAllFastMode": cmplAllFastMode,
			"protect_server": protectServer,
			"protect_server_alias": protectServerAlias,
			"bllVersion": bllVersion
		}

		if operation == 'COMPILEFILE':
			print('COMPILEFILE')