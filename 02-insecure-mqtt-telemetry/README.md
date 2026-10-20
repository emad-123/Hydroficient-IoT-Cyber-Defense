# Insecure MQTT Telemetry Pipeline & Synthetic Sensor Generator

## Overview
This module demonstrates the baseline IoT telemetry infrastructure designed for the Grand Marina Hotel's water monitoring system[cite: 2]. It provides a synthetic sensor log generator paired with a hierarchical MQTT pub/sub pipeline, establishing an operational baseline to evaluate security risks prior to implementing controls.

## Architecture & Topic Design
Telemetry data is organized by location and device function:
`grand-marina/<zone>/<facility>/<device_id>/<channel>`

- **Telemetry:** `grand-marina/east-wing/boiler-room/flow-sensor-01/telemetry`
- **Commands:** `grand-marina/east-wing/boiler-room/valve-actuator-01/cmd`
- **Alerts:** `grand-marina/alerts/critical`
- **Device Status:** `grand-marina/east-wing/boiler-room/flow-sensor-01/status`

## Repository Contents
- `scripts/sensor_log_generator.py` — Python simulation engine generating realistic water pressure, flow rate, and temperature readings.
- `topic-architecture.md` — Detailed breakdown of the topic hierarchy, payload schemas, and access boundaries.

## Security Findings (Baseline)
- **Cleartext Transmission:** Telemetry transmits over unencrypted TCP port 1883, exposing metrics to eavesdropping.
- **Missing Access Controls:** No topic ACLs or client authentication exist, allowing unauthorized clients to publish or subscribe.
- **No Integrity Protection:** Payloads lack HMAC signing or timestamp checks, leaving downstream consumers open to spoofing and replay attacks.
