#!/usr/bin/python3
import time
from PySide2 import QtCore
import serial

class ReadDeviceThread(QtCore.QThread):
    def __init__(self, wsprDevice):
        QtCore.QThread.__init__(self)
        self.wsprDevice = wsprDevice
        self.keep_going = True
        self.paused = False

    def run(self):
        #keep reading from the device while it is still there
        while self.keep_going:
            time.sleep(.1)
            if not self.paused:
                try:
                    data = self.wsprDevice.ReadData().replace("\r\n", "")
                    self.emit( QtCore.SIGNAL('read(QString)'), data)
                except serial.serialutil.SerialException:
                    self.paused = True
                    self.emit( QtCore.SIGNAL('exception(QString)'), "Read Failed. Device disconnected.")
                
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

    