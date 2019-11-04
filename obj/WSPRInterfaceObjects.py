#!/usr/bin/python3
#This object is used by the GUI to get and hold information
#from the WSPR device that it needs to display.
#all calls to the WSPR device should come through here.
#This will allow us to swap out the manager if we ever want to 
#connect this to a different WSPR device
from lib.WSPRInterfaceManager import WSPRInterfaceManager
from obj.ErrorObjects import logError, ErrorLevel
from obj.ConfigurationObjects import ConfigObject
import enum
import os
import time

class Mode (enum.Enum):
    SignalGenerator = 1
    WSPRMode = 2
    Idle = 3

#main object
class WSPRInterfaceObject:
    def __init__(self, configurationFile):
        logError(ErrorLevel.LOW, "*********** START UP *****************")
        
        #Get config object using passed in config file
        self.config = ConfigObject(configurationFile)

        #User the interface manager for all interfaces with the actual wspr device
        self.WSPRInterfaceManager = WSPRInterfaceManager()

        #Object properties we need to take care of
        self._bands = []
        self._callsign = ""
        self._currentMode = Mode
        #self._liveSignalModeFrequency = ""
        self._startupMode = Mode
        self.power = ""
        self.generatorfrequency = ""
        #self._GPSStatus = 0
        #self._wsprTime = ""
        self._port = None
        self.bands = self.config.bands
        self.gpsposition = "0000"
        self.gpstime = ""
        
        #DEBUG: Printing config so we know what is in there
        #self.config.print()
        return
        
    def print(self):
        print("Port:" + self._port)
        print("Bands:")
        print(self._bands)
        print("Callsign: " + self._callsign)
        #print("Startup Mode: " + self.startUpMode)
        #print("Live Mode:" + self.liveMode)
        #print("Live Signal Mode Frequency:" + self.liveSignalModeFrequency)
        #print("GPS Status:" + self.GPSStatus)
        #print("WSPR Time:" + self.wsprTime)

    #########################################
    # Properties
    ########################################
    #Port getters and setters
    def get_port(self):
        return self._port
    
    def set_port(self,p):
        self._port = p

    def del_port(self):
        self._port = None

    port = property(get_port, set_port, del_port, "This is documentation")

    #Bands getters and setters 
    def get_bands(self):
        return self._bands
    
    def set_bands(self, b):
        self._bands = b
    
    def del_bands(self):
        #disable all bands
        for band in self.bands:
            band[1] = "D"

    bands = property(get_bands, set_bands, del_bands)

    #Callsign getters and setters
    def get_callsign(self):
        return self._callsign
    
    def set_callsign(self, c):
        self._callsign = c
    
    def del_callsign(self):
        self._callsign = ""

    callsign = property(get_callsign, set_callsign, del_callsign)

    #Startup Mode getters and setters
    def get_startupmode(self):
        return self._startupMode
    
    def set_startupMode(self, smode):
        self._startupMode = smode

    startupMode = property(get_startupmode, set_startupMode)

    #current Mode getters and setters
    def get_currentmode(self):
        return self._currentMode
    
    def set_currentMode(self, cmode):
        self._currentMode = cmode

    currentMode = property(get_currentmode, set_currentMode)

    #Port List getter
    def get_portList(self):
        ports = []
        if self.config.useAutomaticPorts:
            ports = self.WSPRInterfaceManager.GetPortList()
        else:
            ports = self.config.manualPorts
        return ports

    allPorts = property(get_portList)

    ############################
    #END Properties
    ############################

    ############################
    #Start Methods
    ############################
    def DetectPort(self):
        #print(self.allPorts)
        return self.WSPRInterfaceManager.detectTransmitter(self.allPorts,
                                                           self.config.checkSecurity,
                                                           self.config.securityErrorMessage,
                                                           self.config.deviceconstants.commands.responce.deviceinfo,
                                                           self.config.readDeviceTimeout,
                                                           self.config.deviceconstants.commands.commandEndChars)

    def ReadData(self):
        data = self.WSPRInterfaceManager.readSerialPort(self.port)
        return data
    
    def WriteCommand(self, commandType, command):
        self.WSPRInterfaceManager.sendCommand(self.port, self.config.deviceconstants.commands, commandType, command)
        return
    ###########################
    #END Methods
    ###########################