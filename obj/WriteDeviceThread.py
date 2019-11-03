#!/usr/bin/python3
import time
from PySide2 import QtCore

class WriteDeviceThread(QtCore.QThread):
    def __init__(self, wsprDevice):
        QtCore.QThread.__init__(self)
        self.wsprDevice = wsprDevice
        self.paused = False

    def run(self):
        return
    
    def stop(self):
        self.wait()
        self.exit()
        return
    
    def pause(self):
        self.paused = True
        return

    def resume(self):
        self.paused = False
        return

    def writeCommand(self, commandArray):
        if not self.paused:
            try:
                for command in commandArray:
                    self.wsprDevice.WriteCommand(command)

                self.emit( QtCore.SIGNAL('write(bool)'), True)
            except:
                self.emit( QtCore.SIGNAL('exception(QString)'), "Write Failed. Device disconnected.")
        return
