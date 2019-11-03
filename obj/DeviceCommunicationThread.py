#!/usr/bin/python3
import time
from PySide2 import QtCore
from obj.ReadDeviceThread import ReadDeviceThread
from obj.WriteDeviceThread import WriteDeviceThread

class DeviceCommunicationThread(QtCore.QThread):
    def __init__(self, wsprDevice):
        QtCore.QThread.__init__(self)
        self.wsprDevice = wsprDevice
        self.keep_going = True
        self.readDeviceThread = None
        self.writeDeviceThread = None
        self.gpsDataOnging = False
        self.gpsDataSignalTotal = 0
        self.gpsDataSignalAverage = 0
        self.gpsDataSignalData = []
        self.bandsDataOngoing = False
        self.bandIndex = 0

    ###################################
    #START - Thread handling
    ###################################
    def run(self):
        #Setup other threads
        self.readDeviceThread = ReadDeviceThread(self.wsprDevice)
        self.connect( self.readDeviceThread, QtCore.SIGNAL("read(QString)"), self.callbackDeviceRead )
        self.connect( self.readDeviceThread, QtCore.SIGNAL("exception(QString)"), self.callbackThreadException )
        self.readDeviceThread.start()

        self.writeDeviceThread = WriteDeviceThread(self.wsprDevice)
        self.connect( self.writeDeviceThread, QtCore.SIGNAL("write(bool)"), self.callbackDeviceWrite )
        self.connect( self.writeDeviceThread, QtCore.SIGNAL("exception(QString)"), self.callbackThreadException )
        self.writeDeviceThread.start()
        return

    def stop(self):
        self.readDeviceThread.stop()
        self.writeDeviceThread.stop()
        self.readDeviceThread.wait()
        self.writeDeviceThread.wait()
        self.wait()
        self.exit()
        return
    
    def pause(self):
        self.readDeviceThread.pause()
        self.writeDeviceThread.pause()
        return

    def resume(self):
        self.readDeviceThread.resume()
        self.writeDeviceThread.resume()
        return

    def writeCommand(self, command):
        while self.readDeviceThread is None:
            time.sleep(.1)
        self.readDeviceThread.pause()
        self.writeDeviceThread.writeCommand(command)
    ###################################
    #END - Thread handling
    ###################################
    
    ###################################
    #START - Thread Callbacks
    ###################################
    def callbackDeviceWrite(self, success):
        self.readDeviceThread.resume()
        return

    def callbackDeviceRead(self, returnText):
        if self.wsprDevice.config.debug:
            self.emit( QtCore.SIGNAL('display(QString)'), returnText)

        responce = ""
        value = ""
        splitReturn = returnText.split(" ", 1)
        if len(splitReturn) > 1:
            responce = splitReturn[0].strip()
            value = splitReturn[1].strip()
        
        #Averaging All the GPS data together
        if responce != self.wsprDevice.config.deviceconstants.commands.responce.gpssatdata and self.gpsDataOnging:
            self.returnGPSSignalDataAverage()
        #return the bands when we can
        if responce != self.wsprDevice.config.deviceconstants.commands.responce.bands and self.bandsDataOngoing:
            self.bandsDataOngoing = False
            self.bandIndex = 0
            self.emit( QtCore.SIGNAL('update(QString)'), "")

        if responce in self.wsprDevice.config.deviceconstants.commands.responcestoload:
            if responce == self.wsprDevice.config.deviceconstants.commands.responce.bands:
                self.processBands(responce, value)
            else:
                self.emit( QtCore.SIGNAL('update(QString)'), responce + "," + value)

        if responce in self.wsprDevice.config.deviceconstants.commands.realtimeresponces:
            self.returnRealTimeDataToUI(responce, value)
        
        if not self.wsprDevice.config.debug and responce in self.wsprDevice.config.deviceconstants.commands.alwaysdisplayresponces:
            self.emit( QtCore.SIGNAL('display(QString)'), returnText)
        return
    
    def callbackThreadException(self, error):
        self.emit( QtCore.SIGNAL('exception(QString)'), error)
    ###################################
    #END - Thread Callbacks
    ###################################

    ###################################
    #START - Return Data
    ###################################
    def returnRealTimeDataToUI(self, responce, value):
        if responce == self.wsprDevice.config.deviceconstants.commands.responce.gpssatdata:
            self.gpsDataOnging = True
            self.updateAverageGPSData(value.split()[3])
        else:
            self.emit( QtCore.SIGNAL('realtime(QString)'), responce + "," + value)

    def returnGPSSignalDataAverage(self):
        returnValue = self.wsprDevice.config.deviceconstants.commands.responce.gpssatdata + "," + str(self.gpsDataSignalAverage)
        self.emit( QtCore.SIGNAL('realtime(QString)'), returnValue)
        self.gpsDataOnging = False
        self.gpsDataSignalAverage = 0
        self.gpsDataSignalData = []
        self.gpsDataSignalTotal = 0
    ###################################
    #END - Return Data
    ###################################

    ###################################
    #START - Internal Methods
    ###################################
    def updateAverageGPSData(self, newSignalData):
        newGPSSignalData = int(newSignalData)
        if len(self.gpsDataSignalData) < 4:
            self.gpsDataSignalData.append(newGPSSignalData)
        else:
            itemToRemove = 0
            for val in self.gpsDataSignalData:
                data = int(val)
                if newGPSSignalData > data:
                    if itemToRemove > data:
                        itemToRemove = data
            if itemToRemove > 0:
                self.gpsDataSignalData.remove(itemToRemove)
                self.gpsDataSignalData.append(newGPSSignalData)

        #now do calculate the average
        totalData = 0
        dataCount = 0
        for data in self.gpsDataSignalData:
            totalData += int(data)
            dataCount += 1
        
        self.gpsDataSignalTotal = totalData
        if dataCount > 0:
            self.gpsDataSignalAverage = totalData/dataCount
        else:
            self.gpsDataSignalAverage = 0

        return
    
    def processBands(self, responce, value):
        self.bandsDataOngoing = True
        if len(self.wsprDevice.bands)-1 >= self.bandIndex:
            self.wsprDevice.bands[self.bandIndex][1] = value
            self.bandIndex += 1
        
        return
    ###################################
    #END - Internal Methods
    ###################################