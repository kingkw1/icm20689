from icm20689 import Icm20689SPI
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import math
import time

seeChip = 1

chip1 = Icm20689SPI(1, 0, 0, 25)
chip2 = Icm20689SPI(1, 0, 0, 24)
style.use('fivethirtyeight')

DT = 1

class Scope(object):
    def __init__(self, ax1, ax2, maxt=30):
        self.ax1 = ax1
        self.ax2 = ax2
        self.tlast = time.time()
        self.maxt = maxt
        self.tdata = [0]
        self.ax = [0]
        self.ay = [0]
        self.az = [0]
        self.gx = [0]
        self.gy = [0]
        self.gz = [0]
        self.line1 = Line2D(self.tdata, self.ax)
        self.line2 = Line2D(self.tdata, self.ay)
        self.line3 = Line2D(self.tdata, self.az)
        self.line4 = Line2D(self.tdata, self.gx)
        self.line5 = Line2D(self.tdata, self.gy)
        self.line6 = Line2D(self.tdata, self.gz)
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line2)
        self.ax1.add_line(self.line3)
        self.ax2.add_line(self.line4)
        self.ax2.add_line(self.line5)
        self.ax2.add_line(self.line6)
        self.line1.set_color("g")
        self.line2.set_color("b")
        self.line3.set_color("r")
        self.line4.set_color("g")
        self.line5.set_color("b")
        self.line6.set_color("r")
        self.line4.set_linestyle("--")
        self.line5.set_linestyle("--")
        self.line6.set_linestyle("--")
        self.ax1.set_ylim(-20, 20)
        self.ax1.set_xlim(0, self.maxt)
        self.ax1.legend([self.line1, self.line2, self.line3], ['ax','ay','az'])
        
        self.ax2.set_ylim(-300, 300)
        self.ax2.set_xlim(0, self.maxt)
        self.ax2.legend([self.line4, self.line5, self.line6], ['gx','gy','gz'])
        
    def update(self, data):
        ax = data['ax']
        ay = data['ay']
        az = data['az']
        gx = data['gx']
        gy = data['gy']
        gz = data['gz']

        t1 = time.time()
        t0 = self.tlast
        dt = t1 - t0
        self.tlast = t1

        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ax = [self.ax[-1]]
            self.ay = [self.ay[-1]]
            self.az = [self.az[-1]]
            self.gx = [self.gx[-1]]
            self.gy = [self.gy[-1]]
            self.gz = [self.gz[-1]]
            self.ax1.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax1.figure.canvas.draw()
            self.ax1.legend([self.line1, self.line2, self.line3], ['ax','ay','az'])
            self.ax2.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax2.figure.canvas.draw()
            self.ax2.legend([self.line4, self.line5, self.line6], ['gx','gy','gz'])
            
        t = self.tdata[-1] + dt
        self.tdata.append(t)
        
        self.ax.append(ax)
        self.ay.append(ay)
        self.az.append(az)
        self.gx.append(gx)
        self.gy.append(gy)
        self.gz.append(gz)

        #print('{l1} {l2}'.format(l1 = len(self.tdata),l2 = len(self.ax)))
        #print('{l1} {l2}'.format(l1 = self.tdata,l2 = self.ax))
        
        self.line1.set_data(self.tdata, self.ax)
        self.line2.set_data(self.tdata, self.ay)
        self.line3.set_data(self.tdata, self.az)
        self.line4.set_data(self.tdata, self.gx)
        self.line5.set_data(self.tdata, self.gy)
        self.line6.set_data(self.tdata, self.gz)
        
        return self.line1, self.line2, self.line3, self.line4, self.line5, self.line6,

def extractor():
    data1 = chip1.get_all_data()
    data2 = chip2.get_all_data()
    if seeChip == 1:
        data = data1
    elif seeChip == 2:
        data = data2
    yield data

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
scope = Scope(ax1,ax2)

# pass a generator in "extractor" to produce data for the update func
ani = animation.FuncAnimation(fig, scope.update, extractor, interval=100,
                              blit=True)
plt.show()
