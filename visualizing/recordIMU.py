from icm20689 import Icm20689SPI
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import math
import time
import datetime
import os
import csv

class filterData(object):
    def __init__(self):
        self.tlast = time.time()
        self.dt = 0
        self.iter = 0
        self.pitchAcc = [0.01] # non-zero to avoid math error 1/0
        self.pitchGyr = [0.01]
        self.pitch = [0.01]
                        
        self.rollAcc = [0.01]
        self.rollGyr = [0.01]
        self.roll = [0.01]
        
        self.yawAcc = [0.01]
        self.yawGyr = [0.01]
        self.yaw = [0.01]
        
    def update(self):
        data = chip.get_all_data()
        x = data['ax']
        y = data['ay']
        z = data['az']
        gx = data['gx']
        gy = data['gy']
        gz = data['gz']

        t1 = time.time()
        t0 = self.tlast
        self.dt = t1 - t0
        self.tlast = t1
        self.iter+=1
        # ---------INPUT----------
        alpha = 0.5
        # BETTER WAY TO CALC ALPHA
        # alpha = tc /(tc+DT) # where tc is a time constant greater than the timescale of typical accelerometer noise
        # ---------END INPUT------
        
        pitchAcc = math.degrees(math.atan(x/(math.sqrt(y**2+z**2)+.0001)))
        pitchGyr = self.pitch[-1]+gx*self.dt # Note, to avoid drift, using last filtered angle rather than last gyroAngle
        pitch = alpha*pitchGyr + (1-alpha)*pitchAcc

        rollAcc = math.degrees(math.atan(y/(math.sqrt(x**2+z**2)+.0001)))
        rollGyr = self.roll[-1]+gy*self.dt
        roll = alpha*rollGyr + (1-alpha)*rollAcc

        yawAcc = math.degrees(math.atan(math.sqrt(x**2+y**2)/(z+.0001)))
        yawGyr = self.yawGyr[-1]+gz*self.dt
        yaw = alpha*yawGyr + (1-alpha)*yawAcc

        dict0 = {'dt':self.dt}
        dict1 = {'pitch':pitch,'roll':roll,'yaw':yaw}
        dict2 = {'pitchAcc':pitchAcc,'rollAcc':rollAcc,'yawAcc':yawAcc}
        dict3 = {'pitchGyr':pitchGyr,'rollGyr':rollGyr,'yawGyr':yawGyr}
        newdata = {'sample':self.iter}
        for i in [dict0,dict1,dict2,dict3,data[0],data[1],data[2]]:
            newdata.update(i)

        return newdata

chip = Icm20689SPI(1, 0, 0, 25)
os.chdir('/home/pi/icm20689/data')

tstart = time.time()
tlength = 1800
ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
with open(''.join([ts,'data.csv']),'w', newline='') as csvfile:
#with open('xxnames.csv', 'w', newline='') as csvfile:
    myFields = [
        'sample','dt',
        'ax','ay','az',
        'gx','gy','gz',
        'pitch','roll','yaw',
        'pitchAcc','rollAcc','yawAcc',
        'pitchGyr','rollGyr','yawGyr',
        'temp'
        ]
    writer = csv.DictWriter(csvfile, fieldnames=myFields)
    writer.writeheader()
    
    fData = filterData()
    while time.time()-tstart < tlength:
        idata = fData.update() 
        writer.writerow(idata)
        #print(sorted(idata.items()))
        #f.write(idata.items())
        time.sleep(0.05)
        #print(idata['sample'] time.time()-tstart)
        print("{0:.0f}  {1:.2f}".format(idata['sample'], (time.time()-tstart)))
    csvfile.close()
