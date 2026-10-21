# Enforcing Device Identity with Mutual TLS

## Overview
Project 4 encrypted the MQTT pipeline with TLS, but any client that trusted the CA could still connect, subscribe, and publish. This project closes that gap with mutual TLS (mTLS): the broker now requires every device to present its own client certificate, so a device is accepted because of who it is, not just because it can reach the port. The project also produces a device provisioning policy for the simulated Grand Marina Hotel water-monitoring system, covering how devices are onboarded, rotated, investigated, and retired. It builds on [04-tls-and-cost](../04-tls-and-cost/).

## What's in this folder
- `scripts/generate_certs.py`: creates the Certificate Authority (CA) and the broker certificate
- `scripts/generate_client_certs.py`: issues one client certificate per device, signed by the CA, with the device ID embedded as the certificate's Common Name
- `scripts/publisher_mtls.py`: sensor publisher that authenticates with its client certificate
- `scripts/subscriber_mtls.py`: dashboard subscriber that authenticates with its client certificate
- `scripts/identity_tester.py`: tests connection attempts made with different identities
- `scripts/mtls_benchmark.py`: measures the cost of mTLS
- `config/mosquitto_mtls.conf`: broker configuration requiring client certificates
- `config/mosquitto_mtls_benchmark.conf`: broker configuration used for the benchmark
- `results/`: benchmark output
- `docs/device_provisioning_policy.pdf`: the provisioning policy

`certs/` is not in the repo. The CA, certificates, and private keys are generated locally and excluded by `.gitignore`.

## Prerequisites
- Python 3 with `paho-mqtt` 2.x and the packages used by the certificate scripts (`pip install -r requirements.txt`)
- Mosquitto broker installed

## How to Run
Run everything from this folder.
1. Create the CA and broker certificate: `python scripts/generate_certs.py`
2. Create a certificate for each device: `python scripts/generate_client_certs.py --device-id <device-id>`
3. Start the mTLS broker: `mosquitto -c config/mosquitto_mtls.conf`
4. Start the subscriber: `python scripts/subscriber_mtls.py`
5. Start the publisher: `python scripts/publisher_mtls.py`
6. Run the identity checks: `python scripts/identity_tester.py`
7. Run the benchmark: `python scripts/mtls_benchmark.py` (uses `config/mosquitto_mtls_benchmark.conf`)

## How the Identity Model Works
- One CA signs every certificate in the system.
- Each device gets its own certificate and private key. Certificates are never shared or reused between devices.
- The device ID is embedded in the certificate, so the broker can tie a connection to a specific device.
- The broker checks the device's certificate, and the device checks the broker's. Both sides must pass.

## Device Provisioning Policy
The full policy is in [`docs/device_provisioning_policy.pdf`](docs/device_provisioning_policy.pdf). It covers:

| Section | What it defines |
|---|---|
| Onboarding | Registering the device, generating its certificate, installing it on site, verifying the connection, and documenting it. About 30 minutes per device. |
| Two-person verification | One technician installs the certificate and a second independently checks that its fingerprint and device ID match the registry and the physical label. |
| CA key handling | The CA private key is stored encrypted and offline, accessible only to authorized security engineers, and never kept in source control. |
| Rotation | One-year certificates, rotation starts 30 days before expiry, and new keys are always generated (never reused). The old certificate is revoked only after the new one is confirmed working. |
| Compromised device | Revoke the certificate, disconnect the device (not just power it off), notify stakeholders within 15 minutes, investigate within 24 hours, then re-provision with fresh keys. |
| Decommissioning | Revoke the certificate, remove the device from the broker and dashboard, factory reset, and archive logs for 90 days. |

The policy states that the broker must reject:
1. any unencrypted connection on port 1883
2. a connection with no client certificate
3. a certificate not signed by the project CA
4. an expired or revoked certificate
5. a device publishing to a topic that belongs to a different device

New devices are verified with at least one negative test (for example, an attempted connection on port 1883) before they are left in service.

## Security Notes
**What mTLS fixes from project 4:** anonymous or unknown clients can no longer connect. Each device has its own identity, so a single compromised device can be revoked without touching the others.

**What it does not fix:**
- **Replay attacks.** A captured valid message can still be resent. Project 6 tests this and defends against it.
- **Stolen keys.** If an attacker obtains a device's private key and certificate, they can impersonate that device until the certificate is revoked. This is why the policy covers key handling and fast revocation.
- **CA compromise.** If the CA key is exposed, every certificate it signed must be treated as untrusted.

## Limitations
- This is a lab setup. The policy is a design document for the simulated Grand Marina scenario, and the approval and signature fields for the reviewer and the General Manager are not filled in.
- The emergency contact details in the policy are placeholders.

## Next
Project 6 attacks the pipeline with replayed messages and tests three defenses: [06-replay-defenses](../06-replay-defenses/)
