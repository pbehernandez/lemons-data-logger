#!/usr/bin/env python3
import os, csv, time, datetime, signal, yaml
from sensors.imu import IMU
from sensors.temp import Ambient
from obd.reader import OBDReader

RUN = True
def _sig(sig,frame):
    global RUN; RUN=False
signal.signal(signal.SIGINT,_sig)
signal.signal(signal.SIGTERM,_sig)

def ensure_dir(p): os.makedirs(p, exist_ok=True)

def main():
    with open("config.yaml","r") as f:
        cfg = yaml.safe_load(f)

    hz = float(cfg.get("sample_hz", 10))
    dt = 1.0 / max(1.0, hz)
    csv_dir = cfg.get("csv_dir","./data")
    ensure_dir(csv_dir)

    imu = amb = None
    if cfg.get("i2c",{}).get("enabled",True):
        imu = IMU(addr=cfg["i2c"].get("imu_addr",0x6A))
        amb = Ambient(addr=cfg["i2c"].get("bme280_addr",0x76))

    obd = None
    if cfg.get("obd",{}).get("enabled",True):
        oc = cfg["obd"]
        obd = OBDReader(
            oc.get("device_candidates",["/dev/ttyUSB0","/dev/ttyACM0","/dev/serial0"]),
            fast=bool(oc.get("fast",False)),
            timeout=float(oc.get("timeout",1.0))
        )

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(csv_dir, f"log_{ts}.csv")
    fields = ["timestamp","rpm","throttle_pct","coolant_C",
              "ax_m_s2","ay_m_s2","az_m_s2","gx_dps","gy_dps","gz_dps",
              "ambient_C"]
    print(f"[logger] writing -> {csv_path}")

    with open(csv_path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        while RUN:
            row = {"timestamp": time.time()}

            if obd and obd.conn:
                rpm, tps, clt = obd.read()
                row["rpm"], row["throttle_pct"], row["coolant_C"] = rpm, tps, clt
            else:
                row["rpm"]=row["throttle_pct"]=row["coolant_C"]=None

            if imu and imu.ok:
                ax, ay, az, gx, gy, gz = imu.read()
                row.update({"ax_m_s2":ax,"ay_m_s2":ay,"az_m_s2":az,
                            "gx_dps":gx,"gy_dps":gy,"gz_dps":gz})
            else:
                row.update({"ax_m_s2":None,"ay_m_s2":None,"az_m_s2":None,
                            "gx_dps":None,"gy_dps":None,"gz_dps":None})

            if amb and amb.ok:
                row["ambient_C"] = amb.read_c()
            else:
                row["ambient_C"] = None

            w.writerow(row); f.flush()
            time.sleep(dt)

if __name__ == "__main__":
    main()
