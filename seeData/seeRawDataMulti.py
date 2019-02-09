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

DT = 1

class Scope(object):
    def __init__(self, axis1, axis2, maxt=50):
        self.axis1 = axis1
        self.axis2 = axis2
        self.tlast = time.time()
        self.maxt = maxt
        self.tdata = [0]
        
        self.ax1 = [0]
        self.ay1 = [0]
        self.az1 = [0]
        self.gx1 = [0]
        self.gy1 = [0]
        self.gz1 = [0]
        self.line1 = Line2D(self.tdata, self.ax1)
        self.line2 = Line2D(self.tdata, self.ay1)
        self.line3 = Line2D(self.tdata, self.az1)
        self.line4 = Line2D(self.tdata, self.gx1)
        self.line5 = Line2D(self.tdata, self.gy1)
        self.line6 = Line2D(self.tdata, self.gz1)
        self.axis1.add_line(self.line1)
        self.axis1.add_line(self.line2)
        self.axis1.add_line(self.line3)
        self.axis1.add_line(self.line4)
        self.axis1.add_line(self.line5)
        self.axis1.add_line(self.line6)
        self.line1.set_color("g")
        self.line2.set_color("b")
        self.line3.set_color("r")
        self.line4.set_color("g")
        self.line5.set_color("b")
        self.line6.set_color("r")
        self.line4.set_linestyle("--")
        self.line5.set_linestyle("--")
        self.line6.set_linestyle("--")
        self.axis1.set_ylim(-200, 200)
        self.axis1.set_xlim(0, self.maxt)
        self.axis1.set_ylabel("Chip 1")
        self.axis1.legend([self.line1, self.line2, self.line3, self.line4, self.line5, self.line6], ['ax','ay','az','gx','gy','gz'])
        
        self.ax2 = [0]
        self.ay2 = [0]
        self.az2 = [0]
        self.gx2 = [0]
        self.gy2 = [0]
        self.gz2 = [0]
        self.line7 = Line2D(self.tdata, self.ax2)
        self.line8 = Line2D(self.tdata, self.ay2)
        self.line9 = Line2D(self.tdata, self.az2)
        self.line10 = Line2D(self.tdata, self.gx2)
        self.line11 = Line2D(self.tdata, self.gy2)
        self.line12 = Line2D(self.tdata, self.gz2)
        self.axis2.add_line(self.line7)
        self.axis2.add_line(self.line8)
        self.axis2.add_line(self.line9)
        self.axis2.add_line(self.line10)
        self.axis2.add_line(self.line11)
        self.axis2.add_line(self.line12)
        self.line7.set_color("g")
        self.line8.set_color("b")
        self.line9.set_color("r")
        self.line10.set_color("g")
        self.line11.set_color("b")
        self.line12.set_color("r")
        self.line10.set_linestyle("--")
        self.line11.set_linestyle("--")
        self.line12.set_linestyle("--")
        self.axis2.set_ylim(-200, 200)
        self.axis2.set_xlim(0, self.maxt)
        self.axis2.set_ylabel("Chip 2")
        self.axis2.legend([self.line7, self.line8, self.line9, self.line10, self.line11, self.line12], ['ax','ay','az','gx','gy','gz'])
        
    def update(self, data):
        ax1 = data[0]['ax']
        ay1 = data[0]['ay']
        az1 = data[0]['az']
        gx1 = data[0]['gx']
        gy1 = data[0]['gy']
        gz1 = data[0]['gz']

        ax2 = data[1]['ax']
        ay2 = data[1]['ay']
        az2 = data[1]['az']
        gx2 = data[1]['gx']
        gy2 = data[1]['gy']
        gz2 = data[1]['gz']
        
        t1 = time.time()
        t0 = self.tlast
        dt = t1 - t0
        self.tlast = t1

        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ax1 = [self.ax1[-1]]
            self.ay1 = [self.ay1[-1]]
            self.az1 = [self.az1[-1]]
            self.gx1 = [self.gx1[-1]]
            self.gy1 = [self.gy1[-1]]
            self.gz1 = [self.gz1[-1]]
            self.ax2 = [self.ax2[-1]]
            self.ay2 = [self.ay2[-1]]
            self.az2 = [self.az2[-1]]
            self.gx2 = [self.gx2[-1]]
            self.gy2 = [self.gy2[-1]]
            self.gz2 = [self.gz2[-1]]
            self.axis1.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.axis1.figure.canvas.draw()
            self.axis1.legend([self.line1, self.line2, self.line3, self.line4, self.line5, self.line6], ['ax','ay','az', 'gx','gy','gz'])
            self.axis2.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.axis2.figure.canvas.draw()
            self.axis2.legend([self.line7, self.line8, self.line9, self.line10, self.line11, self.line12], ['ax','ay','az', 'gx','gy','gz'])

            
        t = self.tdata[-1] + dt
        self.tdata.append(t)
        
        self.ax1.append(ax1)
        self.ay1.append(ay1)
        self.az1.append(az1)
        self.gx1.append(gx1)
        self.gy1.append(gy1)
        self.gz1.append(gz1)

        self.ax2.append(ax2)
        self.ay2.append(ay2)
        self.az2.append(az2)
        self.gx2.append(gx2)
        self.gy2.append(gy2)
        self.gz2.append(gz2)
        
        self.line1.set_data(self.tdata, self.ax1)
        self.line2.set_data(self.tdata, self.ay1)
        self.line3.set_data(self.tdata, self.az1)
        self.line4.set_data(self.tdata, self.gx1)
        self.line5.set_data(self.tdata, self.gy1)
        self.line6.set_data(self.tdata, self.gz1)

        self.line7.set_data(self.tdata, self.ax2)
        self.line8.set_data(self.tdata, self.ay2)
        self.line9.set_data(self.tdata, self.az2)
        self.line10.set_data(self.tdata, self.gx2)
        self.line11.set_data(self.tdata, self.gy2)
        self.line12.set_data(self.tdata, self.gz2)
        
        return self.line1, self.line2, self.line3, self.line4, self.line5, self.line6, self.line7, self.line8, self.line9, self.line10, self.line11, self.line12,

def extractor():
    data1 = chip1.get_all_data()
    data2 = chip2.get_all_data()
    data = [data1, data2]
    yield data

fig = plt.figure()
axis1 = fig.add_subplot(2,1,1)
axis2 = fig.add_subplot(2,1,2)
scope = Scope(axis1,axis2)

# pass a generator in "extractor" to produce data for the update func
ani = animation.FuncAnimation(fig, scope.update, extractor, interval=100,
                              blit=True)
plt.show()
