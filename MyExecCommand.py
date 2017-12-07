import sublime
from Default.exec import ExecCommand
from . import CommonFunctions
import shutil
import os

class MyExecCommand(ExecCommand):	
	def __copyBllsInUserPaths(self):
		activeWindow = sublime.active_window()
		settings = CommonFunctions.getSettings()
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

	def on_data(self, proc, data):
		ExecCommand.on_data(self, proc, data)		
		self.__copyBllsInUserPaths()