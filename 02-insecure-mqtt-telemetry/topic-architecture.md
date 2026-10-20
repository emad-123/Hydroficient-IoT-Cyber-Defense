# Grand Marina Hotel: MQTT Topic Hierarchy

## Topic Structure Design
The MQTT namespace is structured hierarchically by facility zone, device type, and channel:

`grand-marina/<zone>/<facility>/<device_id>/<channel>`

### Channel Specifications
- **Telemetry (`/telemetry`):** Sensor metric streams (water flow, water pressure, temperature).
- **Commands (`/cmd`):** Control actions directed to actuators and valves.
- **Alerts (`/alerts`):** High-priority operational warnings (leaks, threshold violations).
- **Status (`/status`):** Device health, connectivity, and heartbeat pings.

### Topic Mapping Examples
- `grand-marina/east-wing/boiler-room/flow-sensor-01/telemetry`
- `grand-marina/east-wing/boiler-room/valve-actuator-01/cmd`
- `grand-marina/alerts/critical`
- `grand-marina/east-wing/boiler-room/flow-sensor-01/status`

---

## Baseline Vulnerability Analysis
- **Cleartext Exposure:** All telemetry and control payloads are published over unencrypted TCP (port 1883), allowing passive packet capture.
- **Missing Authorization:** No topic-level Access Control Lists (ACLs) are configured, allowing any client to subscribe to sensitive telemetry or inject false commands.
