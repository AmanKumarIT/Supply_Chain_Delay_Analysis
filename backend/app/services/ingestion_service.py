import random

DISRUPTION_PRESETS = {
    "severe_weather": {"weather": 0.9, "traffic": 0.4, "congestion": 0.5},
    "port_congestion": {"weather": 0.1, "traffic": 0.3, "congestion": 0.95},
    "traffic_jam":    {"weather": 0.2, "traffic": 0.9, "congestion": 0.3},
    "clear":          {"weather": 0.0, "traffic": 0.1, "congestion": 0.1},
}

def simulate_disruption(preset: str = "severe_weather") -> dict:
    base = DISRUPTION_PRESETS.get(preset, DISRUPTION_PRESETS["severe_weather"]).copy()
    # Add small random noise so repeated simulations vary
    base["weather"]    = min(base["weather"]    + random.uniform(-0.05, 0.05), 1.0)
    base["traffic"]    = min(base["traffic"]    + random.uniform(-0.05, 0.05), 1.0)
    base["congestion"] = min(base["congestion"] + random.uniform(-0.05, 0.05), 1.0)
    return base
