#!/usr/bin/python3
# This file holds all the interfaces with the wspr device

import serial
import getpass
import serial.tools.list_ports
from datetime import datetime
from obj.ErrorObjects import logError, ErrorLevel
import time
import random
import os
import enum

class WSPRInterfaceManager:

    ###########################################
    # START - Get Methods
    ###########################################
    def getCallSign(self, port, deviceconstants):
        command = self.createCommand(deviceconstants.commands, CommandType.GET, Command.CALLSIGN)
        self.sendCommand(port, command)
        return

    def getStartUpMode(self, port, deviceconstants):
        command = self.createCommand(deviceconstants.commands, CommandType.GET, Command.STARTUPMODE)
        self.sendCommand(port, command)
        return
    
    def getCurrentMode(self, port, deviceconstants):
        command = self.createCommand(deviceconstants.commands, CommandType.GET, Command.CURRENTMODE)
        self.sendCommand(port, command)
        return

    def getPower(self, port, deviceconstants):
        command = self.createCommand(deviceconstants.commands, CommandType.GET, Command.POWER)
        self.sendCommand(port, command)
        return

    def getGeneratorFequency(self, port, deviceconstants):
        command = self.createCommand(deviceconstants.commands, CommandType.GET, Command.GENERATORFREQUENCY)
        self.sendCommand(port, command)
        return
    
    def getBands(self, port, deviceconstants):
        command = self.createCommand(deviceconstants.commands, CommandType.GET, Command.BANDS)
        self.sendCommand(port, command)
        return
    ###########################################
    # END - Get Methods
    ###########################################
    
    ###########################################
    # START - Set Methods
    ###########################################  
    def setBands(self, port, bands):
        return True

    def setStartupMode(self, port, mode):
        return True
    
    def setCurrentMode(self, port, bands):
        return True

    def setCallsign(self, port, bands):
        return True
    ###########################################
    # END - Get Methods
    ###########################################

    ###########################################
    # START - Port Functions
    ###########################################
    #detect which port the wspr transmitter is on
    def detectTransmitter(self, portList, checkSecurity, securityErrorMessage, correctResponce, portReadTimeout):
        connectedPort = None
        responce = ""
        for portName in portList:
            serialPort = self.openSerialPort(portName, portReadTimeout)
            responceBytes = serialPort.readline()
            responce = responceBytes.decode("utf-8")
            if responce.startswith(correctResponce):
                connectedPort = serialPort
                break
        
        #check security if necessary
        if connectedPort is not None and checkSecurity:
            security = os.access(connectedPort.port, os.R_OK|os.W_OK)
            if not security:
                errMsg = securityErrorMessage.format(getpass.getuser())
                logError(ErrorLevel.HIGH, errMsg)
                connectedPort = None
        returnTuple = (connectedPort, responce.replace("\r\n", ""))
        return returnTuple
        
    def openSerialPort(self, portName, readTimeoutSeconds):
        port = None
        try:
            port = serial.Serial(portName)
        except Exception as ex:
            errorText = "Failed to connect to port: " + portName
            logError(ErrorLevel.HIGH, errorText, ex)

        if port is not None:
            #print(port)
            port.timeout = readTimeoutSeconds

        return port

    def readSerialPort(self, port):
        responce = ""
        responce = port.readline()
        return responce.decode("utf-8")

    def GetPortList(self):
        ports = []
        rawPorts = serial.tools.list_ports.comports(True)
        for port in rawPorts:
            if port.description != "n/a":
                #print("Port: " + port.description)
                ports.append(port.device)
    
        return ports
    ###########################################
    # END - Port Functions
    ###########################################
    #creates commands to send to the device
    def createCommand(self, commands, type, command):
        commandString = ""
        
        if command == Command.CALLSIGN:
            commandString = commands.get.callsign
        elif command == Command.BANDS:
            commandString = commands.get.bands
        elif command == Command.STARTUPMODE:
            commandString = commands.get.startupmode
        elif command == Command.CURRENTMODE:
            commandString = commands.get.currentmode
        elif command == Command.POWER:
            commandString = commands.get.power
        elif command == Command.GENERATORFREQUENCY:
            commandString = commands.get.generatorfrequency 
        else:
            print("Unknown Command!")
        #ELIF for next command

        if type == CommandType.GET:
                commandString += commands.get.char + commands.commandEndChars
        elif type == CommandType.SET:
            commandString += commands.set.char + commands.commandEndChars
        
        return commandString.encode("utf-8")
    
    def sendCommand(self, ser, commandToSend):
        self.waitForPort(ser)
        ser.write(commandToSend)
        return
    
    def waitForPort(self, ser):
        while not ser.inWaiting():
            time.sleep(.1)
        return

class CommandType(enum.Enum):
    GET = 1
    SET = 2
    RESPONCE = 3

class Command(enum.Enum):
    CALLSIGN = 1
    BANDS = 2
    STARTUPMODE = 3
    CURRENTMODE = 4
    POWER = 5
    GENERATORFREQUENCY = 6
