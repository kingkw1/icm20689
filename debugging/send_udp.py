#!/usr/bin/python

import socket
import struct
import icm20689
import time


UDP_IP = '192.168.0.1'
UDP_PORT = 1025

mpu = icm20689.Icm20689SPI(1, 0, 0, 25)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

while True:
	gyro_data = mpu.get_gyro_data()
	accel_data = mpu.get_accel_data()
	MESSAGE = struct.pack('!dddddd', gyro_data['x'], gyro_data['y'], gyro_data['z'], accel_data['x'], accel_data['y'], accel_data['z'])
	
	sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
	print("Message sent")
	time.sleep(.01)
