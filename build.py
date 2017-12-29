import sublime_plugin

class BsscriptBuildCommand(sublime_plugin.WindowCommand):
    def run(self):
        print('Build')