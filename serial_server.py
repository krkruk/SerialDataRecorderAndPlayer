import serial
from serial.tools import list_ports

l = list_ports.comports()
print(l[0].name)