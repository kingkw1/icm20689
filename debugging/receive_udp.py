#!/usr/bin/python

import socket
#import struct
import icm20689
import time


UDP_IP = '192.168.0.1'
host = ''
UDP_PORT = 1025
bufsize = 1024;
#mpu = icm20689.Icm20689SPI(1, 0, 0, 25)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP,UDP_PORT))

while True:
	data, addr = sock.recv(bufsize)
	print("Message received")
	time.sleep(.01)
