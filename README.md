# BSScript for Sublime
This project contains: a syntax for the BSScript language, a set of snippets, an autocomplete, and the configuration for the build system.
# Installation
**With the Package Control plugin**: bring up the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows), select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select BSScript when the list appears. 
The advantage of using this method is that Package Control will automatically keep BSScript up to date with the latest version.

**Without Git**: Download the latest source from GitHub and copy the BSScript folder to your Sublime Text "Packages" directory.

**With Git**: Clone repository git://github.com/rusiv/BSScript.git in your Sublime Text"Packages" directory.
# Configuration
To be able to compile *.bls files, you must create project, where: 
* bscc.exe locate in project_path\exe;
* system files in project_path\system;
* bll files in project_path\user.
