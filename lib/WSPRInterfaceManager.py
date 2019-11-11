#!/usr/bin/python3
# This file holds all the interfaces with the wspr device

import serial
import getpass
import serial.tools.list_ports
from datetime import datetime
from obj.ErrorObjects import logError, ErrorLevel
from obj.CommandEnums import CommandType, Command
import time
import random
import os

class WSPRInterfaceManager:
    ###########################################
    # START - Port Functions
    ###########################################
    #detect which port the wspr transmitter is on
    def detectTransmitter(self, portList, checkSecurity, securityErrorMessage, correctResponce, portReadTimeout, commandEndChars):
        connectedPort = None
        responce = ""
        for portName in portList:
            serialPort = self.openSerialPort(portName, portReadTimeout)
            responceBytes = serialPort.readline()
            try:
                responce = responceBytes.decode("utf-8")
            except Exception as ex:
                logError(ErrorLevel.MODERATE, "Bad Start Byte.", ex)
                print(responceBytes)
                print("Exception: " + str(ex))
                responce = "ERROR"
                
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
        returnTuple = (connectedPort, responce.replace(commandEndChars, ""))
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
    def createCommand(self, commands, type, command, value = ""):
        commandString = ""
        #print(command)
        if command == Command.CALLSIGN:
            commandString = commands.get.callsign
        elif command == Command.BANDS:
            commandString = commands.get.bands
        elif command == Command.STARTUP_MODE:
            commandString = commands.get.startupmode
        elif command == Command.CURRENT_MODE:
            commandString = commands.get.currentmode
        elif command == Command.POWER:
            commandString = commands.get.power
        elif command == Command.GENERATOR_FREQUENCY:
            commandString = commands.get.generatorfrequency
        elif command == Command.FACTORY_FREQUENCY_REFERENCE_OSCILLATOR_FREQUENCY:
            commandString = commands.get.factoryreferenceoscillatorfrequency
        elif command == Command.FACTORY_HARDWARE_REVISION:
            commandString = commands.get.factoryhardwarerevision
        elif command == Command.FACTORY_HARDWARE_VERSION:
            commandString = commands.get.factoryhardwareversion
        elif command == Command.FACTORY_PRODUCT_NUMBER:
            commandString = commands.get.factoryproductnumber
        elif command == Command.FACTORY_SOFTWARE_REVISION:
            commandString = commands.get.factorysoftwarerevision
        elif command == Command.FACTORY_SOFTWARE_VERSION:
            commandString = commands.get.factorysoftwareversion
        elif command == Command.FACTORY_LOWPASS_FINTER_INSTALLED:
            commandString = commands.get.factorylowpassfilterinstalled

        elif command == Command.SAVE:
            commandString = commands.set.save
        #ELIF for next command
        else:
            print("Unknown Command!")
        #print(commandString)
        if type == CommandType.GET:
                commandString += commands.get.char + commands.commandEndChars
        elif type == CommandType.SET:
            commandString += commands.set.char + " " + value + " " + commands.commandEndChars
        
        #print("Created Command: " + commandString)
        return commandString.encode("utf-8")
    
    def sendCommand(self, ser, commands, commandType, command, waitTime, value = ""):
        commandToSend = self.createCommand(commands, commandType, command, value)
        self.waitForPort(ser, waitTime)
        ser.write(commandToSend)
        return
    
    def waitForPort(self, ser, waitTime):
        while not ser.inWaiting():
            time.sleep(waitTime)
        return
