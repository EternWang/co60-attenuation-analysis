# Co-60 attenuation analysis: source position and absorber thickness

This repository analyzes a Co-60 counting experiment with a Geiger-Muller detector. The central question is how much additional absorber thickness is required to keep the net count rate fixed when the source position changes.

## What This Demonstrates

This project emphasizes transparent modeling choices: background subtraction, restricted
fit ranges, regression inversion, a control test, and generated figures. I use it as a
compact example of how I document quantitative assumptions so that another researcher
can rerun the analysis and inspect where each number came from.

## At a Glance

- **Data workflow:** count-rate measurements, absorber metadata, and control-test data
  are turned into regression figures and a compact quantitative summary.
- **Methods signal:** background subtraction, fit-range restrictions, regression
  inversion, and an explicit negative-control check.
- **Reproducibility signal:** a short Python script rebuilds the figures and regression
  summary from the committed data tables.
- **Transferable skill:** the project demonstrates defensible modeling choices, clear
  assumptions, and robustness checks, all central to empirical research design.

## Analysis question

For a target background-subtracted net count rate, how does the required absorber areal density change when the source moves from one slot to another?

## Method

1. Use background-subtracted count rates for several absorber stacks and source positions.
2. Restrict the fit to the gamma-dominated region where beta contributions are negligible.
3. Fit net count rate versus areal density for the relevant source slots.
4. Invert the fitted lines to compute the equivalent thickness difference `Delta Z` at fixed net count rate.
5. Run a control test to check whether absorber position alone changes the net rate at fixed areal density.

## Key figures

**Net count rate versus absorber thickness**

![N-B vs Z](figures/nb_vs_z_by_slot.png)

**Equivalent thickness change when moving the source**

![Delta Z vs N-B](figures/deltaZ_vs_nb.png)

**Control test: absorber position**

![Absorber position test](figures/absorber_position_net_rates.png)

## Main quantitative results

- Slot 3 fit: `(N - B) = -0.00857 * Z + 263.00`
- Slot 4 fit: `(N - B) = -0.00595 * Z + 177.95`
- Approximate mapping over the operating region:
  `Delta Z ~= 51.38 * (N - B) + 781` `mg/cm^2`
- At `N - B = 130 cpm`, moving from Slot 4 to Slot 3 requires about `7.46e3 mg/cm^2` of additional absorber.
- One-way ANOVA for absorber position gives `p ~= 0.70`, so no statistically significant position effect was detected at fixed areal density.

## Reproduce

```bash
python -m venv .venv
pip install -r requirements.txt
python src/analyze_co60.py
```

Outputs are written to `figures/`.

## Repository structure

```text
data/     Processed attenuation points and raw control-test data
src/      Python analysis script
figures/  Generated plots and regression summary
report/   Technical report
summary/  One-page non-technical summary
assets/   Apparatus photo and decay scheme
```

## Writing sample

- Technical report: `report/report.pdf`
- One-page summary: `summary/one_page_summary.pdf`
