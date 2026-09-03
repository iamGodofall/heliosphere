"""
Smoke tests for the beam simulator — the first tests in this repository.

These exist because `make sim` never ran. The Makefile invoked
`python3 sim/beam_trace.py` with no arguments and the script requires
`--ish_power` and `--distance`, so the documented build command exited 2 and
`make all` failed with it. Nobody had seen this simulator's output.

Standard library only. Run: python3 -m unittest discover -s sim -p "test_*.py"
"""
import io
import math
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import beam_trace  # noqa: E402


def run(power, distance):
    out = io.StringIO()
    with redirect_stdout(out):
        beam_trace.main(["--ish_power", str(power), "--distance", str(distance)])
    return out.getvalue()


class TestItRunsAtAll(unittest.TestCase):
    def test_the_documented_design_point_produces_output(self):
        # 10 GW at the ISH, geostationary — docs/README.md's own figures.
        text = run(1e10, 3.5786e7)
        self.assertIn("ISH Power: 10.0 GW", text)
        self.assertIn("Power density:", text)

    def test_missing_arguments_are_an_error_rather_than_a_default(self):
        # The Makefile relied on there being defaults. There are none.
        with self.assertRaises(SystemExit):
            with redirect_stdout(io.StringIO()):
                beam_trace.main([])


class TestThePhysicsIsSelfConsistent(unittest.TestCase):
    def test_spot_diameter_grows_linearly_with_distance(self):
        # spot = 1.22 * lambda / aperture * distance, so doubling the distance
        # doubles the spot. Measured from `beam_geometry`, NOT from the printed
        # line: that is rounded, and the first version of this test read the
        # rounding rather than the beam and reported a ratio of 1.0.
        near = beam_trace.beam_geometry(1e10, 1e7)["spot_diameter_m"]
        far = beam_trace.beam_geometry(1e10, 2e7)["spot_diameter_m"]
        self.assertAlmostEqual(far / near, 2.0, places=6)

    def test_power_density_falls_with_the_square_of_distance(self):
        near = beam_trace.beam_geometry(1e10, 1e7)["power_density_wpm2"]
        far = beam_trace.beam_geometry(1e10, 2e7)["power_density_wpm2"]
        self.assertAlmostEqual(near / far, 4.0, places=6)

    def test_a_sub_kilometre_spot_is_not_printed_as_zero(self):
        # `Spot diameter: {:.0f} km` printed "0 km" for anything under 500 m
        # while the power density beside it used the true value.
        text = run(1e10, 4e5)          # a 25 m spot
        line = next(l for l in text.splitlines() if l.startswith("Spot diameter:"))
        self.assertNotIn("0.000 km (0 m)", line)
        self.assertIn(" m)", line)

    def test_a_non_positive_input_is_refused(self):
        for power, distance in ((0, 1e7), (-1, 1e7), (1e10, 0), (1e10, -5),
                                (float("nan"), 1e7), (1e10, float("inf"))):
            with self.assertRaises(ValueError):
                beam_trace.beam_geometry(power, distance)

    def test_divergence_matches_the_diffraction_limit(self):
        # 1.22 * 0.052 m / 1000 m = 63.4 microradians.
        text = run(1e10, 3.5786e7)
        line = next(l for l in text.splitlines() if l.startswith("Beam divergence:"))
        urad = float(line.split(":")[1].strip().split()[0])
        self.assertAlmostEqual(urad, 1.22 * 0.052 / 1000.0 * 1e6, places=1)


class TestTheSafetyVerdict(unittest.TestCase):
    def test_the_documented_design_point_exceeds_the_limit_the_code_uses(self):
        # This is the finding, pinned so it cannot be lost: at 10 GW to GEO the
        # simulator reports about 2,470 W/m² against its own 1,000 W/m² constant.
        # The repository's own tool says its own headline design point is unsafe,
        # and no one had run it.
        self.assertIn("EXCEEDS SAFETY LIMIT", run(1e10, 3.5786e7))

    def test_a_low_enough_power_is_reported_as_safe(self):
        # The control. Without it the assertion above is satisfied by a tool that
        # always says "unsafe".
        self.assertIn("Within safety limits", run(1e9, 3.5786e7))

    def test_the_safety_constant_is_the_one_the_code_documents(self):
        # Guards the constant itself. The comment calls 1,000 W/m² "the ICNIRP
        # limit at 5.8 GHz"; ICNIRP's published 2020 reference level for general
        # public exposure at that frequency is far lower. Worth confirming
        # against the standard before this number is used in a filing — flagged
        # here rather than silently changed, because picking a limit is an
        # engineering decision, not a typo fix.
        src = (Path(__file__).parent / "beam_trace.py").read_text()
        self.assertIn("SAFETY_LIMIT_WPM2 = 1000.0", src)
        self.assertEqual(beam_trace.SAFETY_LIMIT_WPM2, 1000.0)


if __name__ == "__main__":
    unittest.main()
