import json
import sys
from obj.ErrorObjects import logError, ErrorLevel
import os
#DEFINE CLASSES

class ConfigObject:

    def print(self):
        print("Name: " + self.name)
        print("Version: " + self.version)
        print('Bands: ')
        print(self.bands)
        print("Icons:")
        print(self.icons)
        print("Band Enabled Char: " + self.deviceconstants.bandEnabledChar)
        print("Band Disabled Char: " + self.deviceconstants.bandDisabledChar)
        print("Command End Chars: " + repr(self.deviceconstants.commands.commandEndChars))
        self.deviceconstants.commands.print()
        return

    def __init__(self, configFileName):
        #open the passed in config file
        try:
            configFile = open(configFileName, 'r')
        except IOError as ex:
            errorText = "Could not read config file: " + configFileName
            print(errorText)
            logError(ErrorLevel.CRITICAL, errorText, ex)
            sys.exit()

        #get the data
        configData = json.loads(configFile.read())
        configFile.close

        #load the data into the object
        self.name = configData["about"]["name"]
        self.version = configData["about"]["version"]
        self.debug = configData["debug"]
        self.notconnectedtext = configData["notConnectedText"]
        self.connectedtext = configData["connectedText"]
        self.bands = configData["bands"]
        self.readDeviceTimeout = configData["readdevicetimeout"]

        #icon data
        fullIconPath = os.getcwd() + configData["icons"]["dir"]
        self.icons = {
            "disconnected": fullIconPath + configData["icons"]["disconnected"],
            "connected": fullIconPath + configData["icons"]["connected"],
            "toolTip": configData["icons"]["toolTip"]
            }

        #Security
        self.checkSecurity = configData["checkSecurity"]
        self.securityErrorMessage = configData["securityErrorMessage"]
        
        #gps config
        self.gpsLockedFalseCSS = configData["gpsLockedFalseCSS"]
        self.gpsLockedTrueCSS = configData["gpsLockedTrueCSS"]
        self.gpsLockedUnknownCSS = configData["gpsLockedUnknownCSS"]

        #debug area config
        self.debugAreaMaximumBlockCount = configData["debugAreaMaximumBlockCount"]
        #Device Specific configuration
        self.deviceconstants = DeviceConstants()

        #band enabled/disabled chars
        self.deviceconstants.bandEnabledChar = configData["deviceconstants"]["bandEnabledChar"]
        self.deviceconstants.bandDisabledChar = configData["deviceconstants"]["bandDisabledChar"]

        #mode values
        self.deviceconstants.modeIdleChar = configData["deviceconstants"]["modeIdleChar"]
        self.deviceconstants.modeSignalChar = configData["deviceconstants"]["modeSignalChar"]
        self.deviceconstants.modeWSPRChar = configData["deviceconstants"]["modeWSPRChar"]
        
        #Device Commands and responces
        self.deviceconstants.commands = CommandObject()
    
        #chars for get/set commands
        self.deviceconstants.commands.get.char = configData["deviceconstants"]["commands"]["get"]["char"]
        self.deviceconstants.commands.set.char = configData["deviceconstants"]["commands"]["set"]["char"]
        self.deviceconstants.commands.commandEndChars = configData["deviceconstants"]["commandEndChars"]
        
        #callsign
        self.deviceconstants.commands.get.callsign = configData["deviceconstants"]["commands"]["get"]["callsign"]
        self.deviceconstants.commands.set.callsign = configData["deviceconstants"]["commands"]["set"]["callsign"]
        self.deviceconstants.commands.responce.callsign = configData["deviceconstants"]["commands"]["responce"]["callsign"]

        #bands
        self.deviceconstants.commands.get.bands = configData["deviceconstants"]["commands"]["get"]["bands"]
        self.deviceconstants.commands.set.bands = configData["deviceconstants"]["commands"]["set"]["bands"]
        self.deviceconstants.commands.responce.bands = configData["deviceconstants"]["commands"]["responce"]["bands"]

        #startupmode
        self.deviceconstants.commands.get.startupmode = configData["deviceconstants"]["commands"]["get"]["startupmode"]
        self.deviceconstants.commands.set.startupmode = configData["deviceconstants"]["commands"]["set"]["startupmode"]
        self.deviceconstants.commands.responce.startupmode = configData["deviceconstants"]["commands"]["responce"]["startupmode"]

        #currentmode
        self.deviceconstants.commands.get.currentmode = configData["deviceconstants"]["commands"]["get"]["currentmode"]
        self.deviceconstants.commands.set.currentmode = configData["deviceconstants"]["commands"]["set"]["currentmode"]
        self.deviceconstants.commands.responce.currentmode = configData["deviceconstants"]["commands"]["responce"]["currentmode"]

        #power
        self.deviceconstants.commands.get.power = configData["deviceconstants"]["commands"]["get"]["power"]
        self.deviceconstants.commands.set.power = configData["deviceconstants"]["commands"]["set"]["power"]
        self.deviceconstants.commands.responce.power = configData["deviceconstants"]["commands"]["responce"]["power"]

        #generatorfequency
        self.deviceconstants.commands.get.generatorfrequency = configData["deviceconstants"]["commands"]["get"]["generatorfrequency"]
        self.deviceconstants.commands.set.generatorfrequency = configData["deviceconstants"]["commands"]["set"]["generatorfrequency"]
        self.deviceconstants.commands.responce.generatorfrequency = configData["deviceconstants"]["commands"]["responce"]["generatorfrequency"]

        #Lists
        self.deviceconstants.commands.responcestoload = configData["deviceconstants"]["commands"]["responce"]["responcestoload"]
        self.deviceconstants.commands.realtimeresponces = configData["deviceconstants"]["commands"]["responce"]["realtimeresponces"]
        self.deviceconstants.commands.alwaysdisplayresponces = configData["deviceconstants"]["commands"]["responce"]["alwaysdisplayresponces"]

        #Set Only
        self.deviceconstants.commands.set.save = configData["deviceconstants"]["commands"]["set"]["save"]
        
        #Responce Only
        self.deviceconstants.commands.responce.gpsposition = configData["deviceconstants"]["commands"]["responce"]["gpsposition"]
        self.deviceconstants.commands.responce.gpstime = configData["deviceconstants"]["commands"]["responce"]["gpstime"]
        self.deviceconstants.commands.responce.gpslocked = configData["deviceconstants"]["commands"]["responce"]["gpslocked"]
        self.deviceconstants.commands.responce.gpssatdata = configData["deviceconstants"]["commands"]["responce"]["gpssatdata"]
        self.deviceconstants.commands.responce.deviceinfo = configData["deviceconstants"]["commands"]["responce"]["deviceinfo"]
        return

class DeviceConstants:
    def __init__(self):
        self.commands = CommandObject()
        self.bandEnabledChar = ""
        self.bandDisabledChar = ""
        self.modeIdleChar = ""
        self.modeSignalChar = ""
        self.modeWSPRChar = ""


class CommandObject:
    def __init__(self):
        self.get = RawCommandObject()
        self.set = RawCommandObject()
        self.responce = RawCommandObject()
        self.responcestoload = []
        self.realtimeresponces = []
        self.alwaysdisplayresponces = []
        
    def print(self, title = "Commands"):
        print(title + ":")
        self.get.print("Gets")
        self.set.print("Sets")
        self.responce.print("Responces")


class RawCommandObject:
    def __init__(self):
        self.char = ""
        self.save = ""
        self.callsign = ""
        self.bands = ""
        self.startupmode = ""
        self.currentmode = ""
        self.gpsposition = ""
        self.gpstime = ""
        self.gpssatdata = ""
        self.deviceinfo = ""
        self.gpslocked = ""
        self.power = ""
        self.generatorfrequency = ""

    def print(self, title = "RawCommandObject"):
        print(title + ":")
        print("char: " + self.char)
        print("callsign: " + self.callsign)
        print("bands: " + self.bands)
        print("startup: " + self.startupmode)
#END DEFINE CLASSES