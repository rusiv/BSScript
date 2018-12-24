# BSScript for Sublime
This project contains: a syntax for the BSScript language, a set of snippets, an autocomplete, and the configuration for the build system.
# Installation
**With the Package Control plugin**: bring up the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows), select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select BSScript when the list appears. 
The advantage of using this method is that Package Control will automatically keep BSScript up to date with the latest version.

**Without Git**: Download the latest source from GitHub and copy the BSScript folder to your Sublime Text "Packages" directory.

**With Git**: Clone repository git://github.com/rusiv/BSScript.git in your Sublime Text"Packages" directory.
# Configuration
For correct operation it is desirable to create a project. Project must have:
* bscc.exe locate in project_path\exe;
* system files in project_path\system;
* bll files in project_path\user.

If there is no project, the folders "exe", "system" and "user" are looked up in relation to the file being compiled.

Configure your protected servers for all version (Preferences -> Package settings -> BSScript). **"protect_server_0"** is default server, also it use for build 3.0.xxx.

Some settings are stored in the project file. For add empty settings to the in the project file use Tools -> BSScript -> Add BSScript Project Settings. Description of the used settings:
* stCmd - path to StarTeam client (stcmd.exe);
* stLogin - StartTeam login;
* stPassword - StarTeam password, can be empty (in this case, the password will be requested when checkout);
* stPort - StartTeam server port;
* stProject - StartTeam project name;
* stServer - StartTeam server;
* stView - StartTeam view.

If errors occur during building (compile all bls), change the settings **"compileAll_fast_mode"** on false (true - use file list, false - one by one).  
Setting **"compileAll_to_temp_Folder"** for build (compile all bls): true - save bll on folder "%workingDir%\TempBLL", false - save on folder "User". **Attention**: at buildig (compile all bls) all files in directory "%workingDir%\TempBLL" or "%workingDir%\User" (depending on the setting "compileAll_to_temp_Folder") will be deleted.

# Use
For compile save bls file or press "ctrl+f9" or right click on file in side bar and choose "Compile".

For compile and run test press "ctrl+shift+f9". For run test you need EXE\execbll.exe and export procedure **__test__execute** (use snippet).

For compile all bls run build system "ctrl+b".

For checkout files from StarTeam press "ctrl+shift+o", then enter label name in the displayed panel. In the case of an empty password un the settigs - enter password in the next displayed panel.
