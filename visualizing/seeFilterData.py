from icm20689 import Icm20689SPI
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import math
import time

chip = Icm20689SPI(1, 0, 0, 25)
style.use('fivethirtyeight')

DT = 1

class Scope(object):
    def __init__(self, ax1, maxt=10):
        self.ax1 = ax1
        self.tlast = time.time()
        self.maxt = maxt
        self.tdata = [0]
        self.pitchAcc = [0.01] # non-zero to avoid math error 1/0
        self.pitchGyr = [0.01]
        self.pitch = [0.01]
        self.line1 = Line2D(self.tdata, self.pitchAcc)
        self.line2 = Line2D(self.tdata, self.pitchGyr)
        self.line3 = Line2D(self.tdata, self.pitch)
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line2)
        self.ax1.add_line(self.line3)
        self.line1.set_color("g")
        self.line2.set_color("b")
        self.line3.set_color("r")
        self.ax1.set_ylim(-200, 200)
        self.ax1.set_xlim(0, self.maxt)
        self.ax1.legend([self.line1, self.line2, self.line3], ['Acc','Gyr','Filt'])
        
    def update(self, data):
        #TODO: Incorporate other IMU axes
        #TODO: Incorporate multiple figures for multiple IMU's
        x = data['ax']
        y = data['ay']
        z = data['az']
        gx = data['gx']
        gy = data['gy']
        gz = data['gz']

        t1 = time.time()
        t0 = self.tlast
        dt = t1 - t0
        self.tlast = t1
        
        # ---------INPUT----------
        alpha = 0.5
        # BETTER WAY TO CALC ALPHA
        # alpha = tc /(tc+DT) # where tc is a time constant greater than the timescale of typical accelerometer noise
        # ---------END INPUT------
        
        pitchAcc = math.degrees(math.atan(x/math.sqrt(y**2+z**2+0.0001)))
        pitchGyr = self.pitch[-1]+gx*dt # Note, to avoid drift, using last filtered angle rather than last gyroAngle
        pitch = alpha*pitchGyr + (1-alpha)*pitchAcc

        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.pitchAcc = [self.pitchAcc[-1]]
            self.pitchGyr = [self.pitchGyr[-1]]
            self.pitch = [self.pitch[-1]]
            self.ax1.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax1.figure.canvas.draw()
            self.ax1.legend([self.line1, self.line2, self.line3], ['Acc','Gyr','Filt'])
            
        t = self.tdata[-1] + dt
        self.tdata.append(t)
        
        self.pitchAcc.append(pitchAcc)
        self.pitchGyr.append(pitchGyr)        
        self.pitch.append(pitch)

        self.line1.set_data(self.tdata, self.pitchAcc) 
        self.line2.set_data(self.tdata, self.pitchGyr)
        self.line3.set_data(self.tdata, self.pitch)

        #print([pitchAcc, pitchGyr, pitch, dt])
        return self.line1, self.line2, self.line3, 

def extractor():
    data = chip.get_all_data()
    yield data

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
scope = Scope(ax1)

# pass a generator in "extractor" to produce data for the update func
ani = animation.FuncAnimation(fig, scope.update, extractor, interval=100,
                              blit=True)
plt.show()
