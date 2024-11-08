import os
import re
import subprocess

class Git:
	def __init__(self, settings):		
		if not settings:
			return
		self.repo = settings['repoPath']
		self.gitPath = os.path.join(settings['gitPath'], 'git')		

	def _getFileListSinceCommit(self, commit):		
		if (commit):
			return []
		date = ''
		return self._getFileListSinceDate(date)
		
	def _getFileListSinceDate(self, date):
		# git log --name-only --since=""2024-09-08"" --pretty=format: >> 2.txt		
		if (not date):
			return []