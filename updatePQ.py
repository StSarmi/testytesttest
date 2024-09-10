#################################################################################################
# Innlesning av parametere fra utstyr i PQ-prosektet 
# Routine:			"updatePQ.py"  
# By: 				Per Dypvik
# Description: 			 
#				
#################################################################################################
# energiScada is a software suite to monitor, control and visualize different equipment 
# in a LES (local energy system) like battery inverter/chargers, solar inverters and different 
# monitoring and control equipment.
#################################################################################################
# Dependencies: 
#
#################################################################################################
#	Monitored parameters are imported from elsinPQ.py with
###########################################################################################################

import asyncio, time
import sys,json
#sys.path.append("/home/openhabian/.local/lib/python2.7/site-packages")

from elsinPQ import readbatteryValues as readBattery, xtenders as readXtenders, contactors as readContactors, readcurrentIn, readcurrentOut, readpowerLimit
from state import Variables, State

async def main():

        state_manager = State()

        while True:
            try:
                tidStart = time.time()
                try:
                    contactors = readContactors()
                    battery = readBattery()
                    xtenders = readXtenders()
                    currentIn = readcurrentIn()
                    currentOut = readcurrentOut()
                    powerLimit = readpowerLimit()
                    #print("\r\n\t", battery,"\r\n\t", xtenders,"\r\n\t",currentIn,"\r\n\t",currentOut,"\r\n\t",powerLimit)
                    #print(f'\r\n\t  - Avlesning og lagring av verdiene tok {time.time()-tidStart:.2f} sekunder\r\n')
                    state_manager.set_variable(Variables.contactorValues, contactors)
                    state_manager.set_variable(Variables.batteryValues, battery)
                    state_manager.set_variable(Variables.xtenderValues, xtenders)
                    state_manager.set_variable(Variables.currentInValues, currentIn)
                    state_manager.set_variable(Variables.currentOutValues, currentOut)
                    state_manager.set_variable(Variables.powerLimit, powerLimit)
                    print("\r\n\t",contactors,"\r\n\t",battery,"\r\n\t", xtenders,"\r\n\t",currentIn,"\r\n\t",currentOut,"\r\n\t",powerLimit)
                    print(f'\r\n\t  - Avlesning og lagring av verdiene tok {time.time()-tidStart:.2f} sekunder\r\n')
                except:
                    print (" - feil ved skriving til db -xtenderValues")
                await asyncio.sleep(11.15)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    asyncio.run(main())
