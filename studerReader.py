
######################################################################
#   read all values from studer equipment in a system 
#   Routine:    studerReader.py
#   modules:    pymodbus, asyncio, json, math, openhab
#   other:      
######################################################################
# Benytt 0.1s delay mellom hver avlesning

import asyncio, json, time, math

"""
from openhab import OpenHAB
base_url='http://localhost:8080/rest'
openhab = OpenHAB(base_url)

contactorValues = openhab.get_item('contactorValues')
xtsValues = openhab.get_item('xtsValues')
batteryValues = openhab.get_item('battery1Values')
currentInValues = openhab.get_item('currentInValues')
voltOutValues = openhab.get_item('voltOutValues')
"""
from state import Variables, State
from studerParameter import readFase 
readDelay = 0.0

DI1 = 1
DI2 = 2
DI3 = 3

def lesDI(DIno):
    command = os.popen("iotg-imx8plus-dio -i" + str(DIno))
    result = command.read()
    command.close()
    return (result)

def readContactors():
# sjekk status på alle kontaktorene i systemet.
    try:
        bfsAktivK2 = int(lesDI(DI2)[0])
    except:
        bfsAktivK2=None         # K2 connect bfs to load
    try:
        bypassAktivK1 = int(lesDI(DI1)[0])
    except:
        bypassAktivK1 = None
    try:
        isolerK3 = int(lesDI(DI3)[0])
    except:
        isolerK3 = None
    try:
        time.sleep(readDelay)
        xtTransfer1 = readFase(1,3020)    # read transfer relay status
        if xtTransfer1 not in [0,1]:xtTransfer1 = None 
    except:
        xtTransfer1 = None
    try:
        time.sleep(readDelay)
        xtTransfer2 = readFase(2,3020)    # read transfer relay status
        #if xtTransfer2 not in [0,1]:xtTransfer2 = None 
    except:
        xtTransfer2 = None
    try:
        time.sleep(readDelay)
        xtTransfer3 = readFase(3,3020)    # read transfer relay status
        #if xtTransfer3 not in [0,1]:xtTransfer3 = None 
    except:
        xtTransfer3 = None
    
    return ({"unit":"BfS", "bfsAktivK2":bfsAktivK2, "bypassAktivK1":bypassAktivK1, "isolerK3":isolerK3, "XT1transfer":xtTransfer1, "XT2transfer":xtTransfer2, "XT3transfer":xtTransfer3 })

def readBattery():
    #########################################################################
    # Rutine for å lese batteriverdiene fra et batteri styrt over CAN av Studer 
    #########################################################################
    #
    try:
        time.sleep(readDelay)
        battery1Temp=readFase(1,7029)
    except:
        battery1Temp = None
    try:
        time.sleep(readDelay)
        battery1Voltage = readFase(1,7000)
    except:
        battery1Voltage = None
    try:
        time.sleep(readDelay)
        battery1Current=readFase(1,7031)            # make a frame format, 7031 is minute avg battery current via CAN
    except:
        battery1Current = None
    try:    # read battery1SoC
        time.sleep(readDelay)
        battery1SoC = readFase(1,7032)
    except:
        battery1SoC = None
    try:    # read battery1SoH
        time.sleep(readDelay)
        battery1SoH = readFase(1,7057)
    except:
        battery1SoH = None
    return ({"unit":"WECOx3","batteryVoltage":battery1Voltage,"batteryCurrent":battery1Current,"batteryTemp":battery1Temp,"batterySoC":battery1SoC,"batterySoH":battery1SoH})

def readXtenders():
    try:
        time.sleep(readDelay)
        xtStatus1 = readFase(1,3049)
        if xtStatus1 not in [0,1]:xtStatus1 = None 
    except:
        xtStatus1 = None
    try:
        time.sleep(readDelay)
        xtStatus2 = readFase(2,3049)
        if xtStatus2 not in [0,1]:xtStatus2 = None 
    except:
        xtStatus2 = None
    try:
        time.sleep(readDelay)
        xtStatus3 = readFase(3,3049)
        if xtStatus3 not in [0,1]:xtStatus3 = None 
    except:
        xtStatus3 = None
    try:
        time.sleep(readDelay)
        xts1Temp=readFase(1,3103)            # make a frame format, 3103 is minute max Xtender temp 1
    except:
        xts1Temp = None
    try:
        time.sleep(readDelay)
        xts2Temp=readFase(2,3103)            # make a frame format, 3103 is minute max Xtender temp 1
    except:
        xts2Temp = None
    try:    
        time.sleep(readDelay)
        xts3Temp=readFase(3,3103)            # make a frame format, 3103 is minute max Xtender temp 1
    except:
        xts3Temp = None
    try:    # read acOutV1, in and out voltage always equal with transfer closed
        time.sleep(readDelay)
        AcOutV1 = readFase(1,3113)
    except:
        AcOutV1 = None
    try:    # read acOutV2, in and out voltage always equal with transfer closed
        time.sleep(readDelay)
        AcOutV2 = readFase(2,3113)
    except:
        AcOutV2 = None
    try:    # read acOutV3, in and out voltage always equal with transfer closed
        time.sleep(readDelay)
        AcOutV3 = readFase(3,3113)
    except:
        AcOutV3 = None
    return ({"unit":"Xtenders","sxtStatus1":xtStatus1,"sxtStatus2":xtStatus2,"sxtStatus3":xtStatus3,"electronicsTemp1":xts1Temp,"electronicsTemp2":xts2Temp,"electronicsTemp3":xts3Temp,"acOutV1":AcOutV1,"acOutV2":AcOutV2,"acOutV3":AcOutV3})


def readCurrentIn():
    try:
        time.sleep(readDelay)
        currentInL1 = readFase(1,3115)
    except:
        currentInL1 = None
    try:
        time.sleep(readDelay)
        currentInL2 = readFase(2,3115)
    except:
        currentInL2 = None
    try:
        time.sleep(readDelay)
        currentInL3 = readFase(3,3115)
    except:
        currentInL3 = None
    return ({"unit":"Xtenders", "currentInL1":currentInL1, "currentInL2":currentInL2,"currentInL3":currentInL3})

def readPowerLimit():
    try:
        time.sleep(readDelay)
        powerLimit1 = readFase(1,3017)
    except:
        powerLimit1 = None
    try:
        time.sleep(readDelay)
        powerLimit2 = readFase(2,3017)
    except:
        powerLimit2 = None
    try:
        time.sleep(readDelay)
        powerLimit3 = readFase(3,3017)
    except:
        powerLimit3 = None
    try:
        powerLimitTarget = round(openhab.get_item('XT_Imaxtarget').state,0)
    except:
        powerLimitTarget = None
    return ({"unit":"Xtenders","powerLimitTarget":powerLimitTarget,"powerLimit1":powerLimit1,"powerLimit2":powerLimit2,"powerLimit3":powerLimit3})

async def main():
        state_manager = State()
        while True:
            try:
                tidStart = time.time()
                """
                #try:
                print(readContactors())
                print(readBattery())
                xtenderValue = readXtenders()
                print (xtenderValue)
                print (xtenderValue['acOutV1'])

                print(readCurrentIn())
                print(readPowerLimit())
                """
                try:
                    state_manager.set_variable(Variables.contactorStatus, readContactors())
                    state_manager.set_variable(Variables.battery1Values, readBattery())
                    state_manager.set_variable(Variables.xtenderValues, readXtenders())
                    state_manager.set_variable(Variables.currentInValues, readCurrentIn())
                    state_manager.set_variable(Variables.powerLimit, readPowerLimit())
                except:
                    print (" - feil ved skriving til db -xtenderValues")
                    pass
                #mellomTid = time.time()
                print(f'\r\n\t-Avlesning av utstyr tok {time.time()-tidStart:.2f} sekunder\r\n')
                """
                try:
                    print("fra db:")
                    print(state_manager.get_variable(Variables.contactorStatus))
                    print(state_manager.get_variable(Variables.battery1Values))
                    print(state_manager.get_variable(Variables.xtenderValues))
                    print(state_manager.get_variable(Variables.currentInValues))
                    print(state_manager.get_variable(Variables.powerLimit))
                except:
                    print (" - feil ved lesing fra db -xtenderValues")
                    pass
                
            
                contactorStatus = 27  # Contactors JSON string
                battery1Values = 28  # Battery1 JSON string
                battery2Values = 29  # Battery2 JSON string
                xtenderValues = 30  # Xtender JSON string
                currentInValues = 31  # currentIn JSON string
                currentOutValues = 32  # currentOut JSON string
                powerLimit = 33  # powerLimit JSON string
                XT_Imaxtarget = 34  # Target for Imax
                
                
                currentOutTable = json.dumps(currentOutTable)
                currentOutValues.state = currentOutTable

                print(f'\r\n\t-Lese fra db tok {time.time() - mellomTid:.2f} sekunder\r\n')
                """

                await asyncio.sleep(8.5)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    asyncio.run(main())
