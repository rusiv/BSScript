import sublime
from Default.exec import ExecCommand
from . import CommonFunctions
import shutil
import os

class MyExecCommand(ExecCommand):
	def __copyBllsInUserPaths(self):
		settings = CommonFunctions.getSettings()
		if settings.get("version", "") == "15":
			activeWindow = sublime.active_window()
			bllFullPath = activeWindow.extract_variables()["file_path"] + "\\" + activeWindow.extract_variables()["file_base_name"] + '.bll'
			if os.path.exists(bllFullPath):
				for userPath in settings.get("userPaths", []):
					shutil.copy2(bllFullPath, userPath)		
				print(bllFullPath)
				os.remove(bllFullPath)

	def on_data(self, proc, data):
		ExecCommand.on_data(self, proc, data)		
		self.__copyBllsInUserPaths()