# Grand Marina Hotel — HYDROLOGIC System Threat Model

## Section 1: Executive Summary

Grand Marina Hotel relies on Hydroficient water pressure monitoring devices to track vital signs for water leaks across 3 critical water lines in the hotel. These 3 sensors continuously send water pressure rate, flow rate, gate position, and the amount of water consumed, all on one dashboard. When a water line's readings fall outside normal ranges, the system triggers immediate alerts.

This threat model identifies security risks that could affect customer safety, data privacy, and the hotel's overall reputation. IoT water monitoring sensors are increasingly targeted by attackers, since IoT devices are among the easiest and most common entry points.

Our analysis identifies three critical concerns requiring immediate attention:

- **Weak authentication** on the dashboard/cloud allows unauthorized access to customer billing data and real-time sensor readings.
- **Unencrypted device communications** could be intercepted or modified, potentially causing false readings or missed alerts.
- **Non-monitored rate limiting** on the dashboard could let an attacker flood the system with dummy packets, denying real users access.

We recommend prioritizing multi-factor authentication, encrypted communication, and server redundancy.

## Section 2: System Overview

The Grand Marina's HYDROLOGIC system:

- 500-room luxury hotel (Hydroficient customer)
- 3 HYDROLOGIC flow management devices (one per water service line)
- Cloud-based monitoring and control
- Web dashboard for operators and management
- Remote shutoff and gate control capability

### Data Flow Diagram

```
                        ┌────────────────────────────┐
                        │         DASHBOARD           │
                        │   (Operators & Marcus Webb) │
                        │                              │
                        │  View Data:     Send Commands:│
                        │  • Pressure     • Adjust gates│
                        │  • Flow rate    • Emergency   │
                        │  • Savings        shutoff     │
                        │                 • Bypass mode │
                        └───────────┬──────────────────┘
                             ↑ Data │ ↓ Commands
                                    │
┌───────────────────┐      ┌───────▼────────┐
│  HYDROLOGIC        │◄────┤    Cloud API    │
│  Devices            │────►│                 │
│  • Main Bldg        │Data │                 │
│  • Pool/Spa       Cmds↓   │                 │
│  • Kitchen           │    └───┬─────────┬───┘
│  • Guest Rooms       │        │Data     │Data
│  • Restaurants       │   Cmds↓│    Cmds↓│
│  • Fitness           │  ┌─────▼───┐ ┌───▼──────┐
│  • Laundry           │  │  Gate    │ │ Database │
└──────────────────────┘  │ Controls │ │          │
                           └────┬─────┘ └────┬─────┘
                           Cmds↓│             │
                       ┌────────▼──┐    ┌─────▼───┐
                       │ Emergency │    │ Reports │
                       │  Shutoff  │    │         │
                       └───────────┘    └─────────┘
```

### How It Works

1. **Sensors collect** water info from rooms, pools, and kitchens.
2. **Devices send** this info up to the Cloud API.
3. **Cloud API saves** everything inside the main Database.
4. **Database updates** the system logs to create simple reports.
5. **Dashboard shows** live updates to the system operators.
6. **Operators send** commands like gate adjustments from screens.
7. **Cloud API passes** those commands down to hardware.
8. **Gate Controls** change water flow or shut it off.

## Section 3: Asset Inventory

Key assets and their CIA (Confidentiality, Integrity, Availability) priorities:

| Asset | Description | C Priority | I Priority | A Priority |
|---|---|---|---|---|
| HYDROLOGIC Devices | 3 flow management units | Medium | Critical | Critical |
| Web Dashboard | Operator monitoring interface | High | High | Critical |
| Cloud API | Device-to-cloud communication | High | Critical | Critical |
| Remote Controls | Gate adjustments, emergency shutoff | Critical | High | Critical |
| Consumption Data | Savings reports, billing records | Medium | High | Medium |

**Priority Rationale:**

- Integrity is Critical for devices and vitals — wrong readings could lead to incorrect shutoff decisions.
- Availability is Critical for dashboard and alerts — downtime during an emergency could cost lives and money.
- Confidentiality is Medium for consumption data — not too sensitive.

## Section 4: STRIDE Analysis

### Component 1: HYDROLOGIC Devices

| Threat | Scenario | Likelihood | Impact | Risk |
|---|---|---|---|---|
| Spoofing | Attacker introduces a fake device on the hotel's network that sends false alarms for a non-existent device | Medium | High | High |
| Tampering | Attacker with physical access modifies device firmware to report normal readings regardless of actual conditions | Low | Critical | High |
| Repudiation | Device sends an alert but no log proves which device or when — "the system never alerted us" | Medium | Medium | Medium |
| Info Disclosure | Attacker on hotel's Wi-Fi captures unencrypted data, learns water flow information | High | Medium | High |
| Denial of Service | Attacker floods the system with fake packets; operator can't access the system | Medium | Critical | Critical |
| Elevation of Privilege | Attacker exploits a device vulnerability to gain access to the hotel network, pivots to other systems | Low | Critical | High |

### Component 2: Web Dashboard

| Threat | Scenario | Likelihood | Impact | Risk |
|---|---|---|---|---|
| Spoofing | Attacker uses stolen system operator credentials (from phishing) to access dashboard from outside hotel | High | Critical | Critical |
| Tampering | Attacker with dashboard access modifies alert thresholds — raises water pressure limit from 60 psi to 80+ psi | Medium | Critical | Critical |
| Repudiation | System operator claims they did not acknowledge an alert; no audit trail for who saw what and when | Medium | Medium | Medium |
| Info Disclosure | Attacker gains dashboard access, exports water consumption data and customer billing data | Medium | Medium | Medium |
| Denial of Service | Attacker floods dashboard with requests; system operators can't view any water flow data | Medium | Critical | Critical |
| Elevation of Privilege | Operator account exploits a bug to gain admin access, can now view/modify system configuration and trigger shutoffs | Low | Critical | High |

### Component 3: Cloud API

| Threat | Scenario | Likelihood | Impact | Risk |
|---|---|---|---|---|
| Spoofing | Attacker creates a fake cloud endpoint; water system gateway sends all readings to the attacker's server | Low | Critical | High |
| Tampering | Attacker with access modifies water readings | Low | Critical | High |
| Repudiation | Hydroficient system claims a water leak alert was sent; hotel's system operator claims it never arrived | Medium | High | High |
| Info Disclosure | Cloud database breach exposes vital records for hotel customers | Low | High | Medium |
| Denial of Service | DDoS attack on Hydroficient cloud takes down monitoring for the whole hotel | Medium | Critical | Critical |
| Elevation of Privilege | Hydroficient support employee accesses sensitive data without authorization | Medium | High | High |

### Component 4: Remote Controls (Gate/Shutoff)

| Threat | Scenario | Likelihood | Impact | Risk |
|---|---|---|---|---|
| Spoofing | Attacker sends fake critical alerts for water lines, causing the operator to perform a gate shutoff | Medium | Medium | Medium |
| Tampering | Attacker intercepts and blocks real critical alerts before they reach the operator | Low | Critical | High |
| Repudiation | Alert was generated but no proof it was delivered to the correct operator on duty | Medium | High | High |
| Info Disclosure | Alert messages contain sensor readings and gate settings; attacker intercepts to learn how to later manipulate them | Medium | Medium | Medium |
| Denial of Service | Attacker floods alert system with false positives, forcing a gate shutoff | Medium | Critical | Critical |
| Elevation of Privilege | Attacker breaches the system and discovers they can modify all alerts and trigger shutoffs | Low | Critical | High |

## Section 5: Risk Summary

### Critical Risks

1. **Unencrypted device communications (Info Disclosure)** — Water sensor readings transmitted over the hotel's Wi-Fi without encryption. Any attacker on the network can capture this information.
2. **Weak dashboard authentication (Spoofing)** — A single password protects access to all water sensor data and alert settings. Phishing attacks could lead to a stolen credential resulting in full access.
3. **Alert system flooding (DoS)** — Alert system has no rate limiting. An attacker could flood it with false alerts, causing real critical alerts to be missed — a customer safety risk.
4. **Dashboard tampering (Tampering)** — Users with dashboard access can modify alert thresholds. A malicious insider or compromised account could raise thresholds so critical alerts never trigger.
5. **Cloud service single point of failure (DoS)** — All 3 devices depend on the Hydroficient cloud. An outage affects the entire hotel simultaneously, with no local fallback.

### High Risks

1. **Device network pivot (Elevation)** — A compromised HYDROLOGIC device could provide an entry point to the hotel network and other systems.
2. **Customer billing data export (Info Disclosure)** — Dashboard allows bulk export of historical data with no additional authorization.
3. **Firmware tampering (Tampering)** — Physical access to a device allows firmware modification with no integrity verification.
4. **Alert delivery gaps (Repudiation)** — No confirmation that critical alerts reached their intended recipients.

### Medium Risks

1. Device spoofing on the network
2. Dashboard action audit gaps
3. Alert interception
4. False alert injection

## Section 6: Recommended Mitigations

### For Critical Risks

| Risk | Proposed Mitigation | Implementation Complexity |
|---|---|---|
| Weak dashboard authentication | Enable multi-factor authentication | Low — configuration change |
| Unencrypted device communications | Implement TLS encryption for all device-to-gateway communication | Medium — firmware update required |
| Dashboard tampering | Require admin approval for threshold changes; add confirmation dialogs | Low — application update |
| Cloud single point of failure | Implement local gateway fallback mode with on-premise data caching | High — architecture change |

### For High Risks

| Risk | Proposed Mitigation | Implementation Complexity |
|---|---|---|
| Device network pivot | Segment HYDROLOGIC devices on an isolated VLAN, separate from the hotel network | Medium — network configuration |
| Customer data export | Add re-authentication requirement for bulk data exports | Low — application update |
| Firmware tampering | Enable secure boot and signed firmware verification | High — hardware/firmware update |
| Alert delivery gaps | Implement delivery receipts and escalation for unacknowledged critical alerts | Medium — application update |
| Insider cloud access | Implement zero-trust access controls and comprehensive audit logging | Medium — policy and technical changes |
