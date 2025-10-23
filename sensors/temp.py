from contextlib import suppress
from typing import Optional

class Ambient:
    def __init__(self, addr=0x76):
        self.dev = None
        self.ok = False
        with suppress(Exception):
            import board, busio
            from adafruit_bme280 import basic as adafruit_bme280
            i2c = busio.I2C(board.SCL, board.SDA)
            self.dev = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=addr)
            self.ok = True

    def read_c(self) -> Optional[float]:
        if not self.ok:
            return None
        return float(self.dev.temperature)
