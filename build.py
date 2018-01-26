import sublime
import sublime_plugin
from . import CommonFunctions
from .BSSCompiler import BSSCompiler

class BsscriptBuildCommand(sublime_plugin.WindowCommand):	
	def run(self):
		settings = CommonFunctions.getSettings()
		compiler = BSSCompiler(settings, BSSCompiler.MODE_SUBPROCESS)
		sublime.set_timeout_async(compiler.compileAll, 0)