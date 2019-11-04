#!/usr/bin/python3
#Main file to kick off the app
#This is what gets run to kick everything off.

import sys
#from PySide2 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from lib.UISetup import WSPRUI

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