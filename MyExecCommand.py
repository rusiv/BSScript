import sublime
from Default.exec import ExecCommand
import os
from . import CommonFunctions
from .BSSCompiler import BSSCompiler

class MyExecCommand(ExecCommand):

	def run(self, 
		on_finished_func_desc,
		cmd = None, 
		shell_cmd = None, 
		file_regex = '', 
		line_regex = '', 
		working_dir = '', 
		encoding = 'utf-8', 
		env = {}, 
		quiet = False, 
		kill = False, 
		update_phantoms_only = False, 
		hide_phantoms_only = False, 
		word_wrap = True, 
		syntax = 'Packages/Text/Plain text.tmLanguage',
		**kwargs):
		self.on_finished_func_desc = on_finished_func_desc
		ExecCommand.run(self, cmd, shell_cmd, file_regex, line_regex, working_dir, encoding, env, quiet, kill, update_phantoms_only, hide_phantoms_only, word_wrap, syntax, **kwargs)


	def on_finished(self, proc):
		ExecCommand.on_finished(self, proc)
		if self.on_finished_func_desc:
			for functionName, functionParams in self.on_finished_func_desc.items():				
				fn = None
				if hasattr(CommonFunctions, functionName):
					fn = getattr(CommonFunctions, functionName)					
				elif hasattr(BSSCompiler, functionName):
					fn = getattr(BSSCompiler, functionName)
				if fn:
					fn(functionParams)