#!/usr/bin/env python3
"""
Beam Trace Simulation for Heliosphere ISH

Calculates beam divergence, spot size, and power density for Inner Solar Harvesters.
Validates safety against ICNIRP limits (1,000 W/m² at 5.8 GHz).

Usage: python sim/beam_trace.py --ish_power 1e10 --distance 1.5e11
"""

import argparse
import math

#: 5.8 GHz. Both constants are the ISH design point, not free parameters.
WAVELENGTH_M = 0.052
APERTURE_M = 1000.0

#: The exposure ceiling the safety verdict is measured against.
#:
#: The original comment called this "the ICNIRP limit at 5.8 GHz". ICNIRP's
#: published 2020 reference level for GENERAL PUBLIC exposure at that frequency
#: is far lower than 1,000 W/m², so this number wants confirming against the
#: standard before it appears in any filing. It is left as it was found and
#: flagged here rather than quietly changed: choosing an exposure limit is an
#: engineering and regulatory decision, not a typo fix.
SAFETY_LIMIT_WPM2 = 1000.0


def beam_geometry(ish_power_w: float, distance_m: float) -> dict:
    """
    The physics, as numbers, separately from the printing.

    Everything used to live inside `main` and reach the world only as formatted
    strings, so the only way to check the model was to parse its own output —
    and the printed spot diameter is rounded to whole kilometres, which reads as
    "0 km" for any spot under 500 m. A test written against that text measures
    the format string, not the beam.

    This makes the simulator usable from a sweep or a notebook as well.
    """
    if not math.isfinite(ish_power_w) or ish_power_w <= 0:
        raise ValueError(f"ISH power must be a positive number of watts, got {ish_power_w}")
    if not math.isfinite(distance_m) or distance_m <= 0:
        raise ValueError(f"Distance must be a positive number of metres, got {distance_m}")

    divergence_rad = 1.22 * WAVELENGTH_M / APERTURE_M
    spot_diameter_m = divergence_rad * distance_m
    spot_area_m2 = math.pi * (spot_diameter_m / 2.0) ** 2
    power_density_wpm2 = ish_power_w / spot_area_m2

    return {
        "ish_power_w": ish_power_w,
        "distance_m": distance_m,
        "wavelength_m": WAVELENGTH_M,
        "aperture_m": APERTURE_M,
        "divergence_rad": divergence_rad,
        "spot_diameter_m": spot_diameter_m,
        "spot_area_m2": spot_area_m2,
        "power_density_wpm2": power_density_wpm2,
        "safety_limit_wpm2": SAFETY_LIMIT_WPM2,
        "is_safe": power_density_wpm2 <= SAFETY_LIMIT_WPM2,
    }


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ish_power", type=float, required=True, help="ISH power in watts")
    parser.add_argument("--distance", type=float, required=True, help="Distance in meters")
    # `args` is PARSED, not used as-is. It was written `if args is None: args =
    # parser.parse_args()`, so a caller passing a list — which the parameter
    # exists for — had that list bound straight to `args`, and the next line
    # died with `'list' object has no attribute 'ish_power'`. argparse already
    # falls back to sys.argv when handed None, so the guard was doing nothing
    # except breaking the one case it was written for: programmatic use from a
    # test, a sweep or a notebook.
    args = parser.parse_args(args)

    g = beam_geometry(args.ish_power, args.distance)
    spot_km = g["spot_diameter_m"] / 1000.0

    print(f"ISH Power: {g['ish_power_w'] / 1e9:.1f} GW")
    print(f"Distance: {g['distance_m']:.1e} m")
    print(f"Wavelength: {g['wavelength_m']:.3f} m")
    print(f"Aperture: {g['aperture_m']:.0f} m")
    print(f"Beam divergence: {g['divergence_rad'] * 1e6:.1f} µrad ({math.degrees(g['divergence_rad']):.4f}°)")
    # Three decimals rather than none: `{:.0f} km` printed "0 km" for every spot
    # under 500 m, which is a readout saying the beam has no width while the
    # power density beside it is computed from the real one.
    print(f"Spot diameter: {spot_km:.3f} km ({g['spot_diameter_m']:.0f} m)")
    print(f"Power density: {g['power_density_wpm2']:.6f} W/m² ({g['power_density_wpm2'] * 1000:.3f} mW/m²)")
    print(f"{'✓ Within safety limits.' if g['is_safe'] else '⚠️ EXCEEDS SAFETY LIMIT!'}")
    return g


if __name__ == "__main__":
    main()
