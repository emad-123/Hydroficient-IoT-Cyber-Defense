# Securing the Pipeline with TLS & Measuring the Cost

## Overview
This project adds TLS encryption to the baseline MQTT pipeline from [02-insecure-mqtt-telemetry](../02-insecure-mqtt-telemetry/) for the simulated Grand Marina Hotel water-monitoring system. It tests whether TLS works, whether it can be bypassed, and what it costs, then turns the results into a recommendation for the General Manager. The full report is in [`docs/security_assessment.pdf`](docs/security_assessment.pdf).

## What's in this folder
- `scripts/generate_certs.py`: generates the CA and server certificates
- `scripts/publisher_tls.py`: sensor publisher connecting over TLS (port 8883)
- `scripts/subscriber_tls.py`: dashboard subscriber connecting over TLS
- `scripts/experiment_runner.py`: runs the experiments
- `config/mosquitto_insecure.conf`: baseline broker, plaintext on port 1883
- `config/mosquitto_tls.conf`: TLS broker on port 8883
- `results/`: experiment output
- `docs/security_assessment.pdf`: report for the General Manager

`certs/` is not in the repo. Certificates and keys are generated locally and excluded by `.gitignore`.

## Broker Configuration
| Setting | Value | Meaning |
|---|---|---|
| `listener` | 8883 | TLS port |
| `cafile` / `certfile` / `keyfile` | `certs/ca.pem`, `certs/server.pem`, `certs/server-key.pem` | Server identity |
| `require_certificate` | false | Clients do not need a certificate |
| `allow_anonymous` | true | No username or password required |

## Prerequisites
- Python 3 with `paho-mqtt` 2.x (`pip install -r requirements.txt`)
- Mosquitto broker installed

## How to Run
Run everything from this folder.
1. Generate certificates: `python scripts/generate_certs.py`
2. Start the TLS broker: `mosquitto -c config/mosquitto_tls.conf`
3. Start the subscriber: `python scripts/subscriber_tls.py`
4. Start the publisher: `python scripts/publisher_tls.py`
5. Run the experiments: `python scripts/experiment_runner.py`

The plaintext baseline uses `config/mosquitto_insecure.conf` on port 1883.

## Experiments
Four tests, run on a lab test sensor (not a live system):

| # | Test | Question |
|---|---|---|
| 1 | Eavesdropping | Can a listener read sensor data? |
| 2 | Certificate validation | What happens with a correct, wrong, or disabled certificate check? |
| 3 | Speed | How much latency does TLS add? (50 messages per configuration) |
| 4 | Stress | Does TLS hold up at 10, 25, 50, and 100 messages/second? |

## Results

**Eavesdropping**
| | Result |
|---|---|
| Plaintext | Listener captured all 5 messages: device ID, pressure, flow rate |
| TLS | Connection error, no messages visible |

**Certificate validation**
| Scenario | Result |
|---|---|
| Correct certificate | Connected |
| Wrong certificate | Blocked (certificate verification error) |
| Verification switched off | Connected without checking who was on the other end |

**Latency (ms, 50 messages each)**
| Metric | Plaintext | TLS |
|---|---|---|
| Average | 50.97 | 51.04 |
| Fastest | 0.49 | 0.63 |
| Slowest | 100.99 | 101.34 |

**Stress test:** all four loads (10, 25, 50, 100 msg/s) succeeded with and without TLS. At the 100 msg/s load, TLS delivered 96.8 msg/s over 3,000 messages with zero errors.

## Findings
- **TLS blocked eavesdropping.** The same listener that read every plaintext message saw nothing over TLS.
- **The cost was negligible in the lab.** Average latency rose by 0.07 ms (about 0.14%).
- **Capacity was not an issue.** TLS handled double the assumed 50 msg/s emergency load with zero errors.
- **Certificate verification must be enforced.** With verification switched off, the connection was accepted anyway. TLS is only as strong as the check on the other end.
- **Recommendation:** enable TLS on all sensors and make certificate verification mandatory.

## Limitations
- Lab test on a single test sensor, not Grand Marina's live system.
- Per-message latency does not capture connection setup, where TLS costs the most. Sensors should stay connected rather than reconnect for every reading.
- Publishing fake readings was not tested. The report names it as a risk but does not claim to have tested it.

## Security Notes
**TLS protects against** passive eavesdropping and tampering in transit.

**It does not protect against** unauthorized clients: with `require_certificate false` and `allow_anonymous true`, any client that trusts the CA can connect, subscribe to `hydroficient/grandmarina/#`, and publish. Project 5 closes this with mutual TLS.

## Next
Project 5 adds device identity with mutual TLS: [05-mtls-device-identity](../05-mtls-device-identity/)
