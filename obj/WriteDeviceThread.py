#!/usr/bin/python3
import time
from PyQt5 import QtCore
from obj.CommandEnums import CommandType, Command

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

    def sendCommand(self, commandType, commandArray, valueArray = []):
        if not self.paused:
            i = 0
            try:
                for command in commandArray:
                    if commandType == CommandType.GET:
                        self.wsprDevice.WriteCommand(commandType, command)
                    else:
                        self.wsprDevice.WriteCommand(commandType, command, valueArray[i])
                        self.wsprDevice.WriteCommand(CommandType.SET, Command.SAVE)
                        i += 1
                    
                self.write.emit(True)
            except Exception as ex:
                self.exception.emit("Write Failed. Device disconnected.")
        return
    
