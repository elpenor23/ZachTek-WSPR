#!/usr/bin/python3
import enum
class CommandType(enum.Enum):
    GET = 1
    SET = 2
    RESPONCE = 3

class Command(enum.Enum):
    CALLSIGN = 1
    BANDS = 2
    STARTUP_MODE = 3
    CURRENT_MODE = 4
    POWER = 5
    GENERATOR_FREQUENCY = 6
    SAVE = 7
    FACTORY_PRODUCT_NUMBER = 8
    FACTORY_HARDWARE_VERSION = 9
    FACTORY_HARDWARE_REVISION = 10
    FACTORY_SOFTWARE_VERSION = 11
    FACTORY_SOFTWARE_REVISION = 12
    FACTORY_FREQUENCY_REFERENCE_OSCILLATOR_FREQUENCY = 13
    FACTORY_LOWPASS_FINTER_INSTALLED = 14
    LOCATION_STATE = 15
    LOCATION_VALUE = 16
     