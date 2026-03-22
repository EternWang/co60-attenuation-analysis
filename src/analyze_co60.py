"""Analyze Co-60 attenuation data for different source positions.

This script reproduces the core figures and regression results from the
experiment.

Inputs
------
- data/processed_points.csv
- data/raw_absorber_position_test.csv

Outputs
-------
- figures/nb_vs_z_by_slot.png
- figures/deltaZ_vs_nb.png
- figures/absorber_position_net_rates.png
- figures/regression_summary.txt
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
FIG_DIR = REPO_ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class FitResult:
    slope: float
    intercept: float
    r_value: float
    p_value: float
    std_err: float


def linear_fit(x: np.ndarray, y: np.ndarray) -> FitResult:
    res = stats.linregress(x, y)
    return FitResult(
        slope=float(res.slope),
        intercept=float(res.intercept),
        r_value=float(res.rvalue),
        p_value=float(res.pvalue),
        std_err=float(res.stderr),
    )


def main() -> None:
    processed = pd.read_csv(DATA_DIR / "processed_points.csv")

    slot3 = processed.loc[processed["source_position"] == "Slot 3"].copy()
    slot4 = processed.loc[processed["source_position"] == "Slot 4"].copy()

    fit3 = linear_fit(slot3["Z_mg_per_cm2"].to_numpy(), slot3["net_count_rate_cpm"].to_numpy())
    fit4 = linear_fit(slot4["Z_mg_per_cm2"].to_numpy(), slot4["net_count_rate_cpm"].to_numpy())

    nb_values = np.array([110, 120, 130, 140, 150], dtype=float)

    def inv_Z(fit: FitResult, nb: np.ndarray) -> np.ndarray:
        return (nb - fit.intercept) / fit.slope

    z3 = inv_Z(fit3, nb_values)
    z4 = inv_Z(fit4, nb_values)
    delta_z = z3 - z4

    fig1 = plt.figure(figsize=(10, 6))
    ax1 = fig1.add_subplot(111)

    for label, df in [("Slot 2", processed[processed["source_position"] == "Slot 2"]), ("Slot 3", slot3), ("Slot 4", slot4)]:
        ax1.scatter(df["Z_mg_per_cm2"], df["net_count_rate_cpm"], label=label)

    x_line = np.linspace(processed["Z_mg_per_cm2"].min() * 0.95, processed["Z_mg_per_cm2"].max() * 1.05, 200)
    ax1.plot(x_line, fit3.slope * x_line + fit3.intercept, linestyle="--", label="Slot 3 fit")
    ax1.plot(x_line, fit4.slope * x_line + fit4.intercept, linestyle="--", label="Slot 4 fit")

    ax1.set_title("Net count rate (N - B) vs absorber areal density")
    ax1.set_xlabel("Absorber areal density Z (mg/cm^2)")
    ax1.set_ylabel("Net count rate (N - B) (counts/min)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    fig1.tight_layout()
    fig1.savefig(FIG_DIR / "nb_vs_z_by_slot.png", dpi=200)
    plt.close(fig1)

    fit_delta = linear_fit(nb_values, delta_z)

    fig2 = plt.figure(figsize=(8, 5))
    ax2 = fig2.add_subplot(111)
    ax2.scatter(nb_values, delta_z, label="Computed Delta Z")
    nb_line = np.linspace(nb_values.min() - 2, nb_values.max() + 2, 200)
    ax2.plot(nb_line, fit_delta.slope * nb_line + fit_delta.intercept, linestyle="--", label="Linear fit")
    ax2.set_title("Extra absorber thickness needed when moving source (Slot 4 -> Slot 3)")
    ax2.set_xlabel("Target net count rate (N - B) (counts/min)")
    ax2.set_ylabel("Delta Z (Slot 3 - Slot 4) (mg/cm^2)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(FIG_DIR / "deltaZ_vs_nb.png", dpi=200)
    plt.close(fig2)

    raw = pd.read_csv(DATA_DIR / "raw_absorber_position_test.csv")
    groups = [
        raw.loc[raw["absorber_position"] == "Slot 1", "net_count_rate_cpm"].to_numpy(),
        raw.loc[raw["absorber_position"] == "Slot 2", "net_count_rate_cpm"].to_numpy(),
        raw.loc[raw["absorber_position"] == "Slot 3", "net_count_rate_cpm"].to_numpy(),
    ]
    f_stat, p_anova = stats.f_oneway(*groups)

    fig3 = plt.figure(figsize=(8, 5))
    ax3 = fig3.add_subplot(111)
    order = ["Slot 1", "Slot 2", "Slot 3"]
    means = [raw.loc[raw["absorber_position"] == o, "net_count_rate_cpm"].mean() for o in order]
    sems = [raw.loc[raw["absorber_position"] == o, "net_count_rate_cpm"].sem() for o in order]
    ax3.errorbar(order, means, yerr=sems, fmt="o", capsize=4)
    ax3.set_title(f"Absorber position test (one-way ANOVA p = {p_anova:.3g})")
    ax3.set_xlabel("Absorber position")
    ax3.set_ylabel("Net count rate (N - B) (counts/min)")
    ax3.grid(True, alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(FIG_DIR / "absorber_position_net_rates.png", dpi=200)
    plt.close(fig3)

    summary_lines: list[str] = []
    summary_lines.append("Slot 3 fit: y = m x + b\n")
    summary_lines.append(f"  m = {fit3.slope:.8f} cpm/(mg/cm^2)\n")
    summary_lines.append(f"  b = {fit3.intercept:.5f} cpm\n")
    summary_lines.append(f"  r = {fit3.r_value:.6f}, p = {fit3.p_value:.3g}\n\n")

    summary_lines.append("Slot 4 fit: y = m x + b\n")
    summary_lines.append(f"  m = {fit4.slope:.8f} cpm/(mg/cm^2)\n")
    summary_lines.append(f"  b = {fit4.intercept:.5f} cpm\n")
    summary_lines.append(f"  r = {fit4.r_value:.6f}, p = {fit4.p_value:.3g}\n\n")

    summary_lines.append("Delta Z vs N-B (computed by inverting the two fits):\n")
    summary_lines.append(f"  Fit: Delta Z = {fit_delta.slope:.2f}*(N-B) + {fit_delta.intercept:.2f}  (mg/cm^2)\n")
    summary_lines.append(f"  p = {fit_delta.p_value:.3g}\n\n")

    summary_lines.append("Absorber-position one-way ANOVA on net count rate:\n")
    summary_lines.append(f"  F = {f_stat:.3f}, p = {p_anova:.3g}\n")

    (FIG_DIR / "regression_summary.txt").write_text("".join(summary_lines))


if __name__ == "__main__":
    main()
