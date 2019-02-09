# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 14:49:15 2018

@author: kingk
"""
import socket
import time

SERVER_IP = '192.168.0.200'
PORT = 50000

loop = 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))

mssg = 'Hello server'
print('sending message:    ', mssg)
s.sendto(mssg.encode('utf-8'), (SERVER_IP, PORT)) #s.sendall(mssg.encode('utf-8'))
data = s.recv(1024)
print('received message:  ', repr(data.decode('utf-8')))

if loop:
    icount = 0
    #data = s.recv(1024)
    #print('received message:  ', repr(data.decode('utf-8')))
    while icount < 10:
        icount +=1 
        mssg = 'something # %s' %icount
        print('sending message:    ', mssg)
        s.sendall(mssg.encode('utf-8'))
        time.sleep(0.5)
        
s.close()
