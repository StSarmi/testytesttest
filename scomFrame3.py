#############################################################################
# Routine:		"scomFrame.py"  
# Date: 		October 28th, 2016
# By: 			Per Dypvik
# Description: 	This library contain small utilit programs to make the frames 
#               needed to communicate with the Xtender with Xcom LAN and 
#               via a Digi WR21.# A simple test of the SCOM serial protocol on 
#               Studer Xtender equipment.
#               The Studer "SCOM-protocol" is available on TCP socket using 
#               the IP adress to the gateway and its port set up for the 
#               Xcom-232i (gw and Xcom-232i is together the Xcom-LAN).
# Contents:
#               checksum(): finds the checksum used for SCOM messages
#               bytearray_to_string: converts - you guessed it
#               string_to_bytearray: converts back
#
#
# Improvements: The WR21/WR31 can do all functions of the gateway, making a simpler and 
#               less expensive solution. 
###############################################################################

def checksum(hexStr):
#############################################################################
# 	Input:  bytearray
#   Output: bytearray
#   Description:
#   This routine take a bytearray, calculates its crc value,  adds it to 
#   the bytearray and returns the resulting bytearray with crc
#############################################################################
    
    data = hexStr
    crc_value = bytearray([0xff,0x00])

    i = 0
    length = len(data)
    while (i < length):
        crc_value[0] = (crc_value[0] + data[i]) % 0x100       # modulus is % in python
        crc_value[1] = (crc_value[1] + crc_value[0]) % 0x100
        i = i+1
    
    return (crc_value)

def bytearray_to_string (hexStr):
#############################################################################
# 	Input:  bytearray
#   Output: string
#   Description:
#   This routine take a bytearray, and converts each byte to two hex ciphers  
#   followed by a comma without spaces. The comma after the last cipher is removed 
#   Data checks:
#   None
#############################################################################

    hexStr = str(hexStr)[12:-2]
    out_list = []
    i = 0
    while i < len(hexStr):
        # Items on the format \x00
        if hexStr[i:i+2] == '\\x':
            out_list.append(hexStr[i+2:i+4])
            i += 4
        # Items that are escaped characters like \n
        elif hexStr[i] == '\\':
            nxt = hexStr[i+1]
            escape_ascii_codes = {
                    'a': "07",
                    'b': "08",
                    't': "09",
                    'n': "0a",
                    'v': "0b",
                    'f': "0c",
                    'r': "0d",
                    '\\': '5c',
            }
            
            out_list.append(escape_ascii_codes[nxt])
            i += 2
        # Items that are actual ascii characters
        else:
            out_list.append("{0:x}".format(ord(hexStr[i])))
            i += 1

    return ','.join(out_list)


def string_to_bytearray (hexStr):
#############################################################################
# 	Input:  string
#   
#   Output: bytearray
#
#   Description:
#   This routine take a string with hex divided by comma separator without 
#   spaces, and converts it to bytearray.
#
#   Data checks:None.
#   The string must contain hex ciphers, and be separated by comma without spaces. 
#############################################################################

    ba = bytearray()

    hexStr = ''.join(str(hexStr).split(" "))

    for i in range(0, len(hexStr), 3):
        a = int(hexStr[i:i+2], 16)
        ba.append(a)

    return ba

