#!/usr/bin/python3
import enum
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
