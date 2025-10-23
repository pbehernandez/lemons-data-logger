from contextlib import suppress
from typing import Optional, Tuple

class IMU:
    def __init__(self, addr=0x6A):
        self.dev = None
        self.ok = False
        with suppress(Exception):
            import board, busio
            from adafruit_lsm6ds.lsm6ds33 import LSM6DS33
            i2c = busio.I2C(board.SCL, board.SDA)
            self.dev = LSM6DS33(i2c, address=addr)
            self.ok = True

    def read(self) -> Tuple[Optional[float],Optional[float],Optional[float],Optional[float],Optional[float],Optional[float]]:
        if not self.ok:
            return (None,)*6
        ax, ay, az = self.dev.acceleration
        gx, gy, gz = self.dev.gyro
        return ax, ay, az, gx, gy, gz
