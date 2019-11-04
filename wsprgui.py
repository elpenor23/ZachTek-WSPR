#!/usr/bin/python3
#Main file to kick off the app
#This is what gets run to kick everything off.

import importlib
from importlib import util
#PyQt5 and PySerial packages are required for this project
pyqt5 = util.find_spec("PyQt5")
found_pyqt5 = pyqt5 is not None
pyserial = util.find_spec("serial")
found_pyserial = pyserial is not None

if found_pyqt5 and found_pyserial:

    import sys
    from lib.UISetup import WSPRUI
    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QApplication

    #FILE VARIABLES
    configurationFileDefaultName = 'config'
    configFileType = ".json"
    #END FILE VARIABLES

    #the main things
    def main(configurationFile):
        #app = QtWidgets.QApplication(sys.argv)
        app = QApplication(sys.argv)

        app.setStyleSheet(open('basic.css').read())
        ui = WSPRUI(configurationFile)
        sys.exit(app.exec_())


    #run all the things
    if __name__ == '__main__':
        #if we pass in a config file, use it
        if len(sys.argv) > 1 and str(sys.argv[1]).endswith(configFileType):
            configurationFile = str(sys.argv[1])
        else:
            configurationFile = configurationFileDefaultName + configFileType
            
        main(configurationFile)
else:
    print("PyQt5 and PySerial are required packages. Please install and try again.")