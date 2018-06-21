import sys
import serial

portName = '/dev/ttyACM0'
relayNum = 0
	
serPort = serial.Serial(portName, 19200, timeout=1)
serPort.write("relay on " + str(relayNum) + "\n\r")
serPort.close()
