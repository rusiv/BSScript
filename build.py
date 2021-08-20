import sublime
import sublime_plugin
from .bsscript.bsscriptSblm import SblmCmmnFnctns, SblmBSSCompiler

class BsscriptBuildCommand(sublime_plugin.WindowCommand):	
	def run(self):
		settings = SblmCmmnFnctns.getSettings()		
		compiler = SblmBSSCompiler(settings, SblmBSSCompiler.MODE_SUBPROCESS)
		sublime.set_timeout_async(compiler.compileAll, 0)