import smbus
import spidev
import RPi.GPIO as GPIO
from enum import Enum
from abc import ABC, abstractmethod

from icm20689_regs import *
import time
import socket
import struct
import math
import threading
from queue import Empty, Queue
import signal

class Icm20689Data(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def serialize(self):
        pass

class AccelerometerData(Icm20689Data):
    def __init__(self, x_val, y_val, z_val):
        self.x_val = x_val
        self.y_val = y_val
        self.z_val = z_val

    def serialize(self):
        return struct.pack('!ddd', self.x_val, self.y_val, self.z_val)

    def __repr__(self):
        return "%lf %lf %lf" % (self.x_val, self.y_val, self.z_val)

class GyroData(Icm20689Data):
    def __init__(self, x_val, y_val, z_val):
        self.x_val = x_val
        self.y_val = y_val
        self.z_val = z_val

    def serialize(self):
        return struct.pack('!ddd', self.x_val, self.y_val, self.z_val)

    def __repr__(self):
        return "%lf %lf %lf" % (self.x_val, self.y_val, self.z_val)

class MpuDataPoint(Icm20689Data):

    def __init__(self, mpu_id, accel_data, gyro_data):
        self._mpu_id = mpu_id
        self._gyro_data = gyro_data
        self._accel_data = accel_data

    def serialize(self):
        serialized_data = bytearray()
        serialized_data += struct.pack('!i', self._mpu_id) + self._accel_data.serialize() + self._gyro_data.serialize()
        return serialized_data

    def __repr__(self):
        return "id: %d\nGyro: %s\nAccell: %s\n\n" %(self._mpu_id, str(self._gyro_data), str(self._accel_data))

class MpuDataPacket(Icm20689Data):

    def __init__(self, data):
        self._data = data

    def serialize(self):
        serialized_data = bytearray()
        for point in self._data:
            serialized_data += point.serialize()

        return struct.pack('!i', len(self._data)) + serialized_data

class Icm20689(ABC):

    # Global Variables
    GRAVITIY_MS2 = 9.80665
    #M_PI = math.pi
    #ACCELEROMETER_SENSITIVITY = 16384 # From the specs p10. 250 mode. also self._accel_range_cached.get_lsb_sensitivity()
    #GYROSCOPE_SENSITIVITY = 131 # From the specs p9. 2g mode
    #dt = 0.01
    
    def __init__(self, mpu_id):
        self._mpu_id = mpu_id
        self._gyro_range_cached = FS_SEL.FS_DEG_250 
        self._accel_range_cached = AFS_SEL.FS_2G 
        self._sample_frequency_cached = 1000 # Empirically closer to 1024

    # hardware communication methods
    @abstractmethod
    def read_byte_data(self, register):
        pass

    @abstractmethod
    def write_byte_data(self, register, value):
        pass

    def read_word_data(self, register_high, register_low):
        """Read two i2c registers and combine them.

        register -- the first register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        high = self.read_byte_data(register_high)
        low = self.read_byte_data(register_low)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # ICM-20689 Methods

    def get_temp(self):
        """Reads the temperature from the onboard temperature sensor of the ICM-20689.

        Returns the temperature in degrees Celcius.
        """
        raw_temp = self.read_word_data(ICM20689Regs.TEMP_OUT_H, ICM20689Regs.TEMP_OUT_L)

        # Get the actual temperature using the formule given in the
        # ICM-20689 Register Map and Descriptions revision 4.2, page 30
        actual_temp = (raw_temp / 340.0) + 36.53

        return {'temp': actual_temp}

    def set_accel_range(self, accel_range):
        """Sets the range of the accelerometer to range.

        accel_range -- the range to set the accelerometer to. Using a
        pre-defined range is advised. Input integers corresponding to conversion
        of binary values in table of datasheet [0,1,2,3]
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.write_byte_data(ICM20689Regs.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        hex_mssg = int(bin(accel_range)[2:]+'000',2)
        self.write_byte_data(ICM20689Regs.ACCEL_CONFIG, hex_mssg)

        self._accel_range_cached = AFS_SEL(accel_range)

    def read_accel_range(self, raw = False):
        """Reads the range the accelerometer is set to.

        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        raw_data = self.read_byte_data(ICM20689Regs.ACCEL_CONFIG)
        self._accel_range_cached = AFS_SEL((raw_data >> 3) & 0x3)
        if raw:
            return raw_data
        else:
            return self._accel_range_cached

    def set_sample_frequency(self, samp_freq):
        """Sets the sample freqency of the imu.

        samp_freq -- the sample frequency to set the IMU to. Using a
        pre-defined range is advised.
        """

        internal_sample_freq = 1000
        smplrt_div = int( (internal_sample_freq/samp_freq)-1)

        # First change it to 0x00 to make sure we write the correct value later
        self.write_byte_data(ICM20689Regs.SMPLRT_DIV, 0x00)

        # Write the new range to the SMPLRT_DIV register
        self.write_byte_data(ICM20689Regs.SMPLRT_DIV, smplrt_div)

        self._sample_frequency_cached = samp_freq

    def read_sample_frequency(self, raw = False):
        """Reads the sample frequency the IMU is set to.

        TODO: IMPLEMENT THIS STUFF in the comment
        If raw is True, it will return the raw value from the SMPLRT_DIV
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
 set_gyro_range(self, gyro_range)        """

        smplrt_div = self.read_byte_data(ICM20689Regs.SMPLRT_DIV)
        
        internal_sample_freq = 1000
        sample_rate = internal_sample_freq/(smplrt_div+1)

        return sample_rate

    def get_accel_data(self, g = False):
        """Gets and returns the X, Y and Z values from the accelerometer.

        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        x = self.read_word_data(ICM20689Regs.ACCEL_XOUT_H, ICM20689Regs.ACCEL_XOUT_L)
        y = self.read_word_data(ICM20689Regs.ACCEL_YOUT_H, ICM20689Regs.ACCEL_YOUT_L)
        z = self.read_word_data(ICM20689Regs.ACCEL_ZOUT_H, ICM20689Regs.ACCEL_ZOUT_L)

        accel_scale_modifier = self._accel_range_cached.get_lsb_sensitivity()

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g:
            return {'ax': x, 'ay': y, 'az': z}
        else:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'ax': x, 'ay': y, 'az': z}

    def set_gyro_range(self, gyro_range):
        """Sets the range of the gyroscope to range.

        gyro_range -- the range to set the gyroscope to. Using a pre-defined
        range is advised. Input integers corresponding to conversion of binary
        values in table of datasheet [0,1,2,3]
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.write_byte_data(ICM20689Regs.GYRO_CONFIG, 0x00)

        # Write the new range to the GYRO_CONFIG register
        hex_mssg = int(bin(gyro_range)[2:]+'000',2)
        self.write_byte_data(ICM20689Regs.GYRO_CONFIG, hex_mssg)

        # Change the cached range
        self._gyro_range_cached = FS_SEL(gyro_range)

    def read_gyro_range(self, raw = False):
        """Reads the range the gyroscope is set to.

        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        """
        raw_data = self.read_byte_data(ICM20689Regs.GYRO_CONFIG)

        # self._gyro_range_cached =FS_SEL((raw_data >> 3) & 0x3)
        if raw:
            return raw_data
        else:
            return self._gyro_range_cached

    def get_gyro_data(self):
        """Gets and returns the X, Y and Z values from the gyroscope.

        Returns the read values in a dictionary.
        """
        x = self.read_word_data(ICM20689Regs.GYRO_XOUT_H, ICM20689Regs.GYRO_XOUT_L)
        y = self.read_word_data(ICM20689Regs.GYRO_YOUT_H, ICM20689Regs.GYRO_YOUT_L)
        z = self.read_word_data(ICM20689Regs.GYRO_ZOUT_H, ICM20689Regs.GYRO_ZOUT_L)

        gyro_scale_modifier = self._gyro_range_cached.get_lsb_sensitivity()

        x = x / gyro_scale_modifier
        y = y / gyro_scale_modifier
        z = z / gyro_scale_modifier

        return {'gx': x, 'gy': y, 'gz': z}
       
    def get_all_data(self):
        """Reads and returns all the available data."""
        temp = self.get_temp()
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()

        d1 = accel
        d1.update(gyro)
        d1.update(temp)
        return d1
        #return [accel, gyro, temp]

    def get_fifo_count(self):
        return int(self.read_word_data(ICM20689Regs.FIFO_COUNTH, ICM20689Regs.FIFO_COUNTL) / 2)

    def set_fifo_enable(self, ):
        self.write_byte_data(ICM20689Regs.FIFO_EN, FIFO_EN.ACCEL_FIFO_EN.value | FIFO_EN.XG_FIFO_EN.value | FIFO_EN.YG_FIFO_EN.value | FIFO_EN.ZG_FIFO_EN.value)

    def enable_fifo(self):
        current = self.read_byte_data(ICM20689Regs.USER_CTRL)

        # Reset the FIFO buffer
        self.write_byte_data(ICM20689Regs.USER_CTRL, current | 1<<2)

        self.write_byte_data(ICM20689Regs.USER_CTRL, current | 1<<6)

    def read_fifo_data(self):
        data = []
        count = self.get_fifo_count()
        if count > 128:
            print ("Fifo count %d" % count)
        gyro_scale_modifier = self._gyro_range_cached.get_lsb_sensitivity()
        accel_scale_modifier = self._accel_range_cached.get_lsb_sensitivity() / self.GRAVITIY_MS2
        for i in range(0, math.floor(count/6) - 1):
            x = self.read_word_data(ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_R_W)/accel_scale_modifier
            y = self.read_word_data(ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_R_W)/accel_scale_modifier
            z = self.read_word_data(ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_R_W)/accel_scale_modifier
            g_x = self.read_word_data(ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_R_W)/gyro_scale_modifier 
            g_y = self.read_word_data(ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_R_W)/gyro_scale_modifier
            g_z = self.read_word_data(ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_R_W)/gyro_scale_modifier
            
            data.append(MpuDataPoint(self._mpu_id, AccelerometerData(x, y, z), GyroData(g_x, g_y, g_z)))
            #print (x, y, z)
            #print( g_x, g_y, g_z)
        return data

class Icm20689I2C(Icm20689):

    def __init__(self, mpu_id, bus, chip_select):
        super(Icm20689I2C, self).__init__(mpu_id)
        self._bus = smbus.SMBus(bus)
        self._address = 0x69
        self._chip_select = chip_select

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._chip_select, GPIO.OUT)

        # Wake up the ICM-20689 since it starts in sleep mode
        self.write_byte_data(ICM20689Regs.PWR_MGMT_1, 0x00)

    # I2C communication methods
    def read_byte_data(self, register):
        GPIO.output(self._chip_select, 1)
        ret_val = self._bus.read_byte_data(self._address, register.value)
        GPIO.output(self._chip_select, 0)
        return ret_val

    def write_byte_data(self, register, value):
        GPIO.output(self._chip_select, 1)
        self._bus.write_byte_data(self._address, register.value, value)
        GPIO.output(self._chip_select, 0)


class Icm20689SPI(Icm20689):

    #FIFO_MAX = 1024
    FIFO_MAX = 4096

    def __init__(self, mpu_id, bus, device, chip_select):
        super(Icm20689SPI, self).__init__(mpu_id)
        self._bus =  spidev.SpiDev()
        self._bus.open(bus, device)
        self._bus.max_speed_hz = 2000000
        self._bus.mode = 0b11
        self._chip_select = chip_select

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._chip_select, GPIO.OUT)
        GPIO.output(self._chip_select, 1)
        # Wake up the ICM-20689 since it starts in sleep mode
        self.write_byte_data(ICM20689Regs.PWR_MGMT_1, 0x00)

        self.write_byte_data(ICM20689Regs.USER_CTRL, 1<<4)

    # SPI communication methods
    def read_byte_data(self, register):
        if register in [ICM20689Regs.FIFO_R_W, ICM20689Regs.FIFO_COUNTH, ICM20689Regs.FIFO_COUNTL]:
            self._bus.max_speed_hz = 2000000
        else:
            self._bus.max_speed_hz = 2000000

        GPIO.output(self._chip_select, 0)
        response = self._bus.xfer([ register.value | 0x80, 0x00 ])
        # Perform SPI read
        GPIO.output(self._chip_select, 1)
        return response[1]

    def write_byte_data(self, register, value):
        self._bus.max_speed_hz = 2000000
        GPIO.output(self._chip_select, 0)
        # Perform SPI Write
        self._bus.xfer( [ register.value,  value ])

        GPIO.output(self._chip_select, 1)

    def _bulk_transfer(self, register, size):
        xfer_data = [ 0 ] * (size + 1)
        xfer_data[0] = register.value | 0x80

        GPIO.output(self._chip_select, 0)
        response = self._bus.xfer(xfer_data)
        GPIO.output(self._chip_select, 1)

        return response[1:]

    def _transform_raw_data(self, raw_data):
        data_points = []

        for i in range(0, len(raw_data), 2):
            value = (raw_data[i] << 8) + raw_data[i+1]

            if (value >= 0x8000):
                data_points.append(-((65535 - value) + 1))
            else:
                data_points.append(value)
        return data_points

    def _get_fifo_data(self, count):
        raw_data = self._bulk_transfer(ICM20689Regs.FIFO_R_W, count * 2)

        return self._transform_raw_data(raw_data)

    def read_fifo_data(self):
        data = []
        count = self.get_fifo_count()

        count = min(count, Icm20689SPI.FIFO_MAX)

        if count > 128:
            print ("Fifo count %d" % count)

        if count == 0:
            return data

        data_points = self._get_fifo_data(math.floor(count/6) * 6)
        
        # print(self._gyro_range_cached)
        gyro_scale_modifier = self._gyro_range_cached.get_lsb_sensitivity()
        accel_scale_modifier = self._accel_range_cached.get_lsb_sensitivity() / self.GRAVITIY_MS2

        for i in range(0, len(data_points), 6):
            g_x = data_points[i+3]/gyro_scale_modifier
            g_y = data_points[i+4]/gyro_scale_modifier
            g_z = data_points[i+5]/gyro_scale_modifier
            x = data_points[i+0]/accel_scale_modifier
            y = data_points[i+1]/accel_scale_modifier
            z = data_points[i+2]/accel_scale_modifier
            
            data.append(MpuDataPoint(self._mpu_id, AccelerometerData(x, y, z), GyroData(g_x, g_y, g_z)))
            #print('gyro data: ', g_x,g_y,g_z)
            #print('accelo data: ', x,y,z)
        return data

class InterruptableThread(threading.Thread):
    def __init__(self):
        super(InterruptableThread, self).__init__(daemon=True)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class UdpNetworkSenderThread(InterruptableThread):
    def __init__(self, queue, ip_addr='192.168.0.200', port = 1025):
        super(UdpNetworkSenderThread, self).__init__()
        self._data_queue = queue
        self._ip_addr = ip_addr
        self._port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self.stopped():
            try:
                data = self._data_queue.get(timeout=1)
                try:
                    time.sleep(.100)
                    while not self._data_queue.empty():
                        data.extend(self._data_queue.get(block=False))
                except Empty:
                    pass
                print ("Sending data with %d points" % len(data))
                #print("X: %d   Y: %d   Z: %d" % (data.g_x, data.g_y, data.g_z, ))
                packet = MpuDataPacket(data)
                sock.sendto(packet.serialize(), (self._ip_addr, self._port))
            except Empty:
                pass

class TcpNetworkSenderThread(InterruptableThread):
    # NOTE: This is functional but currently clunky. 
    def __init__(self, queue, ip_addr='192.168.0.200', port = 1025):
        super(TcpNetworkSenderThread, self).__init__()
        self._data_queue = queue
        self._ip_addr = ip_addr
        self._port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._ip_addr, self._port))
        while not self.stopped():
            try:
                data = self._data_queue.get(timeout=1)
                try:
                    time.sleep(.100)
                    while not self._data_queue.empty():
                        data.extend(self._data_queue.get(block=False))
                except Empty:
                    pass
                print ("Sending data with %d points" % len(data))
                #print("X: %d   Y: %d   Z: %d" % (data.g_x, data.g_y, data.g_z, ))
                packet = MpuDataPacket(data)
                sock.sendto(packet.serialize(), (self._ip_addr, self._port))
            except Empty:
                pass

class DataCollectionThread(InterruptableThread):

    def __init__(self, queue, chips, wait_sleep=.005):
        super(DataCollectionThread, self).__init__()
        self._queue = queue
        self._chips = chips
        self._wait_sleep = wait_sleep

    def run(self):
        for chip in self._chips:
            chip.enable_fifo()

        while not self.stopped():
            for chip in self._chips:
                data = chip.read_fifo_data()
                self._queue.put(data)
            time.sleep(self._wait_sleep)
            #print(data)

class Write2FileThread(InterruptableThread):
    def __init__(self, queue, sampNum = 0):
        super(Write2FileThread, self).__init__()
        self._data_queue = queue
        self._sampNum = sampNum

    def run(self):
        f = open("temp.txt","w+")
        start = time.time()
        #f.write("%.2d start datenum\r" % (start))
        while time.time() - start < 3600:
            try:
                data = self._data_queue.get(timeout=1)
                retTime = time.time()-start
                try:
                    time.sleep(.100)
                    while not self._data_queue.empty():
                        data.extend(self._data_queue.get(block=False))
                except Empty:
                    pass
                print ("%d   Writing data with %d points" % (self._sampNum, len(data)))
                for x in range(0, len(data)):
                    self._sampNum += 1
                    f.write("%d %0.4f %d %d %d %d %d %d \r" % (self._sampNum, retTime, data[x]._accel_data.x_val, data[x]._accel_data.y_val, data[x]._accel_data.z_val, data[x]._gyro_data.x_val, data[x]._gyro_data.y_val, data[x]._gyro_data.z_val))
            except Empty:
                pass
        f.write("%d recorded in %0.4f seconds\r" % (self._sampNum, time.time()-start))
        f.close()

THREAD_SET = []

def quit_handler(signal, frame):
    print ('Stopping Threads')
    for thread in THREAD_SET:
        thread.stop()


if __name__ == "__main__":
    i2c_chips = False
    tcp_send = False
    w2f = False 
    
    GPIO.setwarnings(False)
    signal.signal(signal.SIGINT, quit_handler)

    # Initialize each chip
    chips = []
    GPIOS = [22, 23, 24, 25] # GPIOS = [22, 23, 24, 25, 27]
    for i, gpio in enumerate(GPIOS):
        if  i2c_chips:
            chip = Icm20689I2C(i+1, 1, gpio)
        else:
            chip = Icm20689SPI(i+1, 0, 0, gpio)
        chip.set_fifo_enable()
        chip.write_byte_data(ICM20689Regs.CONFIG, 1)
        #chip.write_byte_data(ICM20689Regs.SMPLRT_DIV, 0x00) # sample rate set to internal fs (1khz)
        chip.set_sample_frequency(100)
        chip.set_accel_range(AFS_SEL.FS_8G.value)
        chip.set_gyro_range(FS_SEL.FS_DEG_2000.value)
        chips.append(chip)

    # Set up simultaneous threads for data collection and transmission
    queue = Queue()
    if tcp_send:
        THREAD_SET.append(TcpNetworkSenderThread(queue))
    elif w2f:
        THREAD_SET.append(Write2FileThread(queue))
    else:
        THREAD_SET.append(UdpNetworkSenderThread(queue)) 
    THREAD_SET.append(DataCollectionThread(queue, chips)) 

    # Execute threads
    for thread in THREAD_SET:
        thread.start()

    # ---- (?) waits until thread completes to resume the main thread (i.e the script) (but there isn't anything else...)
    for thread in THREAD_SET:
        thread.join()
