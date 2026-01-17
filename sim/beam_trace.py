#!/usr/bin/env python3
"""
Beam Trace Simulation for Heliosphere ISH

Calculates beam divergence, spot size, and power density for Inner Solar Harvesters.
Validates safety against ICNIRP limits (1,000 W/m² at 5.8 GHz).

Usage: python sim/beam_trace.py --ish_power 1e10 --distance 1.5e11
"""

import argparse
import math

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ish_power", type=float, required=True, help="ISH power in watts")
    parser.add_argument("--distance", type=float, required=True, help="Distance in meters")
    if args is None:
        args = parser.parse_args()

    # Constants
    wavelength_m = 0.052  # 5.8 GHz
    aperture_m = 1000.0   # ISH transmitter diameter
    safety_limit_wpm2 = 1000.0  # ICNIRP limit at 5.8 GHz

    # Calculations
    power_gw = args.ish_power / 1e9
    distance_sci = f"{args.distance:.1e}"
    
    # Beam divergence (radians)
    divergence_rad = 1.22 * wavelength_m / aperture_m
    divergence_urad = divergence_rad * 1e6
    divergence_deg = math.degrees(divergence_rad)
    
    # Spot diameter
    spot_diameter_m = divergence_rad * args.distance
    spot_diameter_km = spot_diameter_m / 1000.0
    
    # Power density (W/m²)
    spot_area_m2 = math.pi * (spot_diameter_m / 2.0)**2
    power_density_wpm2 = args.ish_power / spot_area_m2 if spot_area_m2 > 0 else 0.0
    
    # Safety check
    is_safe = power_density_wpm2 <= safety_limit_wpm2

    # Output
    print(f"ISH Power: {power_gw:.1f} GW")
    print(f"Distance: {distance_sci} m")
    print(f"Wavelength: {wavelength_m:.3f} m")
    print(f"Aperture: {aperture_m:.0f} m")
    print(f"Beam divergence: {divergence_urad:.1f} µrad ({divergence_deg:.4f}°)")
    print(f"Spot diameter: {spot_diameter_km:.0f} km")
    print(f"Power density: {power_density_wpm2:.6f} W/m² ({power_density_wpm2 * 1000:.3f} mW/m²)")
    print(f"{'✓ Within safety limits.' if is_safe else '⚠️ EXCEEDS SAFETY LIMIT!'}")

if __name__ == "__main__":
    main()