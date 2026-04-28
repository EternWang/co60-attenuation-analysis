from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Co60SmokeTest(unittest.TestCase):
    def test_rebuilds_figures_and_regression_summary(self) -> None:
        subprocess.run(
            [sys.executable, "src/analyze_co60.py"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        expected = [
            ROOT / "figures" / "nb_vs_z_by_slot.png",
            ROOT / "figures" / "deltaZ_vs_nb.png",
            ROOT / "figures" / "absorber_position_net_rates.png",
            ROOT / "assets" / "co60_decay_scheme.png",
        ]
        for path in expected:
            self.assertGreater(path.stat().st_size, 0, path.as_posix())

        summary = (ROOT / "figures" / "regression_summary.txt").read_text(encoding="utf-8")
        self.assertIn("+/-", summary)
        self.assertIn("ANOVA", summary)
        self.assertIn("p = 0.7", summary)


if __name__ == "__main__":
    unittest.main()
