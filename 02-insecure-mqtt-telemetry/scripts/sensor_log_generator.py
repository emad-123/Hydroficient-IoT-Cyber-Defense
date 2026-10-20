import random
from datetime import datetime, timezone
import json

class WaterSensor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.counter = 0
        # Base values for realistic variation
        self.base_pressure_up = 82.0
        self.base_pressure_down = 76.0
        self.base_flow = 40.0

    def get_reading(self):
        """Generate a normal sensor reading"""
        self.counter += 1

        return {
            "device_id": self.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counter": self.counter,
            "pressure_upstream": round(self.base_pressure_up + random.uniform(-7, 8), 1),
            "pressure_downstream": round(self.base_pressure_down + random.uniform(-6, 9), 1),
            "flow_rate": round(self.base_flow + random.uniform(-10, 10), 1)
        }

    def get_leak_reading(self):
        """Generate a reading simulating a water leak"""
        reading = self.get_reading()
        reading["flow_rate"] = round(random.uniform(80, 120), 1)
        return reading

    def get_blockage_reading(self):
        """Generate a reading simulating a pipe blockage"""
        reading = self.get_reading()
        reading["pressure_upstream"] = round(random.uniform(85, 95), 1)
        reading["pressure_downstream"] = round(random.uniform(30, 50), 1)
        return reading

    def get_stuck_reading(self):
        """Generate a reading simulating a stuck sensor"""
        reading = self.get_reading()
        stuck_value = 82.0
        reading["pressure_upstream"] = stuck_value
        reading["pressure_downstream"] = stuck_value
        reading["flow_rate"] = stuck_value
        return reading




# Generate 100 readings
sensor = WaterSensor("GM-HYDROLOGIC-01")
readings = []

# 97 normal readings
for _ in range(97):
    readings.append(sensor.get_reading())

# 3 anomalies (for testing detection later)
readings.append(sensor.get_leak_reading())
readings.append(sensor.get_blockage_reading())
readings.append(sensor.get_stuck_reading())

# Shuffle so anomalies aren't at the end
random.shuffle(readings)

# Save to JSON file
with open("sensor_data.json", "w") as f:
    json.dump(readings, f, indent=2)

print(f"Saved {len(readings)} readings to sensor_data.json")
