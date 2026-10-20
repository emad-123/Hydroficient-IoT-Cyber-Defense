import json
import random
import threading
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt


# --- 1. NEW DISPLAY FUNCTION PLACED HERE ---
def display_reading(data):
    """Format and display a sensor reading with alerts."""

    location = data.get("location", "Unknown")
    device_id = data.get("device_id", "Unknown")  # Fixed spacing indentation
    up = data.get("pressure_upstream", 0)
    down = data.get("pressure_downstream", 0)
    flow = data.get("flow_rate", 0)

    # Check for anomalies
    alerts = []

    if up > 90:
        alerts.append("🚨HIGH UPSTREAM PRESSURE")
    if down < 65:
        alerts.append("⚠️LOW DOWNSTREAM PRESSURE")
    if flow > 60:
        alerts.append("🚨HIGH FLOW RATE - POSSIBLE LEAK")
    if flow < 20:
        alerts.append("⚠️LOW FLOW RATE - POSSIBLE BLOCKAGE")

    # Display
    print(f"\n{'─' * 40}")
    print(f"  Location:  {location}")
    print(f"  Device ID: {device_id}")  # Fixed spacing indentation

    if alerts:
        print("  *** ALERTS ***")
        for alert in alerts:
            print(f"  >>> {alert}")

    print(f"{'─' * 40}")
    print(f"  Pressure: {up:.1f} / {down:.1f} PSI")
    print(f"  Flow:     {flow:.1f} gal/min")


# --- 2. EXISTING CODE CONTINUES DOWN BELOW ---
class WaterSensorMQTT:

    def __init__(self, device_id, location, broker="localhost", port=1883):
        self.device_id = device_id
        self.location = location
        self.counter = 0

        # MQTT setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect(broker, port)
        self.client.loop_start()

        # Topic for this sensor
        self.topic = (
            f"hydroficient/grandmarina/sensors/{self.location}/readings"
        )

        # Base values for realistic variation
        self.base_pressure_up = 82
        self.base_pressure_down = 76
        self.base_flow = 40

    def get_reading(self):
        """Generate a sensor reading with realistic variation."""
        self.counter += 1
        return {
            "device_id": self.device_id,
            "location": self.location,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counter": self.counter,
            "pressure_upstream": round(
                self.base_pressure_up + random.uniform(-2, 2), 1
            ),
            "pressure_downstream": round(
                self.base_pressure_down + random.uniform(-2, 2), 1
            ),
            "flow_rate": round(self.base_flow + random.uniform(-3, 3), 1),
        }

    def publish_reading(self):
        """Generate a reading and publish it to MQTT."""
        reading = self.get_reading()
        self.client.publish(self.topic, json.dumps(reading))
        return reading

    def run_continuous(self, interval=2):
        """Publish readings continuously at the specified interval."""
        print(f"Starting device: {self.device_id}")
        print(f"Location: {self.location}")
        print(f"Publishing to: {self.topic}")
        print(f"Interval: {interval} seconds")
        print("-" * 40)
        try:
            while True:
                reading = self.publish_reading()
                # Use the new display function instead of the basic print statement
                display_reading(reading)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nSensor {self.device_id} stopped.")
            self.client.loop_stop()
            self.client.disconnect()


def run_sensor(device_id, location, interval):
    sensor = WaterSensorMQTT(device_id=device_id, location=location)
    sensor.run_continuous(interval)


devices = [
    {"device_id": "GM-HYDROLOGIC-01", "location": "main-building"},
    {"device_id": "GM-HYDROLOGIC-02", "location": "pool-wing"},
    {"device_id": "GM-HYDROLOGIC-03", "location": "kitchen"},
]

threads = []
for d in devices:
    t = threading.Thread(
        target=run_sensor, args=(d["device_id"], d["location"], 2), daemon=True
    )
    t.start()
    threads.append(t)

print("All sensors running. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping simulation.")
