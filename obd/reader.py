from contextlib import suppress
from typing import Optional

class OBDReader:
    def __init__(self, device_candidates, fast=False, timeout=1.0):
        self.conn = None
        self.OBD = None
        with suppress(Exception):
            import obd
            self.OBD = obd
            for dev in device_candidates:
                with suppress(Exception):
                    c = obd.OBD(dev, fast=fast, timeout=timeout)
                    if c and c.is_connected():
                        self.conn = c
                        break

        if self.conn and self.OBD:
            self.CMD_RPM = self.OBD.commands.RPM
            self.CMD_TPS = self.OBD.commands.THROTTLE_POS
            self.CMD_CLT = self.OBD.commands.COOLANT_TEMP

    def _q(self, cmd) -> Optional[float]:
        if not self.conn: return None
        r = self.conn.query(cmd)
        if r.is_null(): return None
        try:
            return float(getattr(r.value, "magnitude", r.value))
        except Exception:
            return None

    def read(self):
        if not self.conn:
            return None, None, None
        rpm  = self._q(self.CMD_RPM)
        tps  = self._q(self.CMD_TPS)
        clt  = self._q(self.CMD_CLT)
        return rpm, tps, clt
