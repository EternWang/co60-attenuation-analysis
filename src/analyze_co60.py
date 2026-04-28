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
BLUE = "#2F6B9A"
ORANGE = "#D97935"
GREEN = "#5B8C5A"
RED = "#B4554B"
GRAY = "#4A5568"
LIGHT = "#EEF2F6"


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


def set_plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 240,
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#D9DEE7",
            "grid.linewidth": 0.8,
            "grid.alpha": 0.75,
            "legend.frameon": False,
        }
    )


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    set_plot_style()
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

    fig1 = plt.figure(figsize=(8.2, 5.0))
    ax1 = fig1.add_subplot(111)

    palette = {"Slot 2": GRAY, "Slot 3": BLUE, "Slot 4": ORANGE}
    for label, df in [
        ("Slot 2", processed[processed["source_position"] == "Slot 2"]),
        ("Slot 3", slot3),
        ("Slot 4", slot4),
    ]:
        ax1.scatter(
            df["Z_mg_per_cm2"],
            df["net_count_rate_cpm"],
            label=label,
            s=46,
            color=palette[label],
            edgecolor="white",
            linewidth=0.6,
            alpha=0.92,
        )

    x_line = np.linspace(processed["Z_mg_per_cm2"].min() * 0.95, processed["Z_mg_per_cm2"].max() * 1.05, 200)
    ax1.plot(x_line, fit3.slope * x_line + fit3.intercept, color=BLUE, lw=2.1, label="Slot 3 fit")
    ax1.plot(x_line, fit4.slope * x_line + fit4.intercept, color=ORANGE, lw=2.1, label="Slot 4 fit")

    ax1.set_title("Co-60 attenuation by source position")
    ax1.set_xlabel("Absorber areal density Z (mg/cm^2)")
    ax1.set_ylabel("Net count rate N - B (counts/min)")
    ax1.text(
        0.03,
        0.06,
        f"Slot 3: slope {fit3.slope:.4f} cpm/(mg/cm^2)\n"
        f"Slot 4: slope {fit4.slope:.4f} cpm/(mg/cm^2)",
        transform=ax1.transAxes,
        ha="left",
        va="bottom",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": LIGHT, "edgecolor": "#CBD5E1"},
    )
    ax1.legend(ncol=2, loc="upper right")

    save_figure(fig1, FIG_DIR / "nb_vs_z_by_slot.png")

    fit_delta = linear_fit(nb_values, delta_z)

    fig2 = plt.figure(figsize=(7.5, 4.6))
    ax2 = fig2.add_subplot(111)
    ax2.scatter(nb_values, delta_z, label="Computed from inverted fits", s=54, color=BLUE, edgecolor="white", linewidth=0.7)
    nb_line = np.linspace(nb_values.min() - 2, nb_values.max() + 2, 200)
    ax2.plot(nb_line, fit_delta.slope * nb_line + fit_delta.intercept, color=ORANGE, lw=2.2, label="Linear summary")
    ax2.set_title("Equivalent absorber change at fixed count rate")
    ax2.set_xlabel("Target net count rate N - B (counts/min)")
    ax2.set_ylabel("Delta Z, Slot 3 - Slot 4 (mg/cm^2)")
    ax2.text(
        0.03,
        0.94,
        f"Delta Z = {fit_delta.slope:.1f}(N-B) + {fit_delta.intercept:.0f}",
        transform=ax2.transAxes,
        ha="left",
        va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": LIGHT, "edgecolor": "#CBD5E1"},
    )
    ax2.legend(loc="lower right")
    save_figure(fig2, FIG_DIR / "deltaZ_vs_nb.png")

    raw = pd.read_csv(DATA_DIR / "raw_absorber_position_test.csv")
    groups = [
        raw.loc[raw["absorber_position"] == "Slot 1", "net_count_rate_cpm"].to_numpy(),
        raw.loc[raw["absorber_position"] == "Slot 2", "net_count_rate_cpm"].to_numpy(),
        raw.loc[raw["absorber_position"] == "Slot 3", "net_count_rate_cpm"].to_numpy(),
    ]
    f_stat, p_anova = stats.f_oneway(*groups)

    fig3 = plt.figure(figsize=(7.0, 4.3))
    ax3 = fig3.add_subplot(111)
    order = ["Slot 1", "Slot 2", "Slot 3"]
    means = [raw.loc[raw["absorber_position"] == o, "net_count_rate_cpm"].mean() for o in order]
    sems = [raw.loc[raw["absorber_position"] == o, "net_count_rate_cpm"].sem() for o in order]
    for idx, name in enumerate(order):
        vals = raw.loc[raw["absorber_position"] == name, "net_count_rate_cpm"].to_numpy()
        jitter = np.linspace(-0.055, 0.055, len(vals))
        ax3.scatter(np.full_like(vals, idx, dtype=float) + jitter, vals, s=26, color="#94A3B8", alpha=0.75, zorder=2)
    ax3.errorbar(range(len(order)), means, yerr=sems, fmt="o", color=BLUE, ecolor=BLUE, capsize=5, ms=7, zorder=3)
    ax3.set_xticks(range(len(order)), order)
    ax3.set_title("Negative control: absorber position")
    ax3.set_xlabel("Absorber position")
    ax3.set_ylabel("Net count rate N - B (counts/min)")
    ax3.text(
        0.03,
        0.95,
        f"One-way ANOVA p = {p_anova:.2f}\nNo detectable position effect",
        transform=ax3.transAxes,
        ha="left",
        va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": LIGHT, "edgecolor": "#CBD5E1"},
    )
    save_figure(fig3, FIG_DIR / "absorber_position_net_rates.png")

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
