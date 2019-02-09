from icm20689 import Icm20689SPI
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import math
import time

chip1 = Icm20689SPI(1, 0, 0, 25)
chip2 = Icm20689SPI(1, 0, 0, 24)
style.use('fivethirtyeight')

DT = 0.5

class Scope(object):
    def __init__(self, ax1, ax2, maxt=DT*100, dt=DT):
        self.ax1 = ax1
        self.ax2 = ax2
        self.tlast = time.time()
        #self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.pitch1 = [0]
        self.roll1 = [0]
        self.pitch2 = [0]
        self.roll2 = [0]
        self.line1 = Line2D(self.tdata, self.pitch1)
        self.line2 = Line2D(self.tdata, self.roll1)
        self.line3 = Line2D(self.tdata, self.pitch2)
        self.line4 = Line2D(self.tdata, self.roll2)
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line2)
        self.ax2.add_line(self.line3)
        self.ax2.add_line(self.line4)
        self.line1.set_color("r")
        self.line2.set_color("b")
        self.line3.set_color("r")
        self.line4.set_color("b")
        self.line1.set_linestyle("-")
        self.line2.set_linestyle("-")
        self.line3.set_linestyle("-")
        self.line4.set_linestyle("-")
        self.ax1.set_ylim(-200, 200)
        self.ax1.set_xlim(0, self.maxt)
        self.ax2.set_ylim(-200, 200)
        self.ax2.set_xlim(0, self.maxt)

    def update(self, data):
        x1 = data[0]['ax']
        y1 = data[0]['ay']
        z1 = data[0]['az']
        gx1 = data[0]['gx']
        gy1 = data[0]['gy']
        gz1 = data[0]['gz']

        t1 = time.time()
        t0 = self.tlast
        dt = t1 - t0
        self.tlast = t1
        
        # ---------INPUT----------
        alpha1 = 0.5
        alpha2 = 0.5
        # BETTER WAY TO CALC ALPHA
        # alpha = tc /(tc+DT) # where tc is a time constant greater than the timescale of typical accelerometer noise
        # ---------END INPUT------
        
        pitchAcc1 = math.degrees(math.atan2(y1,z1))
        rollAcc1 = math.degrees(math.atan2(x1,z1))
        pitchGyr1 = self.pitch1[-1]+gx1*dt
        rollGyr1 = self.roll1[-1]+gx1*dt
        pitch1 = alpha1*pitchGyr1 + (1-alpha1)*pitchAcc1
        roll1 = alpha1*rollGyr1 + (1-alpha1)*rollAcc1
        
        x2 = data[1]['ax']
        y2 = data[1]['ay']
        z2 = data[1]['az']
        gx2 = data[1]['gx']
        gy2 = data[1]['gy']
        gz2 = data[1]['gz']

        pitchAcc2 = math.degrees(math.atan2(y2,z2))
        rollAcc2 = math.degrees(math.atan2(x2,z2))
        pitchGyr2 = self.pitch2[-1]+gx2*dt
        rollGyr2 = self.roll2[-1]+gx2*dt
        pitch2 = alpha2*pitchGyr2 + (1-alpha2)*pitchAcc2
        roll2 = alpha2*rollGyr2 + (1-alpha2)*rollAcc2
        
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            
            self.pitch1 = [self.pitch1[-1]]
            self.roll1 = [self.roll1[-1]]
            self.pitch2 = [self.pitch2[-1]]
            self.roll2 = [self.roll2[-1]]

            self.ax1.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax1.figure.canvas.draw()
            self.ax2.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax2.figure.canvas.draw()

        t = self.tdata[-1] + dt
        self.tdata.append(t)
        
        self.pitch1.append(pitch1)
        self.roll1.append(roll1)
        self.pitch2.append(pitch2)
        self.roll2.append(roll2)

        self.line1.set_data(self.tdata, self.pitch1)
        self.line2.set_data(self.tdata, self.roll1) 
        self.line3.set_data(self.tdata, self.pitch2)
        self.line4.set_data(self.tdata, self.roll2)
        return self.line1, self.line2, self.line3, self.line4, 

def extractor():
    data1 = chip1.get_all_data()
    data2 = chip2.get_all_data()
    data = [data1, data2]
    yield data

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
scope = Scope(ax1, ax2)

# pass a generator in "extractor" to produce data for the update func
ani = animation.FuncAnimation(fig, scope.update, extractor, interval=100,
                              blit=True)
plt.show()
