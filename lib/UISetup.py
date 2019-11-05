#!/usr/bin/python3
#Creates and sets up the GUI
#This is what controls all the GUI and connects things to the 
#interface
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QWidget, QProgressBar, QLabel, QLineEdit, QRadioButton,
            QPlainTextEdit, QGridLayout, QGroupBox, QCheckBox, QPushButton, QSizePolicy)
from obj.WSPRInterfaceObjects import WSPRInterfaceObject
from obj.AutoDetectionThread import AutoDetectionThread
from obj.DeviceCommunicationThread import DeviceCommunicationThread
from obj.CommandEnums import CommandType, Command
import ast

class WSPRUI(QWidget):
    def __init__(self, configFile):
        super(WSPRUI, self).__init__()

        #Things that we need to keep track of to update
        self.wsprDevice = WSPRInterfaceObject(configFile)
        
        self.bandCheckboxes = []
        self.CurrentGPSStatus = QProgressBar(self)
        self.gpsTime = QLabel("00:00:00")
        self.gpsPosition = QLabel("0000")
        self.gpsPower = QLabel("0")
        self.outputFreq = QLabel("000 000 000.00")
        self.gpsLocked = QLabel("GPS Signal Quality:")
        
        self.portConnectionIcon = QLabel()
        self.portConnectionIcon.setFixedSize(50, 50)
        self.portConnectionIcon.mousePressEvent = self.handleConnectionIconClick

        self.portActive = False

        self.txtCallsign = QLineEdit()

        self.portConnectionLabel = QLabel(self.wsprDevice.config.notconnectedtext)

        self.rdoStartUpSignalGen = QRadioButton("Signal Generator")
        self.rdoStartUpWSPRBeacon = QRadioButton("WSPR Beacon")
        self.rdoStartUpIdle = QRadioButton("Idle")

        self.rdoCurrentSignalGen = QRadioButton("Signal Generator")
        self.rdoCurrentWSPRBeacon = QRadioButton("WSPR Beacon")
        self.rdoCurrentIdle = QRadioButton("Idle")

        self.textArea = QPlainTextEdit()
        
        self.commandArray = [Command.CALLSIGN,
                             Command.BANDS,
                             Command.STARTUPMODE,
                             Command.CURRENTMODE,
                             Command.POWER,
                             Command.GENERATORFREQUENCY]
        #Create the UI
        self.initUI()
        
        #Threads
        self.createThreads()
    
    #####################################
    #Start - Build All section of the UI
    #####################################
    #Add all the sections to the main window 
    def initUI(self):

        windowLayout = QGridLayout()

        #serial port section
        serialPort = self.initSerialPortFrame()
        windowLayout.addWidget(serialPort, 0, 0)
        
        #Bands Section
        bands = self.initBandsFrame()
        windowLayout.addWidget(bands, 1, 0)

        #callsign section
        callsign = self.initCallsignFrame()
        windowLayout.addWidget(callsign, 0, 1)
        
        #Button Section
        button = self.initButtonFrame()
        windowLayout.addWidget(button, 2, 0)

        #Startup Config
        startup = self.initStartupModeFrame()
        windowLayout.addWidget(startup, 2, 1)

        #Current Status
        current =  self.initCurrentStatus()
        windowLayout.addWidget(current, 1, 1)

        #Debug Area
        debug = self.initDebugSection()
        windowLayout.addWidget(debug, 0,2, 3,1)

        #Set the layout and window
        self.setLayout(windowLayout)
        self.move(300, 150)
        self.setWindowTitle(self.wsprDevice.config.name + " " + self.wsprDevice.config.version)    
        self.show()

    #Build section with port information
    def initSerialPortFrame(self):
        sectionBox = QGroupBox("Serial Port")
        tempLayout = QGridLayout()

        self.setConnectionStatus()

        tempLayout.addWidget(self.portConnectionIcon,0,0)
        tempLayout.addWidget(self.portConnectionLabel, 1, 0)
        tempLayout.setAlignment(QtCore.Qt.AlignHCenter)
        sectionBox.setLayout(tempLayout)
        return sectionBox

    #create section for Band information
    def initBandsFrame(self):
        sectionBox = QGroupBox("Bands")
        tempLayout = QGridLayout()
        
        i=0
        for band in self.wsprDevice.bands:
            #for each band make a label and a button
            checkbox = QCheckBox(band[1])            
            tempLayout.addWidget(checkbox, i, 1)
            self.bandCheckboxes.append(checkbox)
            i+=1

        sectionBox.setLayout(tempLayout)
        return sectionBox

    #Create section for buttons
    def initButtonFrame(self):
        sectionBox = QGroupBox("Buttons")
        tempLayout = QGridLayout()
        buttonReload = QPushButton("Reload")
        buttonReload.setFixedSize(100, 50)
        buttonReload.clicked.connect(self.handleReloadPush)

        buttonSave = QPushButton("Save")
        buttonSave.setFixedSize(100, 50)
        buttonSave.clicked.connect(self.handleSavePush)
        

        tempLayout.addWidget(buttonReload, 0, 0)
        tempLayout.addWidget(buttonSave, 0, 1)
        sectionBox.setLayout(tempLayout)
        return sectionBox

    #create setion for Callsign input
    def initCallsignFrame(self):
        sectionBox = QGroupBox("Callsign")
        tempLayout = QGridLayout()
        
        tempLayout.addWidget(self.txtCallsign)
        sectionBox.setLayout(tempLayout)
        return sectionBox

    #Create startup mode frame
    def initStartupModeFrame(self):
        sectionBox = QGroupBox("Start Up Configuration")
        tempLayout = QGridLayout()
        
        tempLayout.addWidget(self.rdoStartUpSignalGen, 0, 0)
        tempLayout.addWidget(self.rdoStartUpWSPRBeacon, 1, 0)
        tempLayout.addWidget(self.rdoStartUpIdle, 2, 0)

        sectionBox.setLayout(tempLayout)
        return sectionBox

    #Create current status section
    def initCurrentStatus(self):
        sectionBox = QGroupBox("Current Status")
        tempLayout = QGridLayout()

        #GPS Signal
        tempLayout.addWidget(self.gpsLocked, 1, 0, 1, 3)

        self.CurrentGPSStatus.setTextVisible(True)
        self.CurrentGPSStatus.setValue(0)
        tempLayout.addWidget(self.CurrentGPSStatus, 2, 0, 1, 3)

        #GPS Time
        gpsTimeLabel = QLabel("GPS Time:")
        tempLayout.addWidget(gpsTimeLabel, 3, 0)
        tempLayout.addWidget(self.gpsTime, 3, 1, 1, 2)

        #GPS Position
        gpsPositionLabel = QLabel("GPS Position:")
        tempLayout.addWidget(gpsPositionLabel, 4, 0)
        tempLayout.addWidget(self.gpsPosition, 4, 1, 1, 3)

        #Power
        gpsPowerLabel = QLabel("Reported Power: ")
        tempLayout.addWidget(gpsPowerLabel, 5, 0)
        tempLayout.addWidget(self.gpsPower, 5, 1)
        gpsdBmLabel = QLabel("dBm")
        tempLayout.addWidget(gpsdBmLabel, 5, 2)

        #Output Frequency
        gpsPowerLabel = QLabel("Output Frequency: ")
        tempLayout.addWidget(gpsPowerLabel, 6, 0)
        tempLayout.addWidget(self.outputFreq, 6, 1)
        gpsdBmLabel = QLabel("Hz")
        tempLayout.addWidget(gpsdBmLabel, 6, 2)

        tempLayout.addWidget(self.rdoCurrentSignalGen, 7, 0, 1, 2)
        tempLayout.addWidget(self.rdoCurrentWSPRBeacon, 8, 0, 1, 2)
        tempLayout.addWidget(self.rdoCurrentIdle, 9, 0, 1, 2)

        #Signal Frequency
        tempLayout.setAlignment(QtCore.Qt.AlignTop)
        sectionBox.setLayout(tempLayout)
        return sectionBox        

    def initDebugSection(self):
        sectionBox = QGroupBox("Debug")
        tempLayout = QGridLayout()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.textArea.setSizePolicy(sizePolicy)
        self.textArea.setFixedWidth(400)
        tempLayout.addWidget(self.textArea)

        sectionBox.setLayout(tempLayout)
        return sectionBox

    #####################################
    #END - Build All section of the UI
    #####################################

    #####################################
    #START - UI Data Changes
    #####################################

    #Set the connection status based on 
    #the port information set by the connection process
    def setConnectionStatus(self):
        connected = self.wsprDevice.port is not None
        #print(str(self.wsprDevice.port))
        fileName = ""
        toolTip = ""
        if connected:
            fileName = self.wsprDevice.config.icons["connected"]
            toolTip = self.wsprDevice.config.connectedtext + str(self.wsprDevice.port.port)
        else:
            fileName = self.wsprDevice.config.icons["disconnected"]
            toolTip = self.wsprDevice.config.notconnectedtext

        self.portConnectionLabel.setText(toolTip)
        pixMap = QtGui.QPixmap(fileName)

        self.portConnectionIcon.setPixmap(pixMap)
        self.portConnectionIcon.setToolTip(toolTip)

        return

    #fills all GUI fields with data from the wspr device
    def FillData(self):
        self.txtCallsign.setText(self.wsprDevice.callsign)
        if self.wsprDevice.generatorfrequency is not None:
            gHz = self.wsprDevice.generatorfrequency[0:1]
            decimals = self.wsprDevice.generatorfrequency[10:12]
            mainDigits = self.wsprDevice.generatorfrequency[1:10]
            formattedFreq = gHz + " " + ' '.join([mainDigits[i:i+3] for i in range(0, len(mainDigits), 3)]) + "." + decimals
            self.outputFreq.setText(formattedFreq)

        self.gpsPower.setText(self.wsprDevice.power)

        #set the checkboxes
        for i, checkbox in enumerate(self.bandCheckboxes):
            checkbox.setChecked(self.wsprDevice.bands[i][2] == self.wsprDevice.config.deviceconstants.bandEnabledChar)

        if self.wsprDevice.startupMode == "S":
            self.rdoStartUpSignalGen.setChecked(True)
        elif self.wsprDevice.startupMode == "W":
            self.rdoStartUpWSPRBeacon.setChecked(True)
        elif self.wsprDevice.startupMode == "N":
            self.rdoStartUpIdle.setChecked(True)

        if self.wsprDevice.currentMode == "S":
            self.rdoCurrentSignalGen.setChecked(True)
        elif self.wsprDevice.currentMode == "W":
            self.rdoCurrentWSPRBeacon.setChecked(True)
        elif self.wsprDevice.currentMode == "N":
            self.rdoCurrentIdle.setChecked(True)

        return

    #clear all GUI fields with data from the wspr device
    def ClearData(self):
        self.txtCallsign.setText("")
        
        for i, checkbox in enumerate(self.bandCheckboxes):
            checkbox.setChecked(False)

        self.rdoStartUpSignalGen.setChecked(False)
        self.rdoStartUpWSPRBeacon.setChecked(False)
        self.rdoStartUpIdle.setChecked(True)

        self.rdoCurrentSignalGen.setChecked(False)
        self.rdoCurrentWSPRBeacon.setChecked(False)
        self.rdoCurrentIdle.setChecked(True)

        return

    #####################################
    #END - UI Data Changes
    #####################################

    #####################################
    #START - UI Event Handlers
    #####################################
    def handleConnectionIconClick(self, arg2 = None):
        if self.wsprDevice.config.debug:
            self.wsprDevice.config.debug = False
        else:
            self.wsprDevice.config.debug = True
        return

    def handleReloadPush(self):
        self.deviceCommunicationThread.sendCommand(CommandType.GET, self.commandArray)
        return
    
    def handleSavePush(self):
        commands = [Command.CURRENTMODE,
                    Command.STARTUPMODE,
                    Command.CALLSIGN
                    ]
        startUpModeValue = ""
        if self.rdoStartUpIdle.isChecked():
            startUpModeValue = self.wsprDevice.config.deviceconstants.modeIdleChar
        if self.rdoStartUpSignalGen.isChecked():
            startUpModeValue = self.wsprDevice.config.deviceconstants.modeSignalChar
        if self.rdoStartUpWSPRBeacon.isChecked():
            startUpModeValue = self.wsprDevice.config.deviceconstants.modeWSPRChar
        
        currentModeValue = ""
        if self.rdoCurrentIdle.isChecked():
            currentModeValue = self.wsprDevice.config.deviceconstants.modeIdleChar
        if self.rdoCurrentSignalGen.isChecked():
            currentModeValue = self.wsprDevice.config.deviceconstants.modeSignalChar
        if self.rdoStartUpWSPRBeacon.isChecked():
            currentModeValue = self.wsprDevice.config.deviceconstants.modeWSPRChar

        values = [currentModeValue,
                    startUpModeValue,
                    self.txtCallsign.text()
                ]
        
        for i, checkbox in enumerate(self.bandCheckboxes):
            commands.append(Command.BANDS)
            if checkbox.isChecked():
                checkboxValue = self.wsprDevice.config.deviceconstants.bandEnabledChar
            else:
                checkboxValue = self.wsprDevice.config.deviceconstants.bandDisabledChar

            valueToSend = str(i).zfill(2) + " " + checkboxValue
            values.append(valueToSend)

        self.deviceCommunicationThread.sendCommand(CommandType.SET, commands, values)

        self.wsprDevice.callsign = self.txtCallsign.text()
        self.wsprDevice.startupMode = startUpModeValue
        self.wsprDevice.currentMode = currentModeValue
        #self.deviceCommunicationThread.sendCommand(CommandType.GET, commands)
        
        return

    #####################################
    #END - UI Event Handlers
    #####################################

    #####################################
    #START - Thread Callbacks
    #####################################
    def callbackDetecionChange(self, portName):
        self.textArea.appendPlainText("Connected To Port: " + portName)     
        self.autoDetecThread.pause()   
        self.setConnectionStatus()
        self.deviceCommunicationThread.start()
        self.deviceCommunicationThread.sendCommand(CommandType.GET, self.commandArray)
        return
    
    def callbackDeviceRead(self, readText):
        self.textArea.appendPlainText(readText)
        return

    def callbackDeviceFill(self, responce):
        request = responce.split(",")
        if request[0] == self.wsprDevice.config.deviceconstants.commands.responce.callsign:
            self.wsprDevice.callsign = request[1]
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.startupmode:
            self.wsprDevice.startupMode = request[1]
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.currentmode:
            self.wsprDevice.currentMode = request[1]
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.generatorfrequency:
            self.wsprDevice.generatorfrequency = request[1]
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.power:
            self.wsprDevice.power = request[1]
        
        self.FillData()

    def callbackDeviceRealTime(self, responce):
        request = responce.split(",")
        if request[0] == self.wsprDevice.config.deviceconstants.commands.responce.gpssatdata:
            self.CurrentGPSStatus.setValue(float(request[1]))
            self.gpsLocked.setToolTip("GPS Quality: " + request[1] + "%")
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.gpsposition:
            self.gpsPosition.setText(request[1])
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.gpstime:
            self.gpsTime.setText(request[1])
        elif request[0] == self.wsprDevice.config.deviceconstants.commands.responce.gpslocked:
            if request[1] == "T":
                self.gpsLocked.setStyleSheet(self.wsprDevice.config.gpsLockedTrueCSS)
            else:
                self.gpsLocked.setStyleSheet(self.wsprDevice.config.gpsLockedFalseCSS)

    def callbackThreadException(self, error):
        self.textArea.appendPlainText("EXCEPTION IN THREAD!")
        self.textArea.appendPlainText(error)
        self.deviceCommunicationThread.pause()
        self.wsprDevice.port = None
        self.setConnectionStatus()
        self.autoDetecThread.resume()
    #####################################
    #END - Thread Callbacks
    #####################################

    #####################################
    #START - Thread handlers
    #####################################
    def createThreads(self):
        #detect the wspr device
        self.autoDetecThread = AutoDetectionThread(self.wsprDevice)
        self.autoDetecThread.port.connect(self.callbackDetecionChange)
        self.autoDetecThread.read.connect(self.callbackDeviceRead)
        self.autoDetecThread.start()

        #Communicate with wspr device
        self.deviceCommunicationThread = DeviceCommunicationThread(self.wsprDevice)
        self.deviceCommunicationThread.display.connect(self.callbackDeviceRead)
        self.deviceCommunicationThread.update.connect(self.callbackDeviceFill)
        self.deviceCommunicationThread.realtime.connect(self.callbackDeviceRealTime)
        self.deviceCommunicationThread.exception.connect(self.callbackThreadException)
        
    def stopThreads(self):
        self.autoDetecThread.stop()
        self.deviceCommunicationThread.stop()
        self.autoDetecThread.wait()
        self.deviceCommunicationThread.wait()

    def pauseThreads(self):
        self.autoDetecThread.pause()
        self.deviceCommunicationThread.pause()

    #catches the close of the application
    #clears up threads before closing
    def closeEvent(self, event):
        self.stopThreads()
        return

    #####################################
    #END - Thread handlers
    #####################################