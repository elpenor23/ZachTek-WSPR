#!/usr/bin/python3
import time
from PyQt5 import QtCore
import serial

class ReadDeviceThread(QtCore.QThread):
    read = QtCore.pyqtSignal(str)
    exception = QtCore.pyqtSignal(str)
    
    def __init__(self, wsprDevice):
        QtCore.QThread.__init__(self)
        self.wsprDevice = wsprDevice
        self.keep_going = True
        self.paused = False

    def run(self):
        #keep reading from the device while it is still there
        while self.keep_going:
            time.sleep(self.wsprDevice.config.deviceconstants.waitBetweenCommandsInSeconds)
            if not self.paused:
                try:
                    data = self.wsprDevice.ReadData().replace(self.wsprDevice.config.deviceconstants.commands.commandEndChars, "")
                    self.read.emit(data)
                except serial.serialutil.SerialException:
                    self.paused = True
                    if self.wsprDevice.port is not None:
                        self.wsprDevice.port.close()
                    self.exception.emit("Read Failed. Device disconnected.")
                
        return

    def stop(self):
        self.keep_going = False
        self.wait()
        self.exit()
        return

    def pause(self):
        self.paused = True
        return
    
    def resume(self):
        self.paused = False
        return

    