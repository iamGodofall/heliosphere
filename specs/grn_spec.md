# Ground Reception Node (GRN) Specification

## Rectenna Design
- **Type**: Transparent dipole array on PET film
- **Frequency**: 5.8 GHz (ISM band)
- **Efficiency**: 90% (GaAs Schottky diodes)
- **Power density limit**: **1 kW/m²** (enforced by MOR)

## Integration
- **Output**: 
  - **Micro (1–10 kW)**: 48–400 V DC → batteries/local loads
  - **Urban (10–100 MW)**: ±100 kV DC → city HVDC microgrid
- **Excess energy**: Electrolyzer → green H₂ → salt cavern storage

## Cost
- **1-kW community kit**: $1,000 (**$1/W**)
- **100-MW urban node**: $40M (**$0.40/W**)

## Safety Certification
- Complies with **ICNIRP 2020**:
  - Power density < 10 W/kg SAR → **<1.6 kW/m² at 5.8 GHz**
  - Our limit: **1 kW/m²** → **safe for schools, hospitals, homes**