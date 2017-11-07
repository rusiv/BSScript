import sublime
import sublime_plugin
import os
import subprocess

errorMessages = dict(projectPathNotDefined="Project path not defined")

class bsscriptCompileCommand(sublime_plugin.WindowCommand):
	def run(self):
		activeWindow = sublime.active_window()
		activeWindow.run_command("save")

class bsscriptCompileEventListeners(sublime_plugin.EventListener):
	def on_post_save(self, view):
		activeWindow = sublime.active_window()
		fileExt = activeWindow.extract_variables()["file_extension"].upper()
		if fileExt != 'BLS' :
			return
		projectPath = activeWindow.extract_variables().get("project_path")
		projectPath = projectPath if projectPath != None else self.getProjectPath()
		if projectPath == None:
			print('BSScript: ' + errorMessages.get("projectPathNotDefined"))
			sublime.status_message(errorMessages.get("projectPathNotDefined"))
			return
		fileFullPath = activeWindow.extract_variables()["file"]
		global_settings = sublime.load_settings("BSScript.sublime-settings")
		activeWindow.run_command("exec", {
			"working_dir": projectPath,
			"path": "exe;system;user",
			"cmd": ["bscc.exe ", fileFullPath, "-S" + global_settings.get("protect_server", ""), "-A" + global_settings.get("protect_server_alias", ""), "-Tuser"],
			"file_regex": "Program\\s(.*)\\s*.*\\s*.*line is (\\d*)",
			"quiet": True,
		})
		activeWindow.find_output_panel("exec").set_syntax_file("BSScript-build.sublime-syntax")

	def getProjectPath(self):
		projectPath = sublime.active_window().extract_variables().get("file_path")
		sepIdx = projectPath.rfind('\\')
		while sepIdx != -1:
			projectPath = projectPath[:sepIdx]
			if os.path.exists(projectPath + "\\exe") and os.path.exists(projectPath + "\\user"):
				return projectPath
			sepIdx = projectPath.rfind('\\')
		return None
