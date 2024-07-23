import re
import sublime

from .FnDef import FnDef

class FnDoc:
	def __init__(self, view):
		self.view = view

	def getBelowFnDef(self):		
		curLine = self.view.line(self.view.sel()[0].begin())
		startFn = self.view.line(curLine.end() + 1).begin();
		endFn = self.view.find(r'\)\s*\:?.*;', startFn).end();
		if endFn == -1:
			return None
		fnStr = self.view.substr(sublime.Region(startFn, endFn));		
		#todo: многострочные функции
		matcher = re.search(r'(?P<type>(^\bfunction\b))\s*(?P<name>(.*))(\s*\()\s*(?P<parameters>(.*))(\s*\))\s*:\s*(?P<returnType>(.*))\s*;', fnStr, flags = re.IGNORECASE)
		if matcher:
			matcherDict = matcher.groupdict()
			return FnDef(FnDef.TYPE_FUNCTION, matcherDict.get('name'), matcherDict.get('parameters'), matcherDict.get('returnType'))
		matcher = re.search(r'(?P<type>(^\bprocedure\b))\s*(?P<name>(.*))(\s*\()\s*(?P<parameters>(.*))(\s*\))\s*;', fnStr, flags = re.IGNORECASE)
		if matcher:
			matcherDict = matcher.groupdict()
			return FnDef(FnDef.TYPE_PROCEDURE, matcherDict.get('name'), matcherDict.get('parameters'))
		return None

	def makeBelowDescription(self):		
		fnDef = self.getBelowFnDef()		
		if not fnDef:
			return None
		print(fnDef.toString())