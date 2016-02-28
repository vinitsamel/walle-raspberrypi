# -*- coding:utf-8 -*-
#!/usr/bin/python

import smbus
import time
import os
import RPi.GPIO as GPIO
import math

# Define a class called Accel
class Accel():
	myBus=1
	if GPIO.RPI_REVISION == 1:
		myBus=0
	elif GPIO.RPI_REVISION == 2:
		myBus=1
	b = smbus.SMBus(myBus)
	def setUp(self):
		self.b.write_byte_data(0x1D,0x16,0x55) # Setup the Mode
		self.b.write_byte_data(0x1D,0x10,0) # Calibrate
		self.b.write_byte_data(0x1D,0x11,0) # Calibrate
		self.b.write_byte_data(0x1D,0x12,0) # Calibrate
		self.b.write_byte_data(0x1D,0x13,0) # Calibrate
		self.b.write_byte_data(0x1D,0x14,0) # Calibrate
		self.b.write_byte_data(0x1D,0x15,0) # Calibrate
	def getValueX(self):
		return self.b.read_byte_data(0x1D,0x06)
	def getValueY(self):
		return self.b.read_byte_data(0x1D,0x07)
	def getValueZ(self):
		return self.b.read_byte_data(0x1D,0x08)

MMA7455 = Accel()
MMA7455.setUp()

def signed8Val(val):
	if(val > 127):
		val = -1 * (val%127)
	return val

for a in range(10000):
	x = signed8Val(MMA7455.getValueX())
	y = signed8Val(MMA7455.getValueY())
	z = signed8Val(MMA7455.getValueZ())
	print("X=", x)
	print("Y=", y)
	print("Z=", z)
	xA = math.atan(x / (math.sqrt((y**2)+(z**2))))
	yA = math.atan(y / (math.sqrt((x**2)+(z**2))))
	zA = math.atan(math.sqrt((x**2)+(y**2))/z)
	
	xA = xA * 180
	yA = yA * 180
	zA = zA * 180
	
	pi = 3.141592
	xA = xA / pi
	yA = yA / pi
	zA = zA / pi
	print("XA=", xA)
	print("YA=", yA)
	print("ZA=", zA)
	
	print("==========================================")
	time.sleep(0.5)
	#os.system("clear")