from enum import Enum, IntEnum

class ICM20689Regs(Enum):
    # All register values taken from ICM 20689 Register Map (p36 of datasheet)
    SELF_TEST_X_GYRO = 0x00
    SELF_TEST_Y_GYRO = 0x01
    SELF_TEST_Z_GYRO = 0x02
    SELF_TEST_X_ACCEL = 0x0D
    SELF_TEST_Y_ACCEL = 0x0E
    SELF_TEST_Z_ACCEL = 0x0F
    XG_OFFS_USRH = 0X13
    XG_OFFS_USRL = 0X14
    YG_OFFS_USRH = 0X15
    YG_OFFS_USRL = 0X16
    ZG_OFFS_USRH = 0X17
    ZG_OFFS_USRL = 0X18
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    ACCEL_CONFIG_2 = 0x1D
    LP_MODE_CFG = 0x1E
    ACCEL_WOM_THR = 0x1F
    FIFO_EN = 0x23
    FSYNC_INT = 0x36
    INT_PIN_CFG = 0x37
    INT_ENABLE = 0x38
    DMP_INT_STATUS = 0X39
    INT_STATUS = 0x3A
    ACCEL_XOUT_H = 0x3B
    ACCEL_XOUT_L = 0x3C
    ACCEL_YOUT_H = 0x3D
    ACCEL_YOUT_L = 0x3E
    ACCEL_ZOUT_H = 0x3F
    ACCEL_ZOUT_L = 0x40
    TEMP_OUT_H = 0x41
    TEMP_OUT_L = 0x42
    GYRO_XOUT_H = 0x43
    GYRO_XOUT_L = 0x44
    GYRO_YOUT_H = 0x45
    GYRO_YOUT_L = 0x46
    GYRO_ZOUT_H = 0x47
    GYRO_ZOUT_L = 0x48
    SIGNAL_PATH_RESET = 0x68
    ACCEL_INTEL_CTRL = 0X69
    USER_CTRL = 0x6A
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C
    FIFO_COUNTH = 0x72
    FIFO_COUNTL = 0x73
    FIFO_R_W = 0x74
    WHO_AM_I = 0x75
    XA_OFFSET_H = 0X77
    XA_OFFSET_L = 0X78
    YA_OFFSET_H = 0X7A
    YA_OFFSET_L = 0X7B
    ZA_OFFSET_H = 0X7D
    ZA_OFFSET_L = 0X7E

class EXT_SYNC_SET(Enum):
    DISABLED = 0x0
    TEMP_OUT_L = 0x1
    GYRO_XOUT_L = 0x2
    GYRO_YOUT_L = 0x3
    GYRO_ZOUT_L = 0x4
    ACCEL_XOUT_L = 0x5
    ACCEL_YOUT_L = 0x6
    ACCEL_ZOUT_L = 0x7

class FS_SEL(Enum):
    FS_DEG_250 = 0x0
    FS_DEG_500 = 0x1
    FS_DEG_1000 = 0x2
    FS_DEG_2000 = 0x3
    
    def get_lsb_sensitivity(self):
        if self.value == 0x0:
            return 131.0
        elif self.value == 0x1:
            return 65.5
        elif self.value == 0x2:
            return 32.8
        elif self.value == 0x3:
            return 16.4

class AFS_SEL(Enum):
    FS_2G = 0x0
    FS_4G = 0x1
    FS_8G = 0x2
    FS_16G = 0x3

    def get_lsb_sensitivity(self):
        if self.value == 0x0:
            return 16384.0
        elif self.value == 0x1:
            return 8192.0
        elif self.value == 0x2:
            return 4096.0
        elif self.value == 0x3:
            return 2048.0

class FIFO_EN(IntEnum):
    SLV0_FIFO_EN = 1 << 0
    SLV1_FIFO_EN = 1 << 1
    SLV2_FIFO_EN = 1 << 2
    ACCEL_FIFO_EN = 1 << 3
    ZG_FIFO_EN = 1 << 4
    YG_FIFO_EN = 1 << 5
    XG_FIFO_EN = 1 << 6
    TEMP_FIFO_EN = 1 << 7

class INT_ENABLE(IntEnum):
    DATA_RDY_EN = 1 << 0
    I2C_MST_INT_EN = 1 << 3
    FIFO_OFLOW_EN = 1 << 4

class INT_STATUS(IntEnum):
    DATA_RDY_INT = 1 << 0
    I2C_MST_INT_INT = 1 << 3
    FIFO_OFLOW_INT = 1 << 3
