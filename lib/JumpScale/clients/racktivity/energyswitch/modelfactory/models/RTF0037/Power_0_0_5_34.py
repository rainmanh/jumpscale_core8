from JumpScale.clients.racktivity.energyswitch.common import convert
from JumpScale.clients.racktivity.energyswitch.common.GUIDTable import Value
from copy import copy
import struct
import time
from JumpScale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Model(BaseModule):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._pointerGuids = [
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 3),
            (5, 1),
            (9, 12),
            (10, 8),
            (11, 1),
            (24, 1),
            (31, 8),
            (50, 8),
            (51, 2),
            (52, 12),
            (53, 12),
            (55, 8),
            (5004, 3),
            (5005, 3),
            (5006, 1),
            (5007, 1),
            (5012, 8),
            (5013, 8),
            (5032, 12),
            (5033, 12),
            (5034, 12),
            (5035, 12),
            (16, 8),
            (54, 8),
        ]

        self._guidTable.update({
            1: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),  # GeneralModuleStatus
            2: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),  # SpecificModuleStatus
            3: Value(u"type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='UNIX'\nscale=0"),  # CurrentTime
            4: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),  # Voltage
            5: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='Hz'\nscale=3"),  # Frequency
            9: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),  # ActiveEnergy
            10: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kVAh'\nscale=3"),  # ApparentEnergy
            11: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),  # Temperature
            16: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),  # PowerFactor
            24: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='s'\nscale=0"),  # TimeOnline
            31: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),  # LogMeInfo
            50: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%'\nscale=1"),  # THD
            51: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%'\nscale=0"),  # Phase
            52: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='A'\nscale=4"),  # BigCurrent
            53: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='W'\nscale=3"),  # BigPower
            54: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='VA'\nscale=3"),  # BigApparentPower
            55: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),  # DetectedPhase
            5004: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),  # MaxVoltage
            5005: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),  # MinVoltage
            5006: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),  # MinTemp
            5007: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),  # MaxTemp
            5012: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),  # MinPowerFact
            5013: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),  # MaxPowerFact
            5032: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='A'\nscale=4"),  # MinBigCurr
            5033: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='A'\nscale=4"),  # MaxBigCurr
            5034: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='W'\nscale=3"),  # MinBigPower
            5035: Value(u"type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='W'\nscale=3"),  # MaxBigPower
            10002: Value(u"type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),  # FirmwareVersion
            10003: Value(u"type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),  # HardwareVersion
            10004: Value(u"type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),  # FirmwareID
            10005: Value(u"type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),  # HardwareID
            10047: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),  # MaxVoltageWarning
            10049: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),  # MinVoltageWarning
            10078: Value(u"type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),  # CurrentWarningEvent
            10080: Value(u"type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),  # PowerWarningEvent
            10109: Value(u"type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),  # ExternalSensorLabel
            10193: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='A'\nscale=4"),  # MaxBigCurrentWarn
            10194: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='A'\nscale=3"),  # MaxBigPowerWarning
            10195: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),  # GroupNumber
            10196: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),  # PhaseLink
            10197: Value(u"type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),  # CurrentSensorSel
            40008: Value(u"type='TYPE_STRING'\nsize=26\nlength=26\nunit=''\nscale=0"),  # ModInfo
        })

    #Frequency
    def getFrequency(self, moduleID='P1'):
        moduleID = 'P1'
        guid = 5
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'THD' GUID 50 Data type TYPE_UNSIGNED_NUMBER
    #Total Harmonic Distortion
    def getTHD(self, portnumber=1):
        moduleID = 'P1'
        guid = 50
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # DetectedPhase
    def getDetectedPhase(self, portnumber, length=1):
        moduleID = 'P1'
        guid = 55
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION
    #Firmware version
    def getFirmwareVersion(self):
        moduleID = 'P1'
        guid = 10002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION_FULL
    #Firmware version
    #Return the firmware version as a string (example: '1.2.0.6')
    def getFirmwareVersionStr(self):
        moduleID = 'P1'
        guid = 10002
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = 'TYPE_VERSION_FULL'
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION
    #Hardware version
    def getHardwareVersion(self):
        moduleID = 'P1'
        guid = 10003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION_FULL
    #Hardware version
    #Return the hardware version as a string (example: '1.2.0.6')
    def getHardwareVersionStr(self):
        moduleID = 'P1'
        guid = 10003
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = 'TYPE_VERSION_FULL'
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'FirmwareID' GUID  10004 Data type TYPE_STRING
    #Identification of the firmware
    def getFirmwareID(self):
        moduleID = 'P1'
        guid = 10004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'HardwareID' GUID  10005 Data type TYPE_STRING
    #Identification of the hardware
    def getHardwareID(self):
        moduleID = 'P1'
        guid = 10005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    #Attribute 'MaxVoltageWarning' GUID  10047 Data type TYPE_UNSIGNED_NUMBER
    #Maximum voltage warning level
    def getMaxVoltageWarning(self, phasenumber):
        moduleID = 'P1'
        guid = 10047
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, phasenumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxVoltageWarning(self, value, phasenumber):
        moduleID = 'P1'
        guid = 10047
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), phasenumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    #Attribute 'MinVoltageWarning' GUID  10049 Data type TYPE_UNSIGNED_NUMBER
    #Minimum voltage warning level
    def getMinVoltageWarning(self, phasenumber):
        moduleID = 'P1'
        guid = 10049
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, phasenumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinVoltageWarning(self, value, phasenumber):
        moduleID = 'P1'
        guid = 10049
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), phasenumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # CurrentWarningEvent
    def getCurrentWarningEvent(self, portnumber=1):
        moduleID = 'P1'
        guid = 10078
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCurrentWarningEvent(self, value, portnumber=1):
        moduleID = 'P1'
        guid = 10078
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # PowerWarningEvent
    def getPowerWarningEvent(self, portnumber=1):
        moduleID = 'P1'
        guid = 10080
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPowerWarningEvent(self, value, portnumber=1):
        moduleID = 'P1'
        guid = 10080
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getExternalSensorLabel(self, moduleID, portnumber=1):
        guid = 10109
        valDef = self._guidTable[guid]
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setExternalSensorLabel(self, moduleID, value, portnumber=1):
        guid = 10109
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # MaxBigCurrentWarning
    def getMaxBigCurrentWarning(self, portnumber=1, length=1):
        moduleID = 'P1'
        guid = 10193
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxBigCurrentWarning(self, value, portnumber=1):
        moduleID = 'P1'
        guid = 10193
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # MaxBigPowerWarning
    def getMaxBigPowerWarning(self, portnumber=1, length=1):
        moduleID = 'P1'
        guid = 10194
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxBigPowerWarning(self, value, portnumber=1):
        moduleID = 'P1'
        guid = 10194
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # GroupNumber
    def getGroupNumber(self, portnumber, length=1):
        moduleID = 'P1'
        guid = 10195
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setGroupNumber(self, value, portnumber):
        guid = 10195
        moduleID = 'P1'
        valDef = self._guidTable[guid]
        value, count = convert.values2bin(value, valDef)
        data = self._parent.client.setAttribute(moduleID, guid, value, portnumber, count=count)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # PhaseLink
    def getPhaseLink(self, portnumber, length=1):
        moduleID = 'P1'
        guid = 10196
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPhaseLink(self, value, portnumber):
        guid = 10196
        moduleID = 'P1'
        valDef = self._guidTable[guid]
        value, count = convert.values2bin(value, valDef)
        data = self._parent.client.setAttribute(moduleID, guid, value, portnumber, count=count)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # CurrentSensorSelector
    def getCurrentSensorSelector(self, portnumber, length=1):
        moduleID = 'P1'
        guid = 10197
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCurrentSensorSelector(self, value, portnumber):
        guid = 10197
        moduleID = 'P1'
        valDef = self._guidTable[guid]
        value, count = convert.values2bin(value, valDef)
        data = self._parent.client.setAttribute(moduleID, guid, value, portnumber, count=count)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    #Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self):
        moduleID = 'P1'
        guid = 40008
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getPowerPointer(self):
        moduleID = 'P1'
        return self._getPointerData(moduleID)

    def getOscilloscopeTimeData(self, moduleID, portnumber=1):
        Ioffset = 258
        result = {'voltage': [[], [], []], 'current': []}

        # Get 516 bytes of raw data from device:
        rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType="T")
        if b'failed' in rawData:
            time.sleep(0.1)
            rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType="T")

        if len(rawData) < 516:
            # something is wrong, not enough data
            return (101, rawData)

        # Extracting values from raw binary data:
        voltageCalibration = float((struct.unpack('<H', rawData[:2]))[0]) / 12800.0
        voltageValues = struct.unpack('<256b', rawData[2:Ioffset])

        #the current values is returned in miliampers
        currentCalibration = float((struct.unpack('<H', rawData[Ioffset:Ioffset + 2]))[0]) / 128.0
        currentValues = struct.unpack('<256b', rawData[Ioffset + 2:2 * Ioffset])

        # Calculate the values based on calibration:
        # there're 3 voltage values (3 phases), and 4th should be discarded
        for i in range(256):
            idx = i % 4
            if idx != 0:
                result['voltage'][idx - 1].append(voltageValues[i] * voltageCalibration)
            result['current'].append(currentValues[i] * currentCalibration)

        return (0, result)

    def getOscilloscopeFrequencyData(self, moduleID, portnumber=1, dataType="current"):
        result = {
            'current': {'amplitudes': [], 'phases': []},
            'voltage': {'amplitudes': [], 'phases': []}
        }
        dataType = "FC" if dataType == "current" else "FV"
        numSamples = 64

        rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType=dataType)
        if b'failed' in rawData:
            time.sleep(0.1)
            rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType=dataType)

        if len(rawData) < 516:
            # something is wrong, not enough data
            return (101, rawData)

        if dataType == "FC":
            # Calculate the values based on calibration:
            currentCalibration = float((struct.unpack('<H', rawData[:2]))[0]) / 4096.0 / 1000
            for i in range(6, 2 + 4 * numSamples, 4):  # do not take DC (0th harmonic)
                currentAmplitude = struct.unpack('<H', rawData[i:i + 2])[0]
                result['current']['amplitudes'].append(currentAmplitude * currentCalibration)
                #if first harmonic is below 0.01 A it makes no sense to read as on 0 load, information is useless
                if len(result['current']['amplitudes']) == 1 and result['current']['amplitudes'][0] < 0.01:
                    return (100, None)
                result['current']['phases'].append(struct.unpack('<h', rawData[i + 2:i + 4])[0])
        else:
            length = 256
            VOffset = 2 + length
            voltageCalibration = float((struct.unpack('<H', rawData[VOffset:VOffset + 2]))[0]) * 10 / 4096.0 / 1000
            # Calculate the values based on calibration:
            for i in range(VOffset + 6, VOffset + 4 * numSamples, 4):  # do not take DC (0th harmonic)
                result['voltage']['amplitudes'].append(struct.unpack('<H', rawData[i:i + 2])[0] * voltageCalibration)
                result['voltage']['phases'].append(struct.unpack('<h', rawData[i + 2:i + 4])[0])
        return (0, result)
