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
                #loop through and send all the commands
                for command in commandArray:
                    if commandType == CommandType.GET:
                        self.wsprDevice.WriteCommand(commandType, command)
                    else:
                        self.wsprDevice.WriteCommand(commandType, command, valueArray[i])
                        i += 1
                    time.sleep(self.wsprDevice.config.deviceconstants.waitBetweenCommandsInSeconds)
                
                #if we are setting stuff we need to save it all
                if commandType == CommandType.SET:
                    self.wsprDevice.WriteCommand(CommandType.SET, Command.SAVE)

                self.write.emit(True)
            except Exception as ex:
                self.pause()
                print(ex)
                if self.wsprDevice.port is not None:
                    self.wsprDevice.port.close()
                self.exception.emit("Write Failed. Device disconnected.")
        return
    
