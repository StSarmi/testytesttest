#################################################################################################
# Web server for Elvias project FBI, based on previous versions and latest sikkilsdalen.py 
# Routine:		"elsinFbi.py"  
# Rev date: 	March 6th, 2023
# By: 			Per Dypvik
# Description: 	The routine is used by energiScada running on an Rpi IOTG from Compulab. It is connected 
#				via Studer Xcom-232i to several XTx, that in turn is connected to Pylontech LFP batteries
#				over CAN-bus. 'elsinFbi.py' uses the Studer "SCOM-protocol" and makes JSON data available on
#				on port 8091
#################################################################################################
#				energiScada is a software suite to monitor, control and visualize different equipment 
#				in a LES (local energy system) like battery inverter/chargers, solar inverters and different 
#				monitoring and control equipment.
#################################################################################################
# Dependencies: 
# proprietary library made by elsin:	scomFrame, studerCtrl
# general libraries:					socket, select, struct, serial, time, re, sys, os, 
#										binascii, flask
#################################################################################################
#	Monitored parameters that are visualized
#	readbatteryValues() deliver the following with /battery:
#		{"unit":"BMZ","batteryVoltage":55.8125,"batteryCurrent":-1.6796875,"batteryTemp":29.703125,"batterySoC":61.0,"batterySoH":92.0}
#	xtenders() deliver the following with /xtenders:
#		{"unit":"Xtender", "AcOutFreq":50.0, "sxtStatus":1,"acOutV1":224.0,"acOutV2":220.0,"acOutV3":0}
#	contactors() deliver the following with /contactors:
# 		{"unit":"Xtender", "XT1transfer":1, "XT2transfer":1}
#	readcurrentIn() deliver the following with /currentIn:
#		{"unit":"Xtender", "currentInL1":0, "currentInL2":0,"currentInL3":0}
#	readCurrentOut() deliver the following with /currentOut:
#		{"unit":"Xtender","currentOutL1":3.953125,"currentOutL2":4.28125,"currentOutL3":0}
#	readpowerLimit() deliver the following with /powerLimit:
#		{"unit":"Xtender", "powerLimit":9.046875, "powerLimitV1":9.046875, "powerLimitV2":7.078125}
###########################################################################################################

import sys,json
sys.path.append("/home/openhabian/.local/lib/python2.7/site-packages")
import socket, select, struct, serial, time, re, sys, os, binascii, flask
#from studerCtrl import levelOnly, int32Type, floatType, boolType, enumType, writeList
#import studerCtrl       # henter levelOnly, Int32Type, floatType, boolType, enumType, writeList, specialBool, acceptScada, floatLength og mode
from studerCtrlv2 import parameterId as userInfo, readparameterId as readUserInfo
from studerCtrlv2 import makeProperty, parameterId, readparameterId, checkMode
from scomFrame3 import checksum, bytearray_to_string, string_to_bytearray
#from modbusClient import holdingReg, coil
#from readStatus import readTransfer 

# global variables for use when illegal values are read. LastBatterypower should not be used too many times before an alerm is issued!! 
lastBatteryvoltage	= 'NA'
lastBatterycurrent 	= 'NA'
lastBatterypower 	= 'NA'
lastBatterySoC		= 'NA'
lastBatterytemp		= 'NA'
lastBatterySoH 		= 'NA'
lastV1Out			= 'NA'
lastV2Out			= 'NA'
lastV3Out			= 'NA'
lastOutFreq			= 'NA'
lastPowerin			= 'NA'
lastPowerin1		= 'NA'
lastPowerin2		= 'NA'
lastPowerin3		= 'NA'
lastPowerout		= 'NA'
lastCurrentInL1		= 'NA'
lastCurrentInL2		= 'NA'
lastCurrentInL3		= 'NA'
lastCurrentOutL1	= 'NA'
lastCurrentOutL2	= 'NA'
lastCurrentOutL3	= 'NA'


floatLength = 89	#	a float response is read as 89 hex characters (30 bytes take 2 hex digits + comma, last value lack comma )

from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
	return 'Use values:\tsxtStatus, sxtOFF, sxtON, battery, xtenders, time, powerLimit or setImax <value>'

#####################################################################################################################
# Set up web server
#####################################################################################################################

@app.route('/battery')
def readbatteryValues():
	global lastBatteryvoltage
	global lastBatterycurrent
	global lastBatterypower
	global lastBatterySoC
	global lastBatterytemp
	global lastBatterySoH
	batterySoH = lastBatterySoH
	batteryTemp = lastBatterytemp
	batterySoC = lastBatterySoC
	batteryCurrent = lastBatterycurrent
	batteryVoltage = lastBatteryvoltage
	batteryPower = lastBatterypower
	

	try:	#read batteryTemp
		frameInfo = userInfo(0,7029)            # make a frame format, 7029 is battery temperature via CAN
		data = readUserInfo(frameInfo)          # uses frame format to actually read the parameter
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			batteryTemp = struct.unpack('f', str(value_bytearray))[0]
			if ((batteryTemp > 70) or (batteryTemp < -20)): # settings prevent other values
				batteryTemp = 'Unavailable'	# oppress impossible values	except:
			lastBatterytemp = batteryTemp
	except:
		batteryTemp = lastBatterytemp

	try:	# read batteryVoltage
		frameInfo = userInfo(0,7030)            # make a frame format, 7032 is minute avg battery voltage via CAN
		data = readUserInfo(frameInfo)          # uses frame format to actually read the parameter
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			batteryVoltage = struct.unpack('f', str(value_bytearray))[0]
			if ((batteryVoltage > 70) or (batteryVoltage < 40)): # settings prevent higher values
				batteryVoltage = 'Unavailable'	# oppress impossible values
			lastBatteryvoltage = batteryVoltage
	except:
		batteryVoltage = lastBatteryvoltage

	try:	# read batteryCurrent
		frameInfo = userInfo(0,7031)            # make a frame format, 7031 is minute avg battery current via CAN
		data = readUserInfo(frameInfo)          # uses frame format to actually read the parameter
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			batteryCurrent = struct.unpack('f', str(value_bytearray))[0]
			if ((batteryCurrent > 2000) or (batteryCurrent < -2000)): # settings and fuses prevent higher values
				batteryCurrent = 'Unavailable'	# oppress impossible values
			lastBatterycurrent=batteryCurrent
	except:
		batteryCurrent = lastBatterycurrent
	
	try:	# read batterySoC
		frameInfo = userInfo(0,7032)            # make a frame format, 7030 is minute avg battery SoC via CAN
		data = readUserInfo(frameInfo)          # uses frame format to actually read the parameter
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			batterySoC = struct.unpack('f', str(value_bytearray))[0]
			if ((batterySoC > 100) or (batterySoC < 0)): # settings prevent other values
				batterySoc = 'Unavailable'	# oppress impossible values	
			lastBatterySoC = batterySoC
	except:
		batterySoc = lastBatterySoC

	try:	# read batterySoH
		frameInfo = userInfo(0,7057)            # make a frame format, 7057 is battery SoH via CAN
		data = readUserInfo(frameInfo)          # uses frame format to actually read the parameter
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			batterySoH = struct.unpack('f', str(value_bytearray))[0]
			if ((batterySoH > 100) or (batterySoH < 20)): # settings prevent other values
				batterySoH = 'Unavailable'	# oppress impossible values	except:
			lastBatterySoH = batterySoH
	except:
		batterySoH = lastBatterySoH

	return '{"unit":"BMZ","batteryVoltage":'+str(batteryVoltage)+',"batteryCurrent":'+str(batteryCurrent)+',"batteryTemp":'+str(batteryTemp)+',"batterySoC":'+str(batterySoC)+',"batterySoH":'+str(batterySoH)+'}'

@app.route('/xtenders')
def xtenders():
	global lastV1Out
	global lastV2Out
	global lastV3Out
	global lastOutFreq
	AcOutV1 = lastV1Out
	AcOutV2 = lastV2Out
	AcOutV3 = lastV3Out
	AcOutFreq = lastOutFreq

#		<3049> XTstatus			- one value read every 1 min to see if system is down 
#		<3110> Frequency		- one value read every 1 min for avg AC in frequency
#		<3111> MinV1/2/3		- one value read every 1 min for min 'AC voltage in' phase 1/2/3' (XTM 1,2,3) 
#		<3112> MaxV1/2/3		- one value read every 1 min for max 'AC voltage in' phase 1/2/3' (XTM 1,2,3) 
#		<3113> AvgV1/2/3		- one value read every 1 min for avg 'AC voltage in' phase 1/2/3' (XTM 1,2,3) 

	try:	# check if Xtenders are ON or OFF
		frameInfo = userInfo(0,3049)            # make a frame format, 3049 is parameter to read Xtender status
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		value_bytearray = string_to_bytearray(data)[23:25]  # enum response
		xtStatus = struct.unpack('>H', str(value_bytearray))[0]
	except:
		xtStatus = 'Unavailable'

	try:	# read acOutFreq, in and out frequency always equal when transfer is closed
		frameInfo = userInfo(1,3110)            # make a frame format, 3110 is parameter for avg ac input frequency from Xtender
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			AcOutFreq = struct.unpack('<f', str(value_bytearray))[0]
			if ((AcOutFreq > 60) or (AcOutFreq < 40)): #Do not believe values outside +/- 10 Hz
				AcOutFreq = 'Unavailable'		
			lastOutFreq = AcOutFreq
	except:
		AcOutFreq = lastOutFreq					

	try:	# read acOutV1, in and out voltage always equal with transfer closed
		frameInfo = userInfo(1,3113)            # make a frame format, 3113 is avg ac input voltage to Xtender
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			AcOutV1 = struct.unpack('<f', str(value_bytearray))[0]
			if ((AcOutV1 > 260) or (AcOutV1 < 0)): #Do not believe values below 100V
				AcOutV1 = 'Unavailable'	# Studer uses 1 - 3 V as 'no output voltage'
			lastV1Out = AcOutV1
	except:
		AcOutV1 = lastV1Out

	try:	# read acOutV2, in and out voltage always equal with transfer closed
		frameInfo = userInfo(2,3113)            # make a frame format, 3113 is avg ac input voltage to Xtender
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			AcOutV2 = struct.unpack('<f', str(value_bytearray))[0]
			if ((AcOutV2 > 260) or (AcOutV2 < 0)): #Do not believe values below 100V 
				AcOutV2 = 'Unavailable'	# Studer uses 1 - 3 V as 'no output voltage'
			lastV2Out = AcOutV2
	except:
		AcOutV2 = lastV2Out

	try:	# read acOutV3, in and out voltage always equal with transfer closed
		frameInfo = userInfo(3,3113)            # make a frame format, 3113 is avg ac input voltage to Xtender
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			AcOutV3 = struct.unpack('<f', str(value_bytearray))[0]
			if ((AcOutV3 > 260) or (AcOutV3 < 0)): # Do not believe values below 100V 
				AcOutV3 = 'Unavailable'	# Studer uses 1 - 3 V as 'no output voltage'
		else:
			AcOutV3 = 0
	except:
		AcOutV3 = lastV3Out


	return '{"unit":"Xtender", "AcOutFreq":'+str(AcOutFreq)+', "sxtStatus":'+str(xtStatus)+',"acOutV1":'+str(AcOutV1)+ ',"acOutV2":'+str(AcOutV2)+',"acOutV3":'+str(AcOutV3)+'}'


@app.route('/contactors')
def contactors():
        try:
            contactorValue = {"XT1transfer": readTransfer(1),"XT2transfer": readTransfer(2)}
        except:
            contactorValue = []
        return '{"unit":"Xtender", "XT1transfer":'+str(readTransfer(1))+', "XT2transfer":'+str(readTransfer(2))+'}'
        #return  (json.dumps(contactorValue))


@app.route('/sxtStatus')
def sxtStatus():
	# parameter is ENUM

	try:
		frameInfo = userInfo(0,3049)            # make a frame format, 3049 is parameter to read Xtender status
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		value_bytearray = string_to_bytearray(data)[23:25]  # enum response
		xtStatus = struct.unpack('>H', str(value_bytearray))[0]
	except:
		xtStatus = 'Unavailable'
	return '{"unit":"Xtender", "sxtStatus":'+str(xtStatus)+'}'


@app.route('/time')
def sxtTime():
	try:
		realTime=time.strftime("%Y:%m:%d %H:%M:%S")
	except:
		realTime = 'Unavailable'
	return '{"unit":"NTP:", "Time":'+str(realTime)+'}'


@app.route('/sxtON')
def sxtON():
	data = parameterId(int(0), int(1415), 'write', 'int', int(1))		
	response = readparameterId(data)
	try:
		frameInfo = userInfo(0,3049)            # make a frame format, 3049 is parameter to read Xtender status
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		value_bytearray = string_to_bytearray(data)[23:25]  # enum response
		xtStatus = struct.unpack('>H', str(value_bytearray))[0]
	except:
		xtStatus = 'Unavailable'
	return '{"unit":"Xtender", "sxtStatus":'+str(xtStatus)+'}'

@app.route('/sxtOFF')
def sxtOFF():
	data = parameterId(int(0), int(1399), 'write', 'int', int(1))		
	response = readparameterId(data)
	try:
		frameInfo = userInfo(0,3049)            # make a frame format, 3049 is parameter to read Xtender status
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		value_bytearray = string_to_bytearray(data)[23:25]  # enum response
		xtStatus = struct.unpack('>H', str(value_bytearray))[0]
	except:
		xtStatus = 'Unavailable'
	return '{"unit":"Xtender", "sxtStatus":'+str(xtStatus)+'}'


@app.route('/currentOut')
### skal hente verdi fra 3 invertere, en per fase med userInfo 1 - 3
def readcurrentOut():
	global lastCurrentOutL1, lastCurrentOutL2, lastCurrentOutL3
	currentOutL1 = lastCurrentOutL1
	currentOutL2 = lastCurrentOutL2
	currentOutL3 = lastCurrentOutL3
	error = 0
	
	try:
		frameInfo = userInfo(1,3022)            # make a frame format, 3022 is load current 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			currentOutL1 = struct.unpack('f', str(value_bytearray))[0]
			lastCurrentOutL1 = currentOutL1
		else:
			currentOutL1 = 0
	except:
		error=1

	try:
		frameInfo = userInfo(2,3022)            # make a frame format, 3115 is max current from grid last minute 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			currentOutL2 = struct.unpack('f', str(value_bytearray))[0]
			lastCurrentOutL2 = currentOutL2
		else:
			currentOutL2 = 0
	except:
		error=error+2

	try:
		frameInfo = userInfo(3,3022)            # make a frame format, 3115 is max current from grid last minute 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			currentOutL3 = struct.unpack('f', str(value_bytearray))[0]
			lastCurrentOutL3 = currentOutL3
		else:
			currentOutL3 = 0
	except:
		error=error+3
	
	return '{"unit":"Xtender","currentOutL1":'+str(currentOutL1)+',"currentOutL2":'+str(currentOutL2)+',"currentOutL3":'+str(currentOutL3)+'}'

@app.route('/currentIn')
### skal hente verdi fra 3 invertere, en per fase med userInfo 1 - 3
def readcurrentIn():
	global lastCurrentInL1, lastCurrentInL2, lastCurrentInL3
	currentInL1 = lastCurrentInL1
	currentInL2 = lastCurrentInL2
	currentInL3 = lastCurrentInL3
	error = 0
	
	try:
		frameInfo = userInfo(1,3012)            # make a frame format, 3115 is max current from grid last minute 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			currentInL1 = struct.unpack('f', str(value_bytearray))[0]
			lastCurrentInL1 = currentInL1
		else:
			currentInL1 = 0
	except:
		error=1

	try:
		frameInfo = userInfo(2,3012)            # make a frame format, 3115 is max current from grid last minute 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			currentInL2 = struct.unpack('f', str(value_bytearray))[0]
			lastCurrentInL2 = currentInL2
		else:
			currentInL2 = 0
	except:
		error=error+2

	try:
		frameInfo = userInfo(3,3012)            # make a frame format, 3115 is max current from grid last minute 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			currentInL3 = struct.unpack('f', str(value_bytearray))[0]
			lastCurrentInL3 = currentInL3
		else:
			currentInL3 = 0
	except:
		error=error+3
	
	return '{"unit":"Xtender", "currentInL1":'+str(currentInL1)+', "currentInL2":'+str(currentInL2)+',"currentInL3":'+str(currentInL3)+'}'


@app.route('/powerIn')
### skal summere 3 invertere, en verdi per fase med userInfo 1 - 3
def readpowerIn():
	global lastPowerin, lastPowerIn1, lastPowerIn2, lastPowerIn3
	invPowerIn = lastPowerin
	invPowerIn1 = lastPowerin1
	invPowerIn2 = lastPowerin2
	invPowerIn3 = lastPowerin3
	error = 0
	
	try:
		frameInfo = userInfo(1,3119)            # make a frame format, 3119 is avg power from grid 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			invPowerIn1 = struct.unpack('f', str(value_bytearray))[0]
			#print invPowerOut
			#if ((invPowerOut > 20)|(invPowerOut < 0)): # settings prevent higher values
			#	invPowerOut = 'Unavailable'	# oppress impossible values
			lastPowerin = invPowerIn1
	except:
		error=1
	
	try:
		frameInfo = userInfo(2,3119)            # make a frame format, 3119 is avg power from grid  
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			invPowerIn2 = struct.unpack('f', str(value_bytearray))[0]
			#if ((invPowerOut > 20)|(invPowerOut < 0)): # settings prevent higher values
			#invPowerOut = 'Unavailable'	# oppress impossible values
			lastPowerin = lastPowerin+invPowerIn2
	except:
		error=2+error
	
	try:
		frameInfo = userInfo(3,3119)            # make a frame format, 3119 is avg power from grid 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			invPowerIn3 = struct.unpack('f', str(value_bytearray))[0]
			#if ((invPowerOut > 20)|(invPowerOut < 0)): # settings prevent higher values
			#	invPowerOut = 'Unavailable'	# oppress impossible values
			lastPowerin = lastPowerin+invPowerIn3	# inverter 1 - 3 is only half the system
		else:
			invPowerIn3 = 0
	except:
		error = 3+error

	lastPowerin = lastPowerin * 1000
	invPowerIn = lastPowerin

	if (error):
		invPowerIn = lastPowerin

	
	return '{"unit":"Xtender", "powerIn":'+str(invPowerIn)+', "powerIn1":'+str(invPowerIn1 * 1000)+', "powerIn2":'+str(invPowerIn2 * 1000)+', "powerIn3":'+str(invPowerIn3 * 1000)+', "error":'+str(error)+'}'


@app.route('/powerOut')
### skal summere alle 3 invertere, en verdier per fase med userInfo 1 - 3. Benytter kun to i Mysen
def readpowerOut():
	global lastPowerout
	invPowerOut = lastPowerout
	error = 0
	try:
		frameInfo = userInfo(1,3101)            # make a frame format, 3101 is avg power to load.
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			invPowerOut1 = struct.unpack('f', str(value_bytearray))[0]
			#print invPowerOut
			#if ((invPowerOut > 20)|(invPowerOut < 0)): # settings prevent higher values
			#	invPowerOut = 'Unavailable'	# oppress impossible values
			lastPowerout = invPowerOut1
	except:
		error=1
	
	try:
		frameInfo = userInfo(2,3101)            # make a frame format, 3101 is avg power to load.
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			invPowerOut2 = struct.unpack('f', str(value_bytearray))[0]
			#if ((invPowerOut > 20)|(invPowerOut < 0)): # settings prevent higher values
			#invPowerOut = 'Unavailable'	# oppress impossible values
			lastPowerout = lastPowerout+invPowerOut2
	except:
		error=2+error
	

	try:
		frameInfo = userInfo(3,3101)            # make a frame format, 3101 is avg power to load. 
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			invPowerOut3 = struct.unpack('f', str(value_bytearray))[0]
			#if ((invPowerOut > 20)|(invPowerOut < 0)): # settings prevent higher values
			#	invPowerOut = 'Unavailable'	# oppress impossible values
			lastPowerout = lastPowerout+invPowerOut3	# inverter 1 - 3 is only half the system
		else:
			invPowerOut3 = 0
	except:
		error = 3+error

	lastPowerout = lastPowerout * 1000
	invPowerOut = lastPowerout

	if (error):
		invPowerOut = lastPowerout
	
	return '{"unit":"Xtender", "powerOut":'+str(invPowerOut)+',"powerOut1":'+str(invPowerOut1*1000)+',"powerOut2":'+str(invPowerOut2*1000)+',"powerOut3":'+str(invPowerOut3*1000)+', "error":'+str(error)+'}'

@app.route('/powerLimit')
def readpowerLimit():
	powerLimit = 'Unavailable'
	powerLimitV1 = 'Unavailable'
	powerLimitV2 = 'Unavailable'
	try:
		frameInfo = userInfo(0,3017)            # make a frame format, 3017 is read parameter for max current from grid
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		if (len(data) == floatLength):
			value_bytearray = string_to_bytearray(data)[24:28]  # float response
			powerLimit = struct.unpack('f', str(value_bytearray))[0]
			if ((powerLimit > 50)|(powerLimit < 0)): # settings prevent higher values
				powerLimit = 'Unavailable'	# oppress impossible values
	except:
		powerLimit = 'Unavailable'

	try:
                frameInfo = userInfo(1,3017)            # make a frame format, 3017 is read parameter for max current from grid
                data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
                if (len(data) == floatLength):
                        value_bytearray = string_to_bytearray(data)[24:28]  # float response
                        powerLimitV1 = struct.unpack('f', str(value_bytearray))[0]
                        if ((powerLimitV1 > 50)|(powerLimitV1 < 0)): # settings prevent higher values
                                powerLimit1 = 'Unavailable'      # oppress impossible values
	except:
                powerLimitV1 = 'Unavailable'

	try:
                frameInfo = userInfo(2,3017)            # make a frame format, 3017 is read parameter for max current from grid
                data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
                if (len(data) == floatLength):
                        value_bytearray = string_to_bytearray(data)[24:28]  # float response
                        powerLimitV2 = struct.unpack('f', str(value_bytearray))[0]
                        if ((powerLimitV2 > 50)|(powerLimitV2 < 0)): # settings prevent higher values
                                powerLimitV2 = 'Unavailable'      # oppress impossible values
	except:
                powerLimitV2 = 'Unavailable'

	return '{"unit":"Xtender", "powerLimit":'+str(powerLimit)+', "powerLimitV1":'+str(powerLimitV1)+', "powerLimitV2":'+str(powerLimitV2)+'}'

@app.route("/setImax <value>")
def setImax(value):
	print (value)
	parameterValue = float(value)
	data = parameterId(int(0), int(1107), 'write', 'float', parameterValue)
	response = readparameterId(data)
	try:
		frameInfo = userInfo(0,3017)            # make a frame format, 1107 is to set max current from grid, 3017 to read
		data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
		value_bytearray = string_to_bytearray(data)[24:28]  # float response
		Imax = struct.unpack('f', str(value_bytearray))[0]
	except:
		Imax = 'Unavailable'
	return '{"unit":"Xtenders", "Imax":'+str(Imax)+'}'

@app.route("/setImaxV1 <value>")
def setImaxV1(value):
        print (value)
        parameterValue = float(value)
        data = parameterId(int(1), int(1107), 'write', 'float', parameterValue)
        response = readparameterId(data)
        try:
                frameInfo = userInfo(0,3017)            # make a frame format, 1107 is to set max current from grid, 3017 to read
                data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
                value_bytearray = string_to_bytearray(data)[24:28]  # float response
                ImaxV1 = struct.unpack('f', str(value_bytearray))[0]
        except:
                ImaxV1 = 'Unavailable'
        return '{"unit":"Xtenders", "ImaxV1":'+str(ImaxV1)+'}'

@app.route("/setImaxV2 <value>")
def setImaxV2(value):
        print (value)
        parameterValue = float(value)
        data = parameterId(int(2), int(1107), 'write', 'float', parameterValue)
        response = readparameterId(data)
        try:
                frameInfo = userInfo(0,3017)            # make a frame format, 1107 is to set max current from grid, 3017 to read
                data = readUserInfo(frameInfo)          # uses frame format to actually read the studer charger
                value_bytearray = string_to_bytearray(data)[24:28]  # float response
                ImaxV2 = struct.unpack('f', str(value_bytearray))[0]
        except:
                ImaxV2 = 'Unavailable'
        return '{"unit":"Xtenders", "ImaxV2":'+str(ImaxV2)+'}'


if __name__ == '__main__':
	app.run(debug=True, port=8091, host='0.0.0.0')
		
		
