#!/usr/bin/env python3
import os, json, time, random, math
from datetime import datetime, timezone

# --------- Paramètres via ENV ----------
FREQ_SECONDS = float(os.getenv("FREQ_SECONDS", "2"))
SITES = [s.strip() for s in os.getenv("SITES", "paris,lyon,berlin").split(",")]
OUT_PATH = os.getenv("OUT_PATH", "outbox/raw.energy.jsonl")
RANDOM_SEED = os.getenv("RANDOM_SEED")
if RANDOM_SEED is not None:
    random.seed(int(RANDOM_SEED))

# --------- Modèle simplifié ----------
DEVICE_MODELS = {
    ("hvac", "electricity"):    {"unit": "kWh", "baseline": 4.0,  "variability": 0.12},
    ("servers", "electricity"): {"unit": "kWh", "baseline": 6.0,  "variability": 0.06},
    ("lighting", "electricity"):{ "unit": "kWh", "baseline": 1.0,  "variability": 0.18},
    ("boiler", "gas"):          {"unit": "kWh", "baseline": 2.5,  "variability": 0.15},
    ("generator", "diesel"):    {"unit": "L",   "baseline": 0.02, "variability": 0.50},
    ("vehicle_fleet", "diesel"):{ "unit": "L",  "baseline": 0.5,  "variability": 0.25},
}
SITE_DEVICES = {
    site: [
        ("hvac", "electricity"),
        ("servers", "electricity"),
        ("lighting", "electricity"),
        ("boiler", "gas"),
        ("vehicle_fleet", "diesel"),
        ("generator", "diesel"),
    ] for site in SITES
}

def diurnal_multiplier(dt_hour: float) -> float:
    # Variation journalière simple (min la nuit, max l'après-midi)
    rad = 2*math.pi * ((dt_hour - 15) / 24.0)
    base = (math.cos(rad) + 1) / 2  # 0..1
    return 0.7 + 0.6 * base         # ~0.7..1.3

def weekend_drop(weekday: int) -> float:
    return 0.6 if weekday >= 5 else 1.0

def spike(value: float, prob=0.006, amp_range=(2.0, 5.0)) -> float:
    if random.random() < prob:
        return value * random.uniform(*amp_range)
    return 0.0

def now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def generate_value(device: str, source: str, now: datetime) -> tuple[float, str]:
    m = DEVICE_MODELS[(device, source)]
    base = m["baseline"]
    # variations
    v = base
    v *= diurnal_multiplier(now.hour + now.minute/60.0)
    v *= weekend_drop(now.weekday())
    v *= max(0.0, 1.0 + random.gauss(0, m["variability"]))
    v += spike(base, prob=0.008 if device in ("hvac","lighting") else 0.003)
    return round(max(0.0, v), 3), m["unit"]

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    print(f"[EcoPulse] Writing messages to {OUT_PATH} every {FREQ_SECONDS}s (no Kafka)")
    with open(OUT_PATH, "a", encoding="utf-8") as f:
        while True:
            now = datetime.now(timezone.utc)
            ts = now_iso_utc()
            for site, pairs in SITE_DEVICES.items():
                for device, source in pairs:
                    value, unit = generate_value(device, source, now)
                    msg = {
                        "site_id": site,
                        "device_id": device,
                        "source": source,
                        "value": value,
                        "unit": unit,
                        "ts": ts,
                    }
                    # écriture JSONL (une ligne par message)
                    f.write(json.dumps(msg) + "\n")
            f.flush()
            time.sleep(FREQ_SECONDS)

if __name__ == "__main__":
    main()
