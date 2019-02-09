from icm20689 import Icm20689SPI
import icm20689_multi

chip1 = icm20689_multi(1, 0, 0, 25)
chip2 = icm20689_multi(1, 0, 0, 24)
while True:
    print(chip1.get_accel_data())
    print(chip2.get_accel_data())
