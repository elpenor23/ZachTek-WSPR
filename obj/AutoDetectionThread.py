#!/usr/bin/python3
import time
from PySide2 import QtCore

class AutoDetectionThread(QtCore.QThread):
    def __init__(self, wsprDevice):
        QtCore.QThread.__init__(self)
        self.wsprDevice = wsprDevice
        self.keep_going = True
        self.paused = False

    def run(self):
        #keep checking for devices being plugged or un plugged
        while self.keep_going:
            if self.wsprDevice.port is None and not self.paused:
                returnPort = None
                #if we don't have a port check to see if one showed up
                if len(self.wsprDevice.allPorts) > 0:
                    data = self.wsprDevice.DetectPort()
                    returnPort = data[0]
                    returnMessage = data[1]
                    if returnPort is not None:
                        self.wsprDevice.port = returnPort
                        self.paused = True         
                        self.emit( QtCore.SIGNAL('port(QString)'), returnPort.port)
                        self.emit( QtCore.SIGNAL('read(QString)'), returnMessage)
            time.sleep(2)
        return

    def stop(self):
        self.keep_going = False
        self.wait()
        self.exit()
        return

    def resume(self):
        self.paused = False
        return

    def pause(self):
        self.paused = True
        return