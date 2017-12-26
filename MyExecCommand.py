import sublime
from Default.exec import ExecCommand
import os
from . import CommonFunctions

class MyExecCommand(ExecCommand):

	def run(self, 
		on_finished_function_name,
		cmd = None, 
		shell_cmd = None, 
		file_regex = "", 
		line_regex="", working_dir="", 
		encoding="utf-8", 
		env={}, 
		quiet=False, 
		kill=False, 
		update_phantoms_only=False, 
		hide_phantoms_only=False, 
		word_wrap=True, 
		syntax="Packages/Text/Plain text.tmLanguage",
		**kwargs):
		self.on_finished_function_name = on_finished_function_name
		ExecCommand.run(self, cmd, shell_cmd, file_regex, line_regex, working_dir, encoding, env, quiet, kill, update_phantoms_only, hide_phantoms_only, word_wrap, syntax, **kwargs)


	def on_finished(self, proc):
		ExecCommand.on_finished(self, proc)
		if self.on_finished_function_name != '':
			fn = getattr(CommonFunctions, self.on_finished_function_name)
			if fn:
				fn()