from icm20689 import Icm20689SPI

chip = Icm20689SPI(1, 0, 0, 25)

while True:
    print(chip.get_accel_data())
