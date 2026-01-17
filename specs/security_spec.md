# Security: Anti-Betrayal Protocol (Full Stack)

## Hardware Root of Trust

- **SoC**: Libre-SOC (open RISC-V, 64-bit, MMU)
- **PUF**: SRAM-based physical unclonable function → generates device-unique key
- **Boot ROM**: Mask-programmed, immutable → verified boot chain
- **Debug port**: Physically fused post-deployment

## Beam Authorization Flow (Cryptographically Secure)

```mermaid
sequenceDiagram
    participant G as GRN (PUF-bound)
    participant M as MOR
    participant C as BeamAuth.sol (L2)

    G->>M: BEACON{id, pubkey_puf, timestamp, sig_puf}
    M->>C: verifyNode(id, pubkey_puf)
    C-->>M: {active: true, area_m2: 1000000}
    M->>G: CHALLENGE{nonce}
    G->>M: RESPONSE{HMAC(nonce, session_key_puf)}
    M->>G: BEAM ON (sub-beam focused)
    loop Every 50 ms
        G->>M: HEARTBEAT{timestamp, HMAC(session_key_puf)}
    end
    Note right of M: Miss 2 heartbeats → DEFLECT in <100 ms

## No Backdoor Guarantee
All code public: github.com/iamGodofall/heliosphere
Reproducible builds: SHA256 hash pinned to Git commit (verified by CI)
Zero remote access: Only local debug port (physically disabled post-deploy)
Firmware updates: Require 3-of-5 multi-sig from Global Oversight Council
Critical Security Properties
Identity binding: GRN pubkey derived from PUF → cannot be cloned
Forward secrecy: Session keys ephemeral → compromise today doesn’t affect past/future
Policy enforcement: Power density validated on-chain (requested_power / area_m2 ≤ 1000 W/m²)
Liveness guarantee: Beam defocuses in <100 ms on heartbeat loss
No override: Even builder cannot bypass heartbeat check.

“Not even the builder can betray the commons.”
