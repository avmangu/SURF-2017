import serial.tools.list_ports

def portFind():
    ports = list(serial.tools.list_ports.comports())
    print len(ports)

portFind()
