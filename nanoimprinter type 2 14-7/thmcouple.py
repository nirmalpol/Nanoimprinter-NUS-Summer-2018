'''
    **********************************************************************************************************
    *   FILE NAME:      thmcouple.py
    *   AUTHOR:         Dylan Vogel,  Yu Dong (Peter) Feng
    *   PURPOSE:        This file contains the code for setting up & getting the readings of the thermocouples
    **********************************************************************************************************
'''
import spidev

global READBYTE
READBYTE = [0x00, 0x00]

#Set up 1st thermocouple
def setup1():
   tc_1 = spidev.SpiDev()
   tc_1.open(0,0)
   tc_1.max_speed_hz = 5000000
   return tc_1

#Set up 2nd thermocouple
def setup2():
   tc_2 = spidev.SpiDev()
   tc_2.open(0,1)
   tc_2.max_speed_hz = 5000000
   return tc_2

def read(thmcouple):
    # Assume the input is either 1 or 2, and default to 1 if another value is entered.
    rec = thmcouple.xfer2(READBYTE)

    # Check the fault bit of the returned message
    if rec[1] & 0x01:
        fault = 1
        #print "A fault was encountered by the MAX31855"
    else:
        fault = 0

    # Convert the 16-bit returned number to the 14-bit temp value.
    data = (rec[0] << 6) | (rec[1] >> 2)

    # Check for negatives
    if data >> 13:
        temp = float((int(data) / 4.0) - 2048)
    else:
        temp = float(data / 4.0)

    return temp

def close(thmcouple):
    thmcouple.close()
