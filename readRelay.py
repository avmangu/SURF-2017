import sys
import serial

portName = '/dev/ttyACM0'
relayNum = 0
	
serPort = serial.Serial(portName, 19200, timeout=1)
serPort.write("relay read "+ str(relayNum) + "\n\r")

response = serPort.read(25)

if(response.find("on") > 0):
	print "Relay " + str(relayNum) +" is ON"
	
elif(response.find("off") > 0):
	print "Relay " + str(relayNum) +" is OFF"
	
serPort.close()
