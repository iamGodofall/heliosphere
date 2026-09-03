# Assumptions and Technical Dependencies

This document outlines key assumptions, technical dependencies, and risk factors for the Heliosphere project. These are based on current (2024) technology readiness levels (TRL) and expected advancements by 2030–2050.

## Core Assumptions

### 1. Material and Component Maturity
- **Perovskite/GaAs Tandem Solar Cells (40% AM0 Efficiency)**:
  - TRL: 4 (lab-validated, 2024 NREL records)
  - Risk: Space radiation degradation; requires encapsulation and testing at 0.5 AU
  - Mitigation: Use GaAs-only cells (35% efficiency, TRL 9) as fallback

- **GaN-on-SiC MMICs (85% RF Efficiency at 5.8 GHz)**:
  - TRL: 5 (DARPA-funded prototypes, 2023)
  - Risk: Radiation hardness unproven for deep-space orbits
  - Mitigation: Redundant MMIC arrays with automatic failover

- **Inflatable CFRP Booms + Dyneema Tethers**:
  - TRL: 7 (used in Starlink Gen2, 2024)
  - Risk: Micrometeorite puncture
  - Mitigation: Self-healing polymers (emerging tech)

### 2. Orbital and Propulsion Feasibility
- **Nuclear-Electric Tug for 0.5 AU Deployment**:
  - Assumes availability by 2035 (post-Artemis program)
  - Risk: Regulatory delays on nuclear propulsion
  - Mitigation: Solar-electric propulsion (slower, but TRL 9)

- **Stable 0.5 AU Orbit**:
  - Assumes Venus-Earth L3-like point stability
  - Risk: Orbital perturbations from Jupiter
  - Mitigation: Station-keeping thrusters (ion engines, TRL 9)

### 3. Economic and Scaling Assumptions
- **Launch Costs ($100/kg to 0.5 AU)**:
  - Based on reusable super-heavy launchers (e.g., Starship derivatives)
  - Risk: If costs remain >$200/kg, project becomes uneconomical
  - Mitigation: In-situ resource utilization (lunar aluminum mining, TRL 3)

- **Global Investment (0.15% of GDP)**:
  - Assumes green bond markets scale to $150B/year
  - Risk: Geopolitical instability
  - Mitigation: Decentralized funding via GRN cooperatives

## Technical Dependencies

### Software and Firmware
- **RISC-V SoC with seL4 Microkernel**:
  - TRL: 8 (used in space missions, 2024)
  - Dependency: Open-source toolchain maturity

- **Ed25519 Cryptography for Beacon Signing**:
  - TRL: 9 (quantum-resistant, widely deployed)
  - Dependency: Hardware-accelerated Ed25519 in radiation-hardened chips

### Simulation and Validation
- **Beam Propagation Models**:
  - Assumes Gaussian beam approximation holds for diffraction-limited systems
  - Dependency: Validation against ESA/NASA SBSP simulations

## Risk Mitigation Strategies

1. **Prototyping Roadmap**:
   - 2026: Ground-based 1-kW rectenna demo
   - 2028: LEO 100-kW beam test
   - 2032: GEO MOR prototype

2. **Fallback Technologies**:
   - If GaN fails: Solid-state amplifiers (lower efficiency, but TRL 9)
   - If perovskite fails: Multi-junction GaAs (30% efficiency, TRL 9)

3. **Regulatory Assumptions**:
   - Operates under Outer Space Treaty (1967) and Moon Agreement (1979)
   - Assumes ICNIRP safety guidelines remain at 1 kW/m² limit

## Open Research Questions
- Long-term radiation effects on perovskite cells at 0.5 AU
- Scalability of inflatable structures beyond 1 km diameter
- Economic viability without subsidies

These assumptions will be updated as TRLs advance. All designs are modular to accommodate technology substitutions.

---

## Measured, 3 September 2026 — the simulator had never been run

`make sim` invoked `python3 sim/beam_trace.py` with no arguments, and the script
requires `--ish_power` and `--distance`. It exited 2 every time, and `make all`
failed with it. Nobody had seen this simulator's output.

`main(args=None)` accepted an argument list and then ignored it — the body read
`if args is None: args = parser.parse_args()`, so a caller passing a list had
that list bound straight to `args` and the next line died with
`'list' object has no attribute 'ish_power'`. The signature promised
programmatic use and could not deliver it, so no test, sweep or notebook could
drive the model either.

Both are fixed, and `make test` now runs 10 assertions against the physics.

### What the simulator says about this repository's own design point

Run at the figures `docs/README.md` states — 10 GW at the ISH, beamed to a
geostationary MOR at 35,786 km:

| | |
|---|---|
| Beam divergence | 63.4 µrad, the diffraction limit for 5.8 GHz through a 1 km aperture |
| Spot diameter | **2.27 km** |
| Power density | **2,470 W/m²** |
| Verdict | **exceeds the 1,000 W/m² limit the code checks against, by 2.5×** |

That is the repository's own tool applied to the repository's own numbers, and
it is a real constraint on the architecture rather than a bug to fix: either the
aperture grows, the power per satellite falls, or the receiving station is not a
place people can stand.

### And the safety constant itself wants checking

`SAFETY_LIMIT_WPM2 = 1000.0` carries the comment "ICNIRP limit at 5.8 GHz".
ICNIRP's published 2020 reference level for **general public** exposure at that
frequency is substantially lower. The constant was left exactly as found and
flagged here rather than quietly changed, because choosing an exposure limit is
an engineering and regulatory decision, not a typo fix. If the lower figure is
the right one, the gap above widens by orders of magnitude.

### A display bug found on the way

`Spot diameter: {:.0f} km` printed **"0 km"** for any spot under 500 m while the
power density beside it was computed from the true value — a readout stating the
beam has no width. It prints kilometres to three decimals and metres alongside
now.
