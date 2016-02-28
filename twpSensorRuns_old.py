# -*- coding:utf-8 -*-
#!/usr/bin/python

import smbus
import time
import os
import math
import socket
import sys
import RPi.GPIO as GPIO
import smtplib
import datetime
import uuid
import random
from email.mime.text import MIMEText

GPIO_LEDRED    = 9
GPIO_LEDYELLOW = 10
GPIO_LEDGREEN  = 11
DISTANCE_CAUTION = 30
DISTANCE_COLLISION = 7

# MMA7455 Accelerometer Class
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

# Signed 8 reading conversion for longs
def signed8Val(val):
    if(val > 127):
        val = -1 * (val%127)
    return val

# Run Accelerometer and Send Data
def runMMA7455(MMA7455, sock = None):
    x = signed8Val(MMA7455.getValueX())
    y = signed8Val(MMA7455.getValueY())
    z = signed8Val(MMA7455.getValueZ())
    print 'X= {0}, Y= {1}, Z={2}'.format(x, y, z)
    xA = 0
    yA = 0
    zA = 0
    if (x):
        xA = math.atan(x / (math.sqrt((y**2)+(z**2))))
    if (y):
        yA = math.atan(y / (math.sqrt((x**2)+(z**2))))
    zA = math.atan(math.sqrt((x**2)+(y**2))/z)

    xA = xA * 180
    yA = yA * 180
    zA = zA * 180
    pi = 3.141592
    xA = xA / pi
    yA = yA / pi
    zA = zA / pi
    print 'XA= {0}, YA= {1}, ZA={2}'.format(xA, yA, zA)

    if sock is not None:
        sock.sendall('{3} X= {0}, Y= {1}, Z={2}|'.format(x, y, z, getTimeStamp()))
        sock.sendall('{3} XA= {0}, YA= {1}, ZA={2}|'.format(xA, yA, zA, getTimeStamp()))

    time.sleep(0.5)
    #os.system("clear")

# Run Ultrasonic Sensor and send Data
def runHCSR04(sock = None):
    # Use BCM GPIO references
    # instead of physical pin numbers
    GPIO.setmode(GPIO.BCM)

    # Define GPIO to use on Pi
    GPIO_TRIGGER = 23
    GPIO_ECHO    = 24

    print "Ultrasonic Measurement"

    # Set pins as output and input
    GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
    GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER, False)

    # Allow module to settle
    time.sleep(0.5)

    # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34300

    # That was the distance there and back so halve the value
    distance = distance / 2

    print "Distance : %.1f cms" % distance

    claimNum = ""
    if distance < DISTANCE_COLLISION:
        print "**** COLLISION ALERT! *****"
        setLED(GPIO_LEDRED)
        print "**** Sending Auto-FNOL *****"
        sendEmailAlert()
        claimNum = sendFNOL()
        print "Auto FNOL Generated. Claim #" + claimNum
        print "**** Emergency Dispatch Alerted! *****"
        #time.sleep(2)
    elif distance < DISTANCE_CAUTION:
        print "**** CAUTION!!!! POSSIBLE COLLISION !! *****"
        setLED(GPIO_LEDYELLOW)
    else:
        setLED(GPIO_LEDGREEN)

    # Reset GPIO settings
    #GPIO.cleanup()

    print("==========================================")

    if sock is not None:
        sock.sendall('{0} Ultrasonic Measurement Distance : {1} cms |'.format(getTimeStamp(),distance))
        if distance < DISTANCE_COLLISION:
            sock.sendall('{0} **** COLLISION ALERT! ***** |'.format(getTimeStamp()))
            sock.sendall('{0} **** Auto FNOL Claim # : {1} ***** |'.format(getTimeStamp(), claimNum))
            sock.sendall('{0} **** Emergency Dispatch Alerted! ***** |'.format(getTimeStamp()))
            time.sleep(2)
        elif distance < DISTANCE_CAUTION:
            sock.sendall('{0} **** CAUTION!!!! POSSIBLE COLLISION !! ***** |'.format(getTimeStamp()))
        sock.sendall("------------------------------------- |")

# Send Email using SMTP
def sendEmailAlert():
    msg = MIMEText("Collision Detected on Raspberry Pi!")
    me  = 'emailhere@??.com'
    you = 'emailhere@??.com'
    msg['Subject'] = 'Collision Alert'
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login(me, 'passwordhere')
    s.sendmail(me, [you], msg.as_string())
    s.quit()

def setLED(pinNumber):
    #GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
    #19-10 Yellow, 21-09 Red, 23-11 Green
    GPIO.setup(GPIO_LEDRED, GPIO.OUT) ## Setup GPIO Pin to OUT
    GPIO.output(GPIO_LEDRED, False)
    GPIO.setup(GPIO_LEDYELLOW, GPIO.OUT) ## Setup GPIO Pin to OUT
    GPIO.output(GPIO_LEDYELLOW, False)
    GPIO.setup(GPIO_LEDGREEN, GPIO.OUT) ## Setup GPIO Pin to OUT
    GPIO.output(GPIO_LEDGREEN, False)
    GPIO.setup(pinNumber, GPIO.OUT) ## Setup GPIO Pin to OUT
    GPIO.output(pinNumber, True) ## Turn on GPIO pin
#GPIO.cleanup()


def getTimeStamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]')


def prepFNOL():
    claimNum = claimNum = '{0:05}-01'.format(random.randint(1, 100000))
    fout = open(FILE_NAME_OP, 'w+')
    with open(FILE_NAME_INP, 'r') as fin:
        for line in fin:
            #print line
            if line.strip().startswith("<RqUID>"):
                newLine = "<RqUID>" + str(uuid.uuid1()) + "</RqUID>\n"
                fout.write(newLine)
                print "replaced rquid" + newLine
            elif line.strip().startswith("<ClaimNum>"):
                newLine = "<ClaimNum>" + claimNum + "</ClaimNum>\n"
                fout.write(newLine)
                print "replaced claimnum" + newLine
            else:
                fout.write(line)
    fout.close()
    return claimNum

FILE_NAME_INP = "claimSaveRq.xml"
FILE_NAME_OP  = "claimSaveRq21.xml"

def sendFNOL():
    claimNum =  prepFNOL()
    os.system("java ClaimSaveRunner")
    return claimNum

def main():
    if (len(sys.argv) > 1):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port on the server given by the caller
        server_address = (sys.argv[1], 10000)
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        sock.connect(server_address)
    else:
        sock = None
    GPIO.cleanup()
    MMA7455 = Accel()
    MMA7455.setUp()
    while (1):
        runMMA7455(MMA7455, sock)
        runHCSR04(sock)

if __name__ == "__main__":
    main()