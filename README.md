Project Title
    Translator

Description
This is a simple utilite created to help resource file translation. Was used to speed up translation work.
For now, supports only resx, xml and json files.
There are 2 ways to do translation:
    - manual mode. In this mode apps only parse res file and extracts strings for translation. You do translation manually and after that utilite create translated file with the same format.
    - automatic mode. In this mode Translator do all translation automatically using "googletrans". You have to check all strings manually and correct strings when it is needed.

Getting Started
Tested on Windows10, Windows11 with Python3.10 and Python3.12. To run Translator, first you need to compile its resources:
    - go to app’s folder 
    - open terminal 
    - run “your_python_path tools\build.py”
Compilation need to be done only once after that you can use “your_python_path mainwindow.py” to launch the app
Dependencies
    - PySide6
    - Pyperclip
    - googletrans==3.1.0a0
Installing
    - Install python 3.x first
    - Install all dependencies with command “your_python_path -m pip install -r path_to_requirements.txt” 
Authors
	Oleg Chudakov
License
    This project is licensed under the Apache 2.0 license.


