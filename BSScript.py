import sublime
import sublime_plugin
import os
import subprocess



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
			
		projectPath = activeWindow.extract_variables()["project_path"]
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