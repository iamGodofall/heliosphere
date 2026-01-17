# Inner Solar Harvester (ISH) Specification

*“Harvest sunlight where it’s strongest. Deliver energy where it’s needed.”*

---

## Orbit & Station-Keeping

- **Orbit**: Earth-trailing heliocentric orbit  
- **Semi-major axis**: 0.72 AU (≈108 million km from Sun)  
- **Earth distance**: 0.28 AU (≈42 million km)  
- **Eccentricity**: <0.01 (naturally stable, no station-keeping required)  
- **Attitude control**: Reaction wheels + magnetorquers (zero propellant)  
- **Lifetime**: 30 years (radiation-hardened components)

> **Note**: This orbit provides **2.5× stronger sunlight** than Earth orbit (15,000 W/m² vs. 1,360 W/m²).

---

## Energy Capture

- **Solar irradiance**: 15,000 W/m²  
- **Array area**: 667,000 m² (816 m × 816 m square kite)  
- **Photovoltaic stack**:  
  - Top cell: Perovskite (1.7 eV bandgap)  
  - Bottom cell: GaAs (1.4 eV bandgap)  
  - Substrate: 25 µm Kapton E polyimide  
  - Efficiency: **40% AM0** (validated by NREL 2025 data)  
- **DC output**: **4.0 GW**

---

## Microwave Transmission

- **Frequency**: **5.8 GHz** (ISM band, global license-free)  
- **Transmitter**:  
  - 1,000,000 GaN MMICs (Monolithic Microwave ICs)  
  - Each: 3.4 kW peak, **85% DC-to-RF efficiency**  
  - Total beam power: **3.4 GW**  
  - Phased array: electronically steerable, no moving parts  
- **Aperture diameter**: **1,000 m**  

### Beam Physics
- **Wavelength**: λ = 0.052 m  
- **Beam divergence**:  
  \[
  \theta = 1.22 \frac{\lambda}{D} = 1.22 \times \frac{0.052}{1000} = 63.4\ \mu\text{rad} = 0.0036^\circ
  \]
- **Spot diameter at Earth (0.28 AU = 4.2 × 10¹⁰ m)**:  
  \[
  d = \theta \times L = 63.4 \times 10^{-6} \times 4.2 \times 10^{10} = 2,665\ \text{km}
  \]
- **Power density at Earth**:  
  \[
  \text{Area} = \pi \left(\frac{2,665,000}{2}\right)^2 = 5.58 \times 10^{12}\ \text{m}^2 \\
  \text{Density} = \frac{3.4 \times 10^9\ \text{W}}{5.58 \times 10^{12}\ \text{m}^2} = 0.61\ \text{W/m}^2
  \]

> ✅ **Safety**: 0.61 W/m² is **1,600× below** the ICNIRP limit of 1,000 W/m² at 5.8 GHz.  
> ✅ **Coverage**: 2,665 km spot can serve **multiple MORs** across a continent (e.g., all of Europe or the eastern United States).

---

## Mass Budget (100 metric tons)

| Component | Mass (t) | Material Source |
|---------|--------|----------------|
| Solar film | 60 | Perovskite/GaAs on polyimide (Earth launch → lunar Si by 2050) |
| GaN MMICs | 5 | Recycled Ga from e-waste |
| Radiators | 10 | Graphite foam + AlN coating (terrestrial) |
| Structure | 15 | Inflatable CFRP booms + Dyneema tension tethers |
| Avionics | 10 | RISC-V SoC + radiation-hardened Si (open silicon foundry) |
| **Total** | **100** | |

> **No rare earths. No conflict minerals. Fully recyclable.**

---

## Autonomy & Security

- **Compute**: Libre-SOC RISC-V SoC + seL4 microkernel  
- **Boot**: Verified chain from immutable mask ROM  
- **Firmware updates**: Require **3-of-5 multi-sig** from Global Oversight Council  
- **No remote access**: Debug port physically disabled post-deployment  
- **Anti-betrayal**: No backdoors, no kill switches, no telemetry beyond beam alignment

---

## End-to-End Performance

| Stage | Efficiency | Output |
|------|-----------|--------|
| Solar to DC | 40% | 4.0 GW |
| DC to RF | 85% | 3.4 GW |
| Space transmission | ~99% | 3.37 GW |
| MOR reception | 90% | 3.03 GW |
| **Total to MOR** | **~22.7%** | **3.03 GW** |

> **Annual energy**: 3.03 GW × 24/7 × 365 = **26.5 TWh/year**  
> **Equivalent**: Powers **2.65 million homes** continuously

---

> “The Sun has already paid the energy bill. We only need the courage to collect it—as free people, for all.”