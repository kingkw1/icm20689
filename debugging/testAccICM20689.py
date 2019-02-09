import smbus
import math
import RPi.GPIO as GPIO

# Power management registers
power_mgmt_1 = 0x6B
#power_mgmt_2 = 0x6C

# setup IMUs
GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD
imu1pin = 8
# imu2pin = 25
GPIO.setup(imu1pin, GPIO.OUT, initial = 1)           # link GPIO pin to each IMUs
# GPIO.setup(imu2pin, GPIO.OUT, initial = 0)
switch = False

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

try:
    while True:

#test GPIO on/off change address name on
#TODO: write function that turns desired Sensor on and all others off, call n times for n sensors
        if switch:
            #turn imu1 on
            #GPIO.output(imu2pin, 0)
            GPIO.output(imu1pin, 1)
            switch = False
            print("Reading from IMU 1")
        else:
            #turn imu2 on
            GPIO.output(imu1pin, 0)
            #GPIO.output(imu2pin, 1)
            switch = True
            print("Reading from IMU 2")


        print()
        print("gyro data")
        print("---------")

        gyro_xout = read_word_2c(0x43)
        gyro_yout = read_word_2c(0x45)
        gyro_zout = read_word_2c(0x47)

        print("gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131))
        print("gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131))
        print("gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131))

        print()
        print("accelerometer data")
        print("------------------")

        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        print("accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled)
        print("accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled)
        print("accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled)

        print("x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
        print("y rotation: " , get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))


except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt
    GPIO.cleanup()                 # resets all GPIO ports used by this program
