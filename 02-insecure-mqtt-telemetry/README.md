# Insecure MQTT Telemetry Pipeline & Synthetic Sensor Generator

## Overview
This folder covers two steps of the Hydroficient IoT Cyber Defense externship for the simulated Grand Marina Hotel water-monitoring system: a synthetic sensor log generator (project 2) and a baseline MQTT pipeline (project 3). The pipeline deliberately has no security controls. It is the baseline that the TLS, mTLS, and replay-defense projects are measured against.

## What's in this folder
- `scripts/sensor_log_generator.py`: generates synthetic sensor logs (project 2)
- `scripts/sensor_publisher.py`: three simulated sensors publishing to MQTT every 2 seconds
- `scripts/dashboard_subscriber.py`: subscribes to the whole `hydroficient/grandmarina/#` tree and displays readings
- `config/mosquitto_insecure.conf`: plaintext broker config
- `sample-output/`: generator output and a pipeline run
- `topic-architecture.md`: the full planned topic hierarchy

## Topic Design
The planned hierarchy has four branches (`sensors`, `commands`, `alerts`, `status`) across three zones. See `topic-architecture.md`. This baseline implements the `sensors` branch only, with one topic per zone and a JSON payload:

| Device | Topic |
|---|---|
| GM-HYDROLOGIC-01 | `hydroficient/grandmarina/sensors/main-building/readings` |
| GM-HYDROLOGIC-02 | `hydroficient/grandmarina/sensors/pool-wing/readings` |
| GM-HYDROLOGIC-03 | `hydroficient/grandmarina/sensors/kitchen/readings` |

Payload fields: `device_id`, `location`, `timestamp` (UTC), `counter`, `pressure_upstream`, `pressure_downstream`, `flow_rate`.

The subscriber already has handlers for `alerts`, `commands`, and `status` topics, ready for later projects, but nothing publishes to them yet.

## Prerequisites
- Python 3 with `paho-mqtt` 2.x (`pip install -r requirements.txt`)
- Mosquitto broker installed

## How to Run
Use three terminals from this folder.
1. Start the broker: `mosquitto -c config/mosquitto_insecure.conf`
2. Start the dashboard: `python scripts/dashboard_subscriber.py`
3. Start the sensors: `python scripts/sensor_publisher.py`

Press Ctrl+C to stop.

## Sample Output
Dashboard output, one reading per device:

```text
────────────────────────────────────────
  Location:  main-building
  Device ID: GM-HYDROLOGIC-01
  Time:      2026-10-20T21:56:17.891337+00:00
  Count:     #5
────────────────────────────────────────
  Pressure (upstream):     83.0 PSI
  Pressure (downstream):   77.7 PSI
  Pressure differential:    5.3 PSI
  Flow rate:               38.1 gal/min
```

(Full run in `sample-output/pipeline_run.txt`.)

## Simulated Readings and Alert Thresholds
Each sensor varies around a base of 82 PSI upstream, 76 PSI downstream, and 40 gal/min, with small random jitter. The publisher's local display flags:

| Condition | Alert |
|---|---|
| Upstream pressure > 90 PSI | High upstream pressure |
| Downstream pressure < 65 PSI | Low downstream pressure |
| Flow > 60 gal/min | Possible leak |
| Flow < 20 gal/min | Possible blockage |

## Why It's Insecure
- Plaintext on port 1883: anyone on the network can read every message.
- `allow_anonymous true`: no username, password, or certificate is needed to connect.
- No topic restrictions: the dashboard subscribes to `hydroficient/grandmarina/#` and sees everything, and any client could publish to any topic, including the planned `commands/` topics.
- No message authentication: the subscriber trusts any JSON that arrives.

## Next
Project 4 encrypts this pipeline with TLS and measures the cost: [04-tls-and-cost](../04-tls-and-cost/)
