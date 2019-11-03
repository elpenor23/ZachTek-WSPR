#!/usr/bin/env python

#TODO - Make Real logger
#TODO - Send logfile to company and remove it every x amount of time/size
#TODO - Get error file / dir from config file

from datetime import datetime
from enum import Enum

errorLogDir = 'log/'
errorLogFile = 'error.log'

import traceback
import os

def openOrCreateLogFile(logDir, logFile):
    if not os.path.isdir(logDir):
        try:
            os.mkdir("log")
        except OSError as ex:
            print ("Creation of the directory %s failed" % logDir)
            print(log_traceback(ex))

    if not os.path.exists(logDir + logFile):
        file = open(logDir + logFile, "w+")
    else:
        file = open(logDir + logFile, "a")

    return file
        

def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
        traceback.format_exception(ex.__class__, ex, ex_traceback)]
    return tb_lines

def logError(errLevel, string_error, ex=None, ex_traceback=None):
    currentDateTime = datetime.now()
    f = openOrCreateLogFile(errorLogDir, errorLogFile)
    f.write(errLevel.name + ': ' + str(currentDateTime) + ' - ' + string_error + '\n')
    if errLevel == ErrorLevel.CRITICAL or errLevel == ErrorLevel.HIGH:
        f.write('\n'.join(log_traceback(ex, ex_traceback=ex_traceback)) + '\n')
    f.close

class ErrorLevel(Enum):
    DEBUG = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4