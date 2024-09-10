#################################################################################################
# Implementation of the serial protocol SCOM for Studer Xtender/Variostring
# Routine:      "studerCtrlv2.py"  
# Date:         November 1st, 2016
# Revision:     - as used in Sikkilsdalen, March 13th 2023. Support 3 phases/6 Xtenders
# Revisionv2:   - to be used with python3.9 using scomFrame3 April 2nd, 2023 
#               - to use only one usbport April 25th, 2024
# By:           Per Dypvik
# Description:  energiScada is connected via Studer Xcom-232i to different Studer equipment
#               (Xtenders, Variostring) over CAN-bus. energiScada uses the Studer "SCOM-protocol" 
#               and makes it available to applications.
#################################################################################################
#
#    energiScada(TM) is a system built to monitor, control and visualize equipment like battery 
#    inverter/chargers, solar inverters and different monitoring and control equipment. 
#   
#################################################################################################

def makeProperty(propertyId, frameLength, parameterType, parameterValue):
#################################################################################################
# Function:     The routine encodes the parameterValue according to 'Studer-format'
#               and appends the value to the propertyId
# Input:        propertyId: is a two byte value separated by comma, i.e. '0A,00' 
#               frameLength: no of bytes before additions as a similiar value 
#               parameterType: either 'int', 'float' or 'bool', and
#               parameterValue: its value in the corresponding format
# Output:       The routine returns the string with parameterValue appended to
#               the propertyId, as well as a string with the new bytes
#               added to frameLength. If error occurs, it returns <nil>
#################################################################################################
    levelOnly =   [1101,1129,1137,1141,1186,1197,1201,1203,1204,1208,1212,1216,1220,1245,1257,\
                1269,1270,1274,1278,1282,1310,1312,1313,1317,1321,1325,1329,1353,1366,1378,\
                1379,1383,1387,1420,1451,1452,1453,1454,1455,1456,1471,1484,1489,1501,1502,\
                1503,1504,1522,1531,1537,1568]

    int32Type = [1142,1162,1202,1206,1207,1210,1211,1214,1215,1218,1219,1222,1223,1272,1273,1276,1277,1280,1281,\
                    1287,1315,1316,1319,1320,1323,1324,1327,1328,1331,1332,1381,1382,1385,1386,1389,1390,1395,\
                    1399,1415,1467,1468,1525,1526,1545,1569,1570,5001,5002,5041,6073]

    floatType = [1107,1108,1109,1110,1112,1121,1122,1138,1139,1140,1143,1144,1145,1146,1148,1156,1157,1159,\
                    1161,1164,1165,1166,1169,1171,1172,1174,1175,1176,1187,1188,1189,1190,1195,1198,1199,1200,\
                    1247,1248,1250,1251,1253,1254,1255,1256,1259,1260,1262,1263,1265,1266,1267,1268,1285,1286,\
                    1290,1295,1297,1298,1304,1305,1307,1309,1356,1357,1359,1360,1362,1363,1364,1365,1368,1369,\
                    1371,1372,1374,1375,1376,1377,1391,1404,1405,1432,1433,1440,1441,1443,1444,1447,1448,1458,\
                    1459,1492,1493,1494,1505,1506,1507,1510,1514,1515,1523,1524,1533,1534,1546,1553,1559,1560,\
                    1565,1567,1567,1574,1580,1581,1583,1584,1586,1587,1588,1590,1592,1593,1595,1596,1597,1599,\
                    1607,1613,1622,1623,1624,1629,1630,1631,3000,3001,3002,3003,3004,3005,3006,3007,3008,3009,\
                    3011,3012,3013,3017,3021,3022,3023,3045,3046,3047,3050,3076,3078,3080,3081,3082,3083,3084,\
                    3085,3087,3088,3089,3090,3091,3092,3093,3094,3095,3096,3097,3098,3099,3100,3101,3103,3111,\
                    3113,3115,3116,3119,3124,3125,3136,3137,3138,3139,3155,6055,6056,6001,6062,6063,6067,6069,6070,\
                    6074,6075,7000,7001,7002,7003,7007,7008,7009,7010,7011,7012,7013,7029,7030,7031,7032,7047,\
                    7055,7057,7059,7061,7062,7063,7064,7065,7066]

    boolType = [1111,1124,1125,1126,1127,1128,1130,1131,1132,1134,1147,1149,1155,1158,1160,1163,1168,1170,\
                1173,1191,1194,1225,1226,1227,1228,1229,1231,1232,1233,1234,1235,1236,1237,1238,1239,1240,\
                1242,1243,1244,1246,1249,1252,1258,1261,1264,1283,1284,1288,1291,1296,1333,1334,1335,1336,\
                1337,1339,1340,1341,1342,1343,1344,1345,1346,1347,1348,1350,1351,1352,1354,1355,1358,1361,\
                1367,1370,1373,1436,1437,1438,1439,1442,1446,1457,1461,1462,1485,1486,1491,1500,1512,1513,\
                1516,1517,1518,1519,1520,1521,1527,1536,1538,1539,1540,1541,1542,1543,1544,1547,1548,1549,\
                1550,1551,1555,1556,1557,1558,1566,1566,1571,1572,1575,1576,1577,1578,1579,1582,1585,1589,\
                1591,1594,1598,1600,1601,1602,1608,1610,1615,1616,1617,1618,1619,1620,1621,1627,1628,1646,\
                1647,6068,6071,6072]

    enumType = [1205,1209,1213,1217,1221,1271,1275,1279,1311,1314,1318,1322,1326,1330,1380,1384,1388,\
                1497,1498,1532,1552,3010,3020,3028,3030,3031,3032,3049,3160,6057]

    writeList = [1107,1108, 1109, 1110, 1121, 1122, 1124, 1126, 1127, 1128, 1138, 1140, 1142, 1143, 1143, 1144, 1145, 1155, 1156, \
                    1157, 1158, 1173, 1174, 1187, 1202, 1246, 1249, 1252, 1283, 1286, 1287, 1395, 1399, 1415, 1436, 1438, 1439, 1440,\
                    1441, 1462, 1468, 1516, 1523, 1524, 1525, 1526, 1539, 1541, 1542, 1545, 1546, 1550, 1552, 1578, 1581, 1588,\
                    1589, 1615, 5041, 6062, 6063, 6067, 6068, 6069, 6070, 6071,6072,6073,6074,6075]
    

    import struct
    from scomFrame3 import bytearray_to_string, string_to_bytearray
    
    if (parameterType=='int32'): 
        parameterValue = struct.pack('<I',int(parameterValue))
        increment = 4               # add 4 bytes to frameLength 
    elif (parameterType=='float'):  
        parameterValue = struct.pack('<f',int(parameterValue))
        increment = 4               # add 4 bytes to frameLength 
    elif (parameterType=='bool'):   # bool is a 1 byte integer with value 0 or 1, should add ',01'
        parameterValue = struct.pack('<B',int(parameterValue))
        increment = 1               # add 1 byte to frameLength 
    else:   
        return '<nil>'
    
    #print ("PrameterValue:", parameterValue)
    propertyId = bytearray_to_string(bytearray(string_to_bytearray(propertyId)+parameterValue))
    #print (propertyId)
    frameLength = bytearray_to_string(bytearray(struct.pack('<h',struct.unpack('<h',bytearray(string_to_bytearray(frameLength)))[0]+increment)))
    #print (frameLength)

    return (propertyId, frameLength)
    
def parameterId(*args):
###############################################################################
# Indata:       the xtender offset and object number (=Studer parameter 1xxx/30xx/31xx) 
#               as a decimal number. If the command is write: parameterType and parameterValue 
#               are also input
# Outdata:      the complete frame with checksums, as a string separated with commas 
#               between each byte of data (two ciphres)
#               If any error occur, the routine returnes "<nil>"
# Description:  In order to retrieve data on any parameter from the Studer equipment,
#               a SCOM parameterId message is sent. All parameterId frames are identical,
#               differing only in object_id and thus also in the message_checksum. 
#               The routine give all parameters in the frame their values
#               If the input 'mode' is 'write' then parameterType and parameterValue 
#               are used to append data and change data_length info.
#               Command 'read' is assumed for all other modes than 'write'
###############################################################################
    from scomFrame3 import checksum, bytearray_to_string, string_to_bytearray
    
    #print (len(args), args, type(args[0]), type(args[1]))

    test = len(args)

    if test == 2:
        objectId = args[1]
        mode ='read'
    if test >= 2:
        studerAddress = '64,00,00,00'   # see dst_addr
        if (int(args[0]) == 1): studerAddress='65,00,00,00'
        elif (int(args[0])==2): studerAddress='66,00,00,00'
        elif (int(args[0])==3): studerAddress='67,00,00,00'
        elif (int(args[0])==4): studerAddress='68,00,00,00'
        elif (int(args[0])==5): studerAddress='69,00,00,00'
        elif (int(args[0])==6): studerAddress='6A,00,00,00'
        elif (int(args[0])==9): studerAddress='F5,01,00,00' # RCC cannot be addressed with 9 XTenders        
        objectId = args[1]
        if ((objectId >= 6000) and (objectId < 7000)):
            studerAddress='59,02,00,00' # BSP info
        #print studerAddress
    else:
        print ("See line 96 in studerCtrl.py")
        return ('<nil>')
    if test >= 4:
        mode=args[2]
        parameterType=args[3]
        parameterValue=args[4]
#       print args

        
#    print args, test

# General content for all parameterId request frame from DTE (Scada)
    start_byte =    'AA'
    frame_flags =   '00'
    source_addr =   '01,00,00,00'
    dst_addr =      studerAddress           # 0x64 = 100: all, 101 XTM, 102 XTS, 501 RCC/Xcom-232i, 601 BSP
    data_length =   '0A,00'                 # all READ_PROPERTY service is the size of 10 bytes 

    
#################################################################################
# test the parameterID to identify the info type and make the object_type as string
#################################################################################
#   '01,00' is 'User info' objects, 
#   '02,00' for changeable objects, 
#   '03,00' for messages and 
#   '04,00' for file transfer
#################################################################################
    if objectId < 1000 : 
        print ("See line 124 in studerCtrl.py")
        return "<nil>"
    elif ((objectId < 2000) or ((objectId >= 6000) and (objectId < 7000))) : object_type = '02,00'  # holding register if modbus
    elif objectId < 3000: 
        print ("See line 113 in studerCtrl.py")
        return "<nil>"
    elif (objectId <4000): object_type = '01,00'    # 'read' for all user_info's 3xxx 
    elif (objectId <6000): object_type = '02,00'    # 'read' for all user_info's and 5xxx
    elif ((objectId >= 7000) and (objectId < 7200)): object_type = '01,00'  # 'read' for all user_info's
    elif objectId >= 7200: 
        print ("See line 130 in studerCtrl.py")
        return "<nil>"

    
#################################################################################
# Then, make the object_id as a string
#################################################################################
# But, we need to replace the object_id based on input parameter, and make a new checksum
# First, translate the objectID parameter in decimal to a least endian, 4 byte bytearray and make it a string

    object_id =([0,0,0,0])
    object_id[0] = objectId % 0x100                    # the rest after dividing by 256
    object_id[1] = (objectId - object_id[0]) // 0x100    # better be an hex :-)
    #print(object_id)

    object_id = bytearray_to_string(bytearray(object_id))

# So to the service specific content of the frame, the 10 bytes data
    service_flags ='00'                 # all flags zero from DTE
    service_id = '01'                   # service_id is 01 on all read requests, 02 on write
    property_id = '05,00'               # property depending on request
    
    if ((objectId >= 3000) and (objectId < 4000)):
        property_id = '01,00'               # property depending on request
        
    
##############################################################################
#
#   So far, read has been assumed. If ths is a write request, we need to modify:
#   - service_id to '02'
#   - add a number of bytes to the data_length depending on parameterType
#   - add parameterValue to the message_frame. Property_id is kept
#
###############################################################################

    if (mode == 'write'):   
        service_id ='02'
        #print "ParameterType:", parameterType
        if parameterType == 'bool':
            property_id ='05,00'        # new property: sets value in RAM, not in flash. Not necessary to use <1550> any more
        if parameterType == 'int':
            property_id ='05,00'
        if parameterType== 'float':
            property_id='05,00'
        if (studerAddress=='F5,01,00,00'):
            property_id='05,00'
            object_type ='02,00'

        property_id,data_length=makeProperty(property_id,data_length,parameterType,parameterValue)  #append the parameterValue to property_id


# Convert the frame_header to a bytearray and make the checksum omitting the start byte
    frame_header = start_byte+','+frame_flags+','+source_addr+','+dst_addr+','+ data_length
    frame_header_bytearray = string_to_bytearray(frame_header)  
    header_checksum = bytearray_to_string(checksum(frame_header_bytearray[1:]))    # should return '6f,71'
# Then make the complete frame_header as a string
    frame_header = bytearray_to_string(frame_header_bytearray)+','+header_checksum    
# OK? Then make the message_frame, convert to bytearray and make the checksum
    message_frame = service_flags+','+service_id+','+object_type+','+object_id+','+property_id
    message_frame_bytearray = bytearray(string_to_bytearray(message_frame))    
    message_checksum = bytearray_to_string(checksum(message_frame_bytearray))
# All content is ready, lets make the complete parameterIdFrame and return
    parameterIdFrame = frame_header+','+message_frame+','+message_checksum

    return (parameterIdFrame)

def doRead(ser,term):
    import re, time
    BUFFER_SIZE = 255

    matcher = re.compile(term)    #gives you the ability to search for anything
    tic     = time.time()
    buff    = bytearray() # ser.read(noBytes)
    while (((time.time() - tic) < 0.17) and (not matcher.search(buff.decode()))):
        try:
            buff += ser.read(BUFFER_SIZE)
        except:
            time.sleep(0.01)
            
    return buff


def tsReadparameterId(parameterIdFrame, usbport):
    import os
    from time import sleep
    from datetime import datetime

    # hvis filen finnes og er mer enn 3 sek gammel, slett
    d_unix = datetime.timestamp(datetime.now())
    file_age_unix = d_unix
    if os.path.exists("/tmp/scomlock.txt"):
        file_age_unix = os.path.getmtime("/tmp/scomlock.txt")
    if file_age_unix > d_unix + 3:
        os.remove("/tmp/scomlock.txt")

    while os.path.exists("/tmp/scomlock.txt"):
        sleep(0.1)

    open("/tmp/scomlock.txt", 'w').close()

    data = None
    try:
        data = readparameterId(parameterIdFrame, usbport)
    except:
        pass
    finally:
        os.remove("/tmp/scomlock.txt")

    return data


def readparameterId(parameterIdFrame,usbport):
###############################################################################
# Indata:       the complete frame to send over SCOM, but in string format
# Outdata:      the SCOM response in string format
#
# In and out data to the routine is string as described in string_to_bytearray 
# and bytearray_to_string. All communication on SCOM is in bytearray format
###############################################################################

    import serial
    from scomFrame3 import string_to_bytearray, bytearray_to_string

    parameterIdFrame_bytearray = string_to_bytearray(parameterIdFrame)
    #CR = "\r\n"
    #BUFFER_SIZE = 255
    #data = "<nil>" 
    
    # USB serial routine
    ser = serial.Serial()
    ser.port = usbport #"/dev/ttyUSB4"
    ser.baudrate = 38400
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_EVEN #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    ser.timeout = 0.17              #timeout block read
    
    try: 
        ser.open()
    except Exception as e:
        #print ("error open serial port: ") + str(e)
        exit()
        
# ask for all data and get response
    ser.write(parameterIdFrame_bytearray)   #string_to_bytearray(parameterIdFrame))     # exekveres ikke
    data = doRead(ser,term='!')
    if data == '<nil>': 
        ser.close()
        return (data)
    result = bytearray_to_string(data)
    ser.close()

    return(result)

def checkMode(testdata):
    try:
        unit = int(testdata[0])
        mode = testdata[2:7]
        if mode == 'read ':
            paraId = testdata[7:]
            mode='read'     # remove trailing space
        elif mode =='write':
            paraId = testdata[8:]
        else:
            mode = "false"
            paraId = "false"
    except:
        mode = "false"
        paraId = "false"
    #print ("Unit", unit, "Mode:", mode, "paraId:", paraId)
#   print testdata[0], testdata[2:7], testdata[7:], testdata[8:]
    
    return (unit, mode,paraId) 

def CRCtest(response):
    from scomFrame3 import checksum, bytearray_to_string, string_to_bytearray
    print ("Response: ", response, "\r\n")
    if ((len(response) < 77) or (len(response) >= 90)): 
        print ("Parameter benyttes ikke pga. feil meldingslengde", len(response), "\r\n")
        return (False)
    calculated_CRC = (bytearray_to_string(checksum(string_to_bytearray(response[42:len(response)-6]))))
    received_CRC = response[len(response)-5:]
    if (calculated_CRC != received_CRC): 
        print ("Parameter benyttes ikke pga. feil i mottatt CRC:", received_CRC,"som skulle vært:", calculated_CRC, "\r\n")
        return (False)
    print ("Parameter benyttes da melding har riktig meldingslengde:", len(response), "og CRC:", received_CRC, "\r\n")
    return (True)

def main():
    # husk å sjekke usb før idriftsettelse Sunda, gjelder også setupElviafbiSunda
    usbport =  "/dev/serial/by-id/usb-FTDI_Chipi-X_FT2UXR6I-if00-port0"   # kun en usbport siden det leveres som enhetlig system
    phase1usb = usbport #"/dev/serial/by-id/usb-FTDI_UC232R_FT67GCMA-if00-port0"
    phase2usb = usbport #"/dev/serial/by-id/usb-FTDI_UC232R_FT67GCMA-if00-port0"
    phase3usb = usbport #"/dev/serial/by-id/usb-FTDI_UC232R_FT67GE3D-if00-port0"
    meterusb = "/dev/serial/by-id/usb-FTDI_USB-RS485_Cable_FT2JDXL0-if00-port0"
    import sys, os, time, struct, binascii
    import datetime as DT
    from timeit import default_timer as timer

    from scomFrame3 import checksum, bytearray_to_string, string_to_bytearray
            
    levelOnly =   [1101,1129,1137,1141,1186,1197,1201,1203,1204,1208,1212,1216,1220,1245,1257,\
               1269,1270,1274,1278,1282,1310,1312,1313,1317,1321,1325,1329,1353,1366,1378,\
               1379,1383,1387,1420,1451,1452,1453,1454,1455,1456,1471,1484,1489,1501,1502,\
               1503,1504,1522,1531,1537,1568]

    int32Type = [1142,1162,1202,1206,1207,1210,1211,1214,1215,1218,1219,1222,1223,1272,1273,1276,1277,1280,1281,\
                 1287,1315,1316,1319,1320,1323,1324,1327,1328,1331,1332,1381,1382,1385,1386,1389,1390,1395,\
                 1399,1415,1467,1468,1525,1526,1545,1569,1570,5001,5002,5041,6073]

    floatType = [1107,1108,1109,1110,1112,1121,1122,1138,1139,1140,1143,1144,1145,1146,1148,1156,1157,1159,\
                 1161,1164,1165,1166,1169,1171,1172,1174,1175,1176,1187,1188,1189,1190,1195,1198,1199,1200,\
                 1247,1248,1250,1251,1253,1254,1255,1256,1259,1260,1262,1263,1265,1266,1267,1268,1285,1286,\
                 1290,1295,1297,1298,1304,1305,1307,1309,1356,1357,1359,1360,1362,1363,1364,1365,1368,1369,\
                 1371,1372,1374,1375,1376,1377,1391,1404,1405,1432,1433,1440,1441,1443,1444,1447,1448,1458,\
                 1459,1492,1493,1494,1505,1506,1507,1510,1514,1515,1523,1524,1533,1534,1546,1553,1559,1560,\
                 1565,1567,1567,1574,1580,1581,1583,1584,1586,1587,1588,1590,1592,1593,1595,1596,1597,1599,\
                 1607,1613,1622,1623,1624,1629,1630,1631,3000,3001,3002,3003,3004,3005,3006,3007,3008,3009,\
                 3011,3012,3013,3017,3021,3022,3023,3045,3046,3047,3050,3056,3076,3078,3080,3081,3082,3083,3084,\
                 3085,3087,3088,3089,3090,3091,3092,3093,3094,3095,3096,3097,3098,3099,3100,3101,3103,3111,\
                 3113,3115,3116,3119,3124,3125,3136,3137,3138,3139,3155,6055,6056,6001,6062,6063,6067,6069,6070,\
                 6074,6075,7000,7001,7002,7003,7007,7008,7009,7010,7011,7012,7013,7029,7030,7031,7032,7047,\
                 7055,7057,7059,7061,7062,7063,7064,7065,7066]

    boolType = [1111,1124,1125,1126,1127,1128,1130,1131,1132,1134,1147,1149,1155,1158,1160,1163,1168,1170,\
                1173,1191,1194,1225,1226,1227,1228,1229,1231,1232,1233,1234,1235,1236,1237,1238,1239,1240,\
                1242,1243,1244,1246,1249,1252,1258,1261,1264,1283,1284,1288,1291,1296,1333,1334,1335,1336,\
                1337,1339,1340,1341,1342,1343,1344,1345,1346,1347,1348,1350,1351,1352,1354,1355,1358,1361,\
                1367,1370,1373,1436,1437,1438,1439,1442,1446,1457,1461,1462,1485,1486,1491,1500,1512,1513,\
                1516,1517,1518,1519,1520,1521,1527,1536,1538,1539,1540,1541,1542,1543,1544,1547,1548,1549,\
                1550,1551,1555,1556,1557,1558,1566,1566,1571,1572,1575,1576,1577,1578,1579,1582,1585,1589,\
                1591,1594,1598,1600,1601,1602,1608,1610,1615,1616,1617,1618,1619,1620,1621,1627,1628,1646,\
                1647,6068,6071,6072]

    enumType = [1205,1209,1213,1217,1221,1271,1275,1279,1311,1314,1318,1322,1326,1330,1380,1384,1388,\
                1497,1498,1532,1552,3010,3020,3028,3030,3031,3032,3049,3160,6057]
    
    writeList = [1107,1108, 1109, 1110, 1121, 1122, 1124, 1126, 1127, 1128, 1138, 1140, 1142, 1143, 1143, 1144, 1145, 1155, 1156, \
                 1157, 1158, 1173, 1174, 1187, 1202, 1246, 1249, 1252, 1283, 1286, 1287, 1395, 1399, 1415, 1436, 1438, 1439, 1440,\
                 1441, 1462, 1468, 1510, 1516, 1523, 1524, 1525, 1526, 1539, 1541, 1542, 1545, 1546, 1547,1550, 1552, 1578, 1581, 1588,\
                 1589, 1615, 5041, 6062, 6063, 6067, 6068, 6069, 6070, 6071,6072,6073,6074,6075]
    

    specialBool = [1554, 'expert', 'on/off']
    
    acceptScada = 1550
    mode = ''
    delay = 1

    while True:
        testdata = input("\r\n\r\nUse command '<id#> read <parameter>' or '<id#> write <parameter>'): ")
        startTime=timer()
        xtender, mode, paraId = checkMode(testdata)
        objectId = paraId
        parameterType = "not found"
        try:
            if int(xtender) not in [0,1,2,3,9]:
                print ("id is xtender #, use 0 for all and 9 for RCC/XCom-232i")
                parameterType = '<nil>'
            elif int(objectId) in levelOnly:
                parameterType = 'lo'
                break
            elif int(objectId) in int32Type:
                parameterType = 'int32'
                break
            elif int(objectId) in floatType:
                parameterType = 'float'
                break
            elif int(objectId) in boolType:
                parameterType = 'bool'
                break
            elif int(objectId) in enumType:
                parameterType = 'short enum'
                break
            elif int(objectId) in specialBool:
                parameterType = 'boolExpert'
                break
            else:
                print ("Not a valid Studer parameter")
        except: 
            print ("Use the syntax '# read <para>' or '# write <para> with #=0,1,2,3 and para between 1000 and 15000")

    usbport= phase1usb

    if (mode == 'read'):
        print ("The selected parameter should return a value of type: ", parameterType, "from port",usbport, "\r\n")

        data = parameterId(int(xtender),int(objectId))          # 'read' is default
        print ("Request:  ", data)    
        response = tsReadparameterId(data,usbport)
        print ("Response:", response, '\r\n')
        ##############################
        # Validity check of received data
        ##############################
        if (CRCtest(response) == 0): print ("Error reading, try again") 
        elif parameterType == 'lo':
            print ("Sorry, cant interpret this one yet")
        elif parameterType == 'int32':
            value_bytearray = string_to_bytearray(response) # [24:28] # Slice flyttet ned og justert på samme måte som float -Johannes
            #print (response, repr(value_bytearray), type(value_bytearray), len(value_bytearray))
            value =  struct.unpack("<I", value_bytearray[len(value_bytearray)-6:len(value_bytearray)-2])[0]
            if (int(objectId) == 5002):
                print("Date:", DT.datetime.utcfromtimestamp(value).isoformat())
            else: print ("The value of this int32 is: ", value)
        elif parameterType == 'float':
            value_bytearray = string_to_bytearray(response)
            lengthOfResponse = len(value_bytearray)
### Her har jeg endret fra ..[24:28] 
            floatPart=value_bytearray[lengthOfResponse-6:lengthOfResponse-2]    # the 4 bytes before the crc
            value = struct.unpack('<f', floatPart)
            print ("The value of this float is: ", value[0])
        elif parameterType == 'bool':
            value_bytearray = string_to_bytearray(response)[24]
            value = value_bytearray
            print ("The value of this boolean is: ", value)
            #print ("The value of this boolean is: ", struct.unpack('B',bytes(value)[0]))

        elif parameterType == 'short enum':
            value_bytearray = string_to_bytearray(response)[23:25]
            value = value_bytearray
            print ("The value of this short enum is: ", struct.unpack('>H',value)[0])   # only LSB is used
        else:
            print ("Not a valid Studer parameter")
        
    elif (mode == 'write'):
        if (int(objectId) in writeList):
            print ("Use system at usbport: ", usbport)
            print ("The selected parameter should have a value of type: ", parameterType)
            parameterValue = input("\r\n\tEnter value of the parameter: ")
#       print "Parameter value is:", parameterValue
            #print ("So, you want to change the parameter to", parameterValue,)
            print("\tPlease confirm changing parameter to", parameterValue, " (y/n):", end=' ')
            test = input()
            if ((test =='y') or (test =='yes') or (test =='Yes') or (test =='Y')):
                if (int(objectId) != 1550):
                    if(CRCtest(tsReadparameterId(parameterId(int(xtender), int(1550), 'write', 'bool', 0), usbport))): print ("\r\n\tEndrer 1550 til 0 først!\r\n") # start med å skriv 0 til 1550
                    time.sleep(delay)
                parameterValue = float(parameterValue)
                if (parameterType !='float'):parameterValue = int(parameterValue) 
                data = parameterId(int(xtender), int(objectId), 'write', parameterType, parameterValue)     
                print ("\r\nRequest:  ", data)
                print ("To usbport:   ", usbport)
                response = tsReadparameterId(data, usbport)
                print ("Response: ", response, '\r\n')
                # ##############################
                # # Validity check of received data
                # ##############################
                if (CRCtest(response) == 0): print ("Error reading, try again")
                elif parameterType == 'float':
                    value_bytearray = string_to_bytearray(data)
                    lengthOfResponse = len(value_bytearray)
        ### Her har jeg endret fra ..[24:28] 
                    floatPart=value_bytearray[lengthOfResponse-6:lengthOfResponse-2]    # the 4 bytes before the crc
                    value = struct.unpack('<f', floatPart)
                    print ("\r\nNew value of this float is: ", value[0])
                elif parameterType == 'short enum':
                    value_bytearray = string_to_bytearray(data)[24]
                    value = value_bytearray
                    print ("\r\nNew value of this enum is: ", value)
                elif parameterType == 'bool':
                    value_bytearray = string_to_bytearray(data)[24]
                    value = value_bytearray
                    print ("\r\nNew value of this boolean is: ", value)
                    #print ("The value of this boolean is: ", struct.unpack('B',bytes(value)[0]))
        else: print ("Not allowed to change that parameter yet")
        if (int(objectId) != 1550):
            time.sleep(delay)
            if(CRCtest(tsReadparameterId(parameterId(int(xtender), int(1550), 'write', 'bool', 1), usbport))): print ("\r\n\t..og avslutter med å sette  1550 tilbake til 1\r\n") # avslutt med å skrive 1 til 1550
    
    print ("\r\n\t\tTime used:", timer()-startTime, "sek\r\n")


    exit()

if __name__ == '__main__':
    
    main()
