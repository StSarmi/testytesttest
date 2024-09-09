#################################################################################################
# Innlesning av parametere fra utstyr i PQ-prosektet 
# Routine:			"updatePQ.py"  
# By: 				Stian Olsen
# Description: 			 
#				
#################################################################################################
#				energiScada is a software suite to monitor, control and visualize different equipment 
#				in a LES (local energy system) like battery inverter/chargers, solar inverters and different 
#				monitoring and control equipment.
#################################################################################################
# Dependencies: 
#
#################################################################################################
#	Monitored parameters are imported from elsinPQ.py with
###########################################################################################################

import sys,json
sys.path.append("/home/openhabian/.local/lib/python2.7/site-packages")
"""
import socket, select, struct, serial, time, re, sys, os, binascii, flask
#from studerCtrl import levelOnly, int32Type, floatType, boolType, enumType, writeList
import studerCtrl       # henter levelOnly, Int32Type, floatType, boolType, enumType, writeList, specialBool, acceptScada, floatLength og mode
from studerCtrl import parameterId as userInfo, readparameterId as readUserInfo
from studerCtrl import makeProperty, parameterId, readparameterId, checkMode
from scomFrame import checksum, bytearray_to_string, string_to_bytearray
from modbusClient import holdingReg, coil
from readStatus import readTransfer 
"""
from elsinPQ import readBatteryValues as readBattery, xtenders as readXtenders, contactors as readContactors, readCurrentIn, readCurrentOut, readPowerLimit

async def main():
        state_manager = State()
        while True:
            try:
                tidStart = time.time()
                try:
                    state_manager.set_variable(Variables.contactorStatus, readContactors())
                    state_manager.set_variable(Variables.battery1Values, readBattery())
                    state_manager.set_variable(Variables.xtenderValues, readXtenders())
                    state_manager.set_variable(Variables.currentInValues, readCurrentIn())
                    state_manager.set_variable(Variables.currentOutValues, readCurrentOut())
                    state_manager.set_variable(Variables.powerLimit, readPowerLimit())
                                               
                except:
                    print (" - feil ved skriving til db -xtenderValues")
                    pass
                #mellomTid = time.time()
                print(f'\r\n\t-Avlesning av utstyr tok {time.time()-tidStart:.2f} sekunder\r\n')

                await asyncio.sleep(8.5)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    asyncio.run(main())
