#!/usr/bin/python3
import time
from PyQt5 import QtCore

class WriteDeviceThread(QtCore.QThread):
    write = QtCore.pyqtSignal(bool)
    exception = QtCore.pyqtSignal(str)
    
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

                self.write.emit(True)
            except:
                self.exception.emit("Write Failed. Device disconnected.")
        return
