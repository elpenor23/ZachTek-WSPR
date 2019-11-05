#!/usr/bin/python3
import time
from PyQt5 import QtCore
from obj.ReadDeviceThread import ReadDeviceThread
from obj.WriteDeviceThread import WriteDeviceThread

class DeviceCommunicationThread(QtCore.QThread):
    display = QtCore.pyqtSignal(str)
    update = QtCore.pyqtSignal(str)
    realtime = QtCore.pyqtSignal(str)
    exception = QtCore.pyqtSignal(str)
    
    
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
        
        self

    ###################################
    #START - Thread handling
    ###################################
    def run(self):
        #Setup other threads
        self.readDeviceThread = ReadDeviceThread(self.wsprDevice)
        self.readDeviceThread.read.connect(self.callbackDeviceRead)
        self.readDeviceThread.exception.connect(self.callbackThreadException)
        self.readDeviceThread.start()

        self.writeDeviceThread = WriteDeviceThread(self.wsprDevice)
        self.writeDeviceThread.write.connect(self.callbackDeviceWrite)
        self.writeDeviceThread.exception.connect(self.callbackThreadException)
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

    def sendCommand(self, commandType, commands, values = []):
        while self.readDeviceThread is None:
            time.sleep(.1)
        self.readDeviceThread.pause()
        self.writeDeviceThread.sendCommand(commandType, commands, values)
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
            self.display.emit(returnText)
            
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
            self.update.emit("")
            
        if responce in self.wsprDevice.config.deviceconstants.commands.responcestoload:
            if responce == self.wsprDevice.config.deviceconstants.commands.responce.bands:
                self.processBands(responce, value)
            else:
                self.update.emit(responce + "," + value)
                
        if responce in self.wsprDevice.config.deviceconstants.commands.realtimeresponces:
            self.returnRealTimeDataToUI(responce, value)
        
        if not self.wsprDevice.config.debug and responce in self.wsprDevice.config.deviceconstants.commands.alwaysdisplayresponces:
            self.display.emit(returnText)
        return
    
    def callbackThreadException(self, error):
        self.exception.emit(error)
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
            self.realtime.emit(responce + "," + value)
            
    def returnGPSSignalDataAverage(self):
        returnValue = self.wsprDevice.config.deviceconstants.commands.responce.gpssatdata + "," + str(self.gpsDataSignalAverage)
        self.realtime.emit(returnValue)
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
        #create the array of GPS signals to average
        if len(self.gpsDataSignalData) < 4:
            self.gpsDataSignalData.append(newGPSSignalData)
        else:
            itemToRemove = 101
            for val in self.gpsDataSignalData:
                aryVal = int(val)
                if newGPSSignalData > aryVal:
                    if aryVal < itemToRemove:
                        itemToRemove = aryVal
                        
            if itemToRemove < 101:
                self.gpsDataSignalData.remove(itemToRemove)
                self.gpsDataSignalData.append(newGPSSignalData)

        #now calculate the average
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
        bandValue = value.split()[1]
        if len(self.wsprDevice.bands)-1 >= self.bandIndex:
            self.wsprDevice.bands[self.bandIndex][2] = bandValue
            self.bandIndex += 1
        
        return
    ###################################
    #END - Internal Methods
    ###################################