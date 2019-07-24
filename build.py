import sublime
import sublime_plugin
from .bsscript.bsscriptSblm import SblmCmmnFnctns, BSSCompiler

class BsscriptBuildCommand(sublime_plugin.WindowCommand):	
	def run(self):
		settings = SblmCmmnFnctns.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBPROCESS)
		sublime.set_timeout_async(compiler.compileAll, 0)