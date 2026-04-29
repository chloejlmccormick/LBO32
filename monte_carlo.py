import random

# monte_carlo.py
#
#   Monte Carlo simulation for the LBO Return Simulator.
#   Imports run_model_silent() from lbo.py so the simulation uses exactly the same
#   financial logic as the main model — any change to the FCF formula in lbo.py
#   is automatically reflected here.
#
#   called from main.py via run_monte_carlo(inputs)

from lbo import run_model_silent, _get_float, _get_int


# run the model thousands of times with random draws for growth_rate, ebitda_margin,
# and exit_multiple from user-specified ranges to produce a distribution of outcomes
# rather than just point estimates — uses random.uniform() from Python's standard library
#
# calls run_model_silent() from lbo.py for each scenario so results stay fully
# consistent with the main model
#
# prints a text histogram of MOIC outcomes plus summary statistics:
# median MOIC, median IRR, P10/P25/P75/P90, % of scenarios >= 2x MOIC, >= 3x MOIC, IRR >= 20%

def monte_carlo(inputs, n_simulations=5000,
                growth_lo=0.05, growth_hi=0.20,
                margin_lo=None, margin_hi=None,
                exit_lo=6.0,    exit_hi=10.0):

    # default margin range to +/- 5pp around the base case if the user doesn't specify
    base_margin = inputs["ebitda_margin"]
    if margin_lo is None:
        margin_lo = max(0.01, base_margin - 0.05)
    if margin_hi is None:
        margin_hi = min(0.99, base_margin + 0.05)

    moics = []
    irrs  = []

    for _ in range(n_simulations):

        # swap in random assumptions for this scenario, leave everything else (debt, revenue, etc.) unchanged
        scenario = dict(inputs)
        scenario["growth_rate"]   = random.uniform(growth_lo, growth_hi)
        scenario["ebitda_margin"] = random.uniform(margin_lo, margin_hi)
        scenario["exit_multiple"] = random.uniform(exit_lo, exit_hi)

        final_ebitda, final_debt = run_model_silent(scenario)
        exit_val       = final_ebitda * scenario["exit_multiple"]
        equity_at_exit = exit_val - final_debt
        moic           = equity_at_exit / inputs["equity_invested"]

        # guard against negative moic before taking fractional exponent for IRR
        irr = (max(moic, 0.0001) ** (1 / inputs["holding_period"])) - 1

        moics.append(moic)
        irrs.append(irr)

    moics_sorted = sorted(moics)
    irrs_sorted  = sorted(irrs)

    def percentile(lst, p):
        return lst[int(len(lst) * p / 100)]

    # summary statistics — median, percentiles, and threshold pass rates
    median_moic     = percentile(moics_sorted, 50)
    median_irr      = percentile(irrs_sorted,  50)
    p10             = percentile(moics_sorted, 10)
    p25             = percentile(moics_sorted, 25)
    p75             = percentile(moics_sorted, 75)
    p90             = percentile(moics_sorted, 90)
    pct_above_2x    = sum(1 for m in moics if m >= 2.0) / n_simulations * 100
    pct_above_3x    = sum(1 for m in moics if m >= 3.0) / n_simulations * 100
    pct_irr_above20 = sum(1 for r in irrs  if r >= 0.20) / n_simulations * 100

    print()
    print(f"  MONTE CARLO SIMULATION — {n_simulations:,} runs")
    print(f"  Growth range:   {growth_lo:.0%} – {growth_hi:.0%}")
    print(f"  Margin range:   {margin_lo:.0%} – {margin_hi:.0%}")
    print(f"  Exit multiple:  {exit_lo:.1f}x – {exit_hi:.1f}x")
    print()
    print("  ── Summary Statistics ──────────────────────────")
    print(f"  Median MOIC:          {median_moic:.2f}x")
    print(f"  Median IRR:           {median_irr * 100:.1f}%")
    print(f"  P10 / P25 MOIC:       {p10:.2f}x  /  {p25:.2f}x")
    print(f"  P75 / P90 MOIC:       {p75:.2f}x  /  {p90:.2f}x")
    print(f"  Scenarios MOIC >= 2x: {pct_above_2x:.1f}%")
    print(f"  Scenarios MOIC >= 3x: {pct_above_3x:.1f}%")
    print(f"  Scenarios IRR  >= 20%:{pct_irr_above20:.1f}%")
    print()

    # text histogram — scale bar length to the tallest bin so it always fits on screen
    n_bins = 20
    min_m  = moics_sorted[0]
    max_m  = moics_sorted[-1]
    bin_w  = (max_m - min_m) / n_bins if max_m > min_m else 1
    counts = [0] * n_bins
    for m in moics:
        idx = min(int((m - min_m) / bin_w), n_bins - 1)
        counts[idx] += 1
    max_count = max(counts)
    bar_scale = 40 / max_count if max_count > 0 else 1

    print("  ── MOIC Distribution ───────────────────────────")
    for i, count in enumerate(counts):
        lo_b = min_m + i * bin_w
        hi_b = lo_b + bin_w
        bar  = "█" * int(count * bar_scale)
        print(f"  {lo_b:5.2f}x–{hi_b:5.2f}x │{bar:<40}│ {count:>5}")
    print()

    return list(zip(moics, irrs))


# prompt the user for Monte Carlo parameters and run the simulation
# called from main.py so the input prompts live here rather than cluttering main

def run_monte_carlo(inputs):
    n         = _get_int(  "  Number of simulations (e.g. 5000):     ", min_val=100, max_val=100000)
    growth_lo = _get_float("  Growth rate lower bound (e.g. 0.05):   ", min_val=0.0, max_val=1.0, allow_zero=True)
    growth_hi = _get_float("  Growth rate upper bound (e.g. 0.20):   ", min_val=0.0, max_val=1.0, allow_zero=True)
    exit_lo   = _get_float("  Exit multiple lower bound (e.g. 6.0):  ", min_val=0.1)
    exit_hi   = _get_float("  Exit multiple upper bound (e.g. 10.0): ", min_val=0.1)
    monte_carlo(inputs, n_simulations=n,
                growth_lo=growth_lo, growth_hi=growth_hi,
                exit_lo=exit_lo,     exit_hi=exit_hi)
