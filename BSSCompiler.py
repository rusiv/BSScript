import sublime

class BSSCompiler:
	def __init__(self, settings):		
		if (settings != None):
			self.workingDir = settings.get("working_dir", "")
			self.protectServer = settings.get('protect_server', '')
			self.protectServerAlias = settings.get('protect_server_alias', '')
			self.copyBLLs = True

	def __compile__(self, workingDir, blsPath, protectServer, protectServerAlias, copyBLLs):
		if (blsPath == ''):
			print('BSScript: No bls for compile.')
			return		
		if (workingDir == '') or (protectServer == '') or (protectServerAlias == ''):
			print('BSScript: Not all settings are filled out.')
			return
		activeWindow = sublime.active_window()
		command = "my_exec" if copyBLLs else "exec"
		activeWindow.run_command(command, {
			"working_dir": workingDir,
			"encoding": "cp1251",
			"path": "exe;system;user",
			"cmd": ["bscc.exe ", blsPath, "-S" + protectServer, "-A" + protectServerAlias, "-Tuser"],
			"file_regex": "Program\\s(.*)\\s*.*\\s*.*line is (\\d*)",
			"quiet": True
		})
	
	def compile(self, blsPath):
		self.__compile__(self.workingDir, blsPath, self.protectServer, self.protectServerAlias, self.copyBLLs)

	compileBLS = staticmethod(__compile__)