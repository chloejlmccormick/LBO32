import csv
import random

# NEW: _get_float and _get_int are helper functions for validated input.
# They replace the bare float(input(...)) and int(input(...)) calls in get_inputs()
# so that non-numeric entries, negatives, and out-of-range values are caught cleanly
# with a re-prompt loop instead of crashing.

def _get_float(prompt, min_val=None, max_val=None, allow_zero=False):
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
        except ValueError:
            print("  ✗  Please enter a number (e.g. 0.25 or 100).")
            continue
        if not allow_zero and val == 0:
            print("  ✗  Value cannot be zero.")
            continue
        if min_val is not None and val < min_val:
            print(f"  ✗  Must be at least {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"  ✗  Must be at most {max_val}.")
            continue
        return val

def _get_int(prompt, min_val=1, max_val=50):
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw)
        except ValueError:
            print("  ✗  Please enter a whole number.")
            continue
        if val < min_val or val > max_val:
            print(f"  ✗  Must be between {min_val} and {max_val}.")
            continue
        return val


#  LBO Return Simulator
# first get inputs from user

#   ask the user a series of questions about the deal
#   store each answer in a variable
#   figure out how much debt was used (purchase price minus equity)
#   bundle everything up into a dictionary and return it

#   use a dictionary here because there are a lot of inputs and it's cleaner than passing 8 separate variables around to every function

def get_inputs():

    print("   Welcome to the LBO Return Simulator!")

    # ask the user what they paid for the company in total
    purchase_price   = _get_float("Purchase Price ($M):             ", min_val=0.01)  # NEW: was float(input(...))

    # ask how much of that came from the PE firm's own pocket
    # (the rest is assumed to be debt / borrowed money)
    equity_invested  = _get_float("Equity Invested ($M):            ", min_val=0.01)  # NEW: was float(input(...))

    # NEW: cross-input check — equity must be less than purchase price
    while equity_invested >= purchase_price:
        print(f"  ✗  Equity (${equity_invested:.2f}M) must be less than purchase price (${purchase_price:.2f}M).")
        equity_invested = _get_float("Equity Invested ($M):            ", min_val=0.01)

    # ask what the company's revenue is at the start (year 0)
    revenue          = _get_float("Starting Revenue ($M):           ", min_val=0.01)  # NEW: was float(input(...))

    # EBITDA margin = what fraction of revenue turns into profit
    # e.g. 0.25 means 25 cents of every dollar of revenue is profit
    ebitda_margin    = _get_float("EBITDA Margin (e.g. 0.25):       ", min_val=0.001, max_val=0.999)  # NEW: was float(input(...)), max_val guards against margin >= 100%

    # how fast do we expect revenue to grow each year?
    # e.g. 0.10 means 10% growth per year
    growth_rate      = _get_float("Revenue Growth Rate (e.g. 0.10): ", min_val=0.0, max_val=1.0, allow_zero=True)  # NEW: was float(input(...)), max_val=1.0 guards against e.g. typing 10 instead of 0.10

    # what interest rate are we paying on our debt each year?
    interest_rate    = _get_float("Interest Rate (e.g. 0.08):       ", min_val=0.0, max_val=1.0, allow_zero=True)  # NEW: was float(input(...))

    # when we sell the company, what multiple of EBITDA will we get?
    # e.g. 8x means the buyer pays 8 times the company's annual profit
    exit_multiple    = _get_float("Exit EV/EBITDA Multiple:         ", min_val=0.1)  # NEW: was float(input(...))

    # how many years are we planning to hold this investment?
    holding_period   = _get_int(  "Holding Period (years):          ", min_val=1, max_val=30)  # NEW: was int(input(...))

    # tax rate: fraction of pre-tax income (EBITDA - interest) owed to the government
    # e.g. 0.25 means we pay 25% of taxable income in taxes each year
    tax_rate         = _get_float("Tax Rate (e.g. 0.25):            ", min_val=0.0, max_val=0.99, allow_zero=True)  # NEW: was float(input(...))

    # capex as a percent of revenue: cash spent each year on maintaining/growing the asset base
    # e.g. 0.03 means we spend 3 cents of every revenue dollar on capex
    capex_pct        = _get_float("CapEx as % of Revenue (e.g. 0.03): ", min_val=0.0, max_val=0.99, allow_zero=True)  # NEW: was float(input(...))

    # annual debt amortization: the fixed principal repayment we are contractually
    # required to make each year regardless of how much cash we have
    # e.g. 5.0 means we must pay back $5M of loan principal every year
    annual_amort     = _get_float("Annual Debt Amortization ($M):   ", min_val=0.0, allow_zero=True)  # NEW: was float(input(...))

    # NEW: cross-input check — if margin + capex >= 100%, FCF will be negative before interest and taxes
    # a margin above 100% is technically a valid float but doesn't make financial sense (per professor feedback)
    if ebitda_margin + capex_pct >= 1.0:
        print(f"\n  ⚠️  WARNING: EBITDA margin ({ebitda_margin:.0%}) + CapEx % ({capex_pct:.0%}) >= 100%.")
        print("      Free cash flow will be negative before interest and taxes.")
        print("      Please verify your inputs — this combination is financially unusual.\n")

    # debt is just whatever we didn't pay with our own money
    # e.g. if we paid $100M and put in $40M ourselves, debt = $60M
    debt = purchase_price - equity_invested

    # put everything in a dictionary so it's easy to pass around
    return {
        "purchase_price":  purchase_price,
        "equity_invested": equity_invested,
        "debt":            debt,
        "revenue":         revenue,
        "ebitda_margin":   ebitda_margin,
        "growth_rate":     growth_rate,
        "interest_rate":   interest_rate,
        "exit_multiple":   exit_multiple,
        "holding_period":  holding_period,
        "tax_rate":        tax_rate,
        "capex_pct":       capex_pct,
        "annual_amort":    annual_amort,
    }

# Project financial year by year

# Get starting values and print header
# For each year:
#   grow revenue
#   compute EBITDA, interest, taxes, capex, and FCF
#   compare FCF to scheduled amortization — warn if FCF < amortization (potential covenant breach)
#   pay down debt: at least the scheduled amortization, sweep extra FCF to debt too
#   update debt and print results
# Return final EBITDA and remaining debt

def project_financials(inputs):

    # pull each value out of the dictionary so the math below is readable
    revenue       = inputs["revenue"]
    debt          = inputs["debt"]
    growth_rate   = inputs["growth_rate"]
    ebitda_margin = inputs["ebitda_margin"]
    interest_rate = inputs["interest_rate"]
    years         = inputs["holding_period"]
    tax_rate      = inputs["tax_rate"]
    capex_pct     = inputs["capex_pct"]
    annual_amort  = inputs["annual_amort"]

    # print a nice header so the table is easy to read
    print()
    print("-" * 91)
    print(f"{'Year':<6} {'Revenue':>10} {'EBITDA':>10} {'Interest':>10} {'Taxes':>10} {'CapEx':>10} {'FCF':>10} {'Debt Paid':>10} {'Debt Left':>10}")
    print("-" * 91)

    # this is the main loop — we run through each year one at a time
    # range(1, years + 1) gives us [1, 2, 3, 4, 5] for a 5-year hold
    for year in range(1, years + 1):

        # revenue growth
        # each year, revenue goes up by the growth rate (e.g. if revenue was $20M and growth is 10%, now it's $22M)
        revenue = revenue * (1 + growth_rate)

        # EBITDA
        # multiply revenue by the margin (e.g. $22M revenue * 25% margin = $5.5M EBITDA)
        ebitda = revenue * ebitda_margin

        # Interest Payment
        # every year we owe interest on however much debt is still outstanding ($60M of debt at 8% interest = $4.8M interest bill)
        interest = debt * interest_rate

        # Taxes
        # taxable income = EBITDA minus interest (interest is tax-deductible)
        # if taxable income is negative we owe $0 — no negative tax bill
        taxable_income = ebitda - interest
        taxes = max(taxable_income * tax_rate, 0)

        # CapEx
        # cash we must spend each year to maintain/grow the asset base; scales with revenue
        capex = revenue * capex_pct

        # Free Cash Flow
        # what's actually left after paying interest, taxes, and reinvesting in the business
        free_cash_flow = ebitda - interest - taxes - capex

        # Amortization Schedule & Covenant Breach Check
        # scheduled_payment is the contractual principal we must repay this year
        # cap it at remaining debt so we never "overpay" in the final year
        scheduled_payment = min(annual_amort, debt)

        # if FCF is less than the scheduled payment, we can't cover amortization from operations alone —
        # in a real deal this would trigger a covenant breach or require additional equity injection
        if free_cash_flow < scheduled_payment:
            print(f"  ⚠️  WARNING Year {year}: FCF (${free_cash_flow:.2f}M) < scheduled amortization (${scheduled_payment:.2f}M) — potential covenant breach")

        # Debt Paydown
        # we always make at least the scheduled amortization payment
        # if we have extra FCF beyond the scheduled payment, sweep it toward debt too
        if free_cash_flow > scheduled_payment:
            debt_paid = min(free_cash_flow, debt)
        else:
            debt_paid = scheduled_payment

        # reduce the outstanding debt by however much we just paid
        debt = debt - debt_paid

        # print all the numbers for this year in a nicely formatted row
        print(f"{year:<6} {revenue:>10.2f} {ebitda:>10.2f} {interest:>10.2f} {taxes:>10.2f} {capex:>10.2f} {free_cash_flow:>10.2f} {debt_paid:>10.2f} {debt:>10.2f}")

    # after the loop, calculate final EBITDA based on final year revenue (to figure out what company is worth when selling)
    final_ebitda = revenue * ebitda_margin
    final_debt   = debt

    # return both values so calculate_returns() can use them
    return final_ebitda, final_debt

# Calculate exit returns

# exit value = final EBITDA * exit multiple
# equity = exit value - remaining debt
# MOIC = equity / initial equity
# IRR = MOIC^(1 / years) - 1
# print summary
# return MOIC, IRR

def calculate_returns(inputs, final_ebitda, final_debt):

    # Exit value
    # when we sell the company, the buyer pays a multiple of annual EBITDA
    exit_value = final_ebitda * inputs["exit_multiple"]

    # Equity at exit
    # when the company sells, debt gets paid off first
    equity_at_exit = exit_value - final_debt

    # pull out the equity we originally put in and the holding period
    equity_in = inputs["equity_invested"]
    years     = inputs["holding_period"]

    # MOIC
    # "how many times did we multiply our money?" (1.0x means we broke even, 2.0x means we doubled our money, etc.)
    moic = equity_at_exit / equity_in

    # IRR
    # Tells us the annualized return of different lengths (3x in 3 years is better than a 3x in 7 years)
    irr = (moic ** (1 / years)) - 1

    # print a clean summary of all the key outputs
    print()
    print("           RETURNS SUMMARY")
    print(f"  Exit Enterprise Value:   ${exit_value:.2f}M")
    print(f"  Remaining Debt at Exit:  ${final_debt:.2f}M")
    print(f"  Equity Value at Exit:    ${equity_at_exit:.2f}M")
    print(f"  Equity Invested:         ${equity_in:.2f}M")
    print(f"  MOIC:                    {moic:.2f}x")
    print(f"  IRR:                     {irr * 100:.1f}%")

    return moic, irr

# Sensitivity analysis

# define growth rates and exit multiples
# print header (growth rates)

# for each exit multiple print row label
# for each growth rate update inputs for scenario
# run model (no output)
# compute MOIC
# print MOIC

# result: table of MOIC across scenarios

def sensitivity_analysis(inputs):

    print()
    print("  SENSITIVITY ANALYSIS — MOIC by Growth Rate & Exit Multiple")

    # these are all the scenarios we want to test
    growth_rates   = [0.05, 0.10, 0.15, 0.20]
    exit_multiples = [6, 7, 8, 9, 10]

    # print the top header row — growth rates go across the columns
    print(f"\n{'Growth →':>12}", end="")
    for g in growth_rates:
        print(f"  {int(g*100)}% growth", end="")
    print()

    # print a divider line under the header
    print(f"{'Exit ↓':>12}", end="")
    print("  " + "-" * (len(growth_rates) * 12))

    # outer loop: each exit multiple gets its own row in the table
    for em in exit_multiples:

        # print the row label (the exit multiple for this row)
        print(f"  {em}x exit  |", end="")

        # inner loop: each growth rate gets its own column within this row
        for g in growth_rates:

            # make a fresh copy of inputs so we don't overwrite then swap in this scenario's assumptions
            scenario = dict(inputs)
            scenario["growth_rate"]   = g
            scenario["exit_multiple"] = em

            # run the full model logic - get final EBITDA and remaining debt to calculate MOIC
            final_ebitda, final_debt = run_model_silent(scenario)

            # calculate what the company would sell for in this scenario
            exit_value = final_ebitda * em

            # equity value = sale price minus whatever debt is still left
            equity_at_exit = exit_value - final_debt

            # MOIC = how much we get back divided by how much we put in
            moic = equity_at_exit / scenario["equity_invested"]

            # print this cell's MOIC — end="" keeps us on the same line
            print(f"  {moic:.2f}x    ", end="")

        # after all columns are printed for this row, drop to the next line
        print()

    print()

# run model without printing

#   Same logic as project_financials() but with all the print statements removed.
#   IMPORTANT: must stay in sync with project_financials() — any change to the FCF
#   formula (taxes, capex, amort) must be mirrored here, otherwise the year-by-year
#   view and the sensitivity grid will produce inconsistent results.

#   sensitivity_analysis() calls this once per scenario and we don't want 20 tables on the screen, just the final numbers
#   pull the inputs, loop through the years, do the same math, return final EBITDA and remaining debt at the end

def run_model_silent(inputs):

    # pull values out of the inputs dictionary, same as project_financials()
    revenue       = inputs["revenue"]
    debt          = inputs["debt"]
    growth_rate   = inputs["growth_rate"]
    ebitda_margin = inputs["ebitda_margin"]
    interest_rate = inputs["interest_rate"]
    years         = inputs["holding_period"]
    tax_rate      = inputs["tax_rate"]
    capex_pct     = inputs["capex_pct"]
    annual_amort  = inputs["annual_amort"]

    # same loop as before, grow revenue, calculate EBITDA, pay interest, taxes, capex, pay down debt, just no printing this time
    for year in range(1, years + 1):

        revenue        = revenue * (1 + growth_rate)
        ebitda         = revenue * ebitda_margin
        interest       = debt * interest_rate
        taxable_income = ebitda - interest
        taxes          = max(taxable_income * tax_rate, 0)
        capex          = revenue * capex_pct
        free_cash_flow = ebitda - interest - taxes - capex

        # amortization schedule — same logic as project_financials (no warning printed here)
        scheduled_payment = min(annual_amort, debt)

        if free_cash_flow > scheduled_payment:
            debt_paid = min(free_cash_flow, debt)
        else:
            debt_paid = scheduled_payment

        debt = debt - debt_paid

    # calculate and return the final year's numbers
    final_ebitda = revenue * ebitda_margin
    final_debt   = debt

    return final_ebitda, final_debt


# NEW: Monte Carlo simulation
#
#   run the model thousands of times with random draws for growth_rate, ebitda_margin,
#   and exit_multiple from user-specified ranges to produce a distribution of outcomes
#   rather than just point estimates — uses random.uniform() from Python's standard library
#
#   calls run_model_silent() for each scenario so results stay fully consistent with the main model
#
#   prints a text histogram of MOIC outcomes plus summary statistics:
#   median MOIC, median IRR, P10/P25/P75/P90, % of scenarios >= 2x MOIC, >= 3x MOIC, IRR >= 20%

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


# NEW: CSV export
#
#   write the year-by-year projection table and the sensitivity grid to a single CSV file
#   using Python's built-in csv module — no external dependencies needed
#   the output file can be opened directly in Excel for further analysis

def export_to_csv(inputs, filename="lbo_output.csv"):

    # rebuild year-by-year rows — same math as project_financials(), no printing
    revenue       = inputs["revenue"]
    debt          = inputs["debt"]
    growth_rate   = inputs["growth_rate"]
    ebitda_margin = inputs["ebitda_margin"]
    interest_rate = inputs["interest_rate"]
    years         = inputs["holding_period"]
    tax_rate      = inputs["tax_rate"]
    capex_pct     = inputs["capex_pct"]
    annual_amort  = inputs["annual_amort"]

    proj_rows = []
    for year in range(1, years + 1):
        revenue        = revenue * (1 + growth_rate)
        ebitda         = revenue * ebitda_margin
        interest       = debt * interest_rate
        taxable_income = ebitda - interest
        taxes          = max(taxable_income * tax_rate, 0)
        capex          = revenue * capex_pct
        free_cash_flow = ebitda - interest - taxes - capex
        scheduled      = min(annual_amort, debt)
        debt_paid      = min(free_cash_flow, debt) if free_cash_flow > scheduled else scheduled
        debt           = debt - debt_paid

        # flag covenant breach years so they're easy to spot in Excel
        covenant_flag  = "YES" if free_cash_flow < scheduled else ""

        proj_rows.append({
            "Year":            year,
            "Revenue ($M)":    round(revenue, 2),
            "EBITDA ($M)":     round(ebitda, 2),
            "Interest ($M)":   round(interest, 2),
            "Taxes ($M)":      round(taxes, 2),
            "CapEx ($M)":      round(capex, 2),
            "FCF ($M)":        round(free_cash_flow, 2),
            "Debt Paid ($M)":  round(debt_paid, 2),
            "Debt Left ($M)":  round(debt, 2),
            "Covenant Breach": covenant_flag,
        })

    # rebuild sensitivity grid — same scenarios as sensitivity_analysis()
    growth_rates   = [0.05, 0.10, 0.15, 0.20]
    exit_multiples = [6, 7, 8, 9, 10]
    sens_rows = []
    for em in exit_multiples:
        sens_row = {"Exit Multiple": f"{em}x"}
        for g in growth_rates:
            scenario = dict(inputs)
            scenario["growth_rate"]   = g
            scenario["exit_multiple"] = em
            final_ebitda, final_debt = run_model_silent(scenario)
            exit_val = final_ebitda * em
            moic     = (exit_val - final_debt) / inputs["equity_invested"]
            sens_row[f"Growth {int(g*100)}%"] = round(moic, 2)
        sens_rows.append(sens_row)

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        # section 1: deal inputs so the file is self-contained
        writer.writerow(["LBO RETURN SIMULATOR — OUTPUT"])
        writer.writerow([])
        writer.writerow(["DEAL INPUTS"])
        for k, v in inputs.items():
            writer.writerow([k, v])
        writer.writerow([])

        # section 2: year-by-year projection
        writer.writerow(["YEAR-BY-YEAR PROJECTION"])
        proj_writer = csv.DictWriter(f, fieldnames=proj_rows[0].keys())
        proj_writer.writeheader()
        proj_writer.writerows(proj_rows)
        writer.writerow([])

        # section 3: sensitivity grid
        writer.writerow(["SENSITIVITY ANALYSIS — MOIC"])
        sens_writer = csv.DictWriter(f, fieldnames=sens_rows[0].keys())
        sens_writer.writeheader()
        sens_writer.writerows(sens_rows)

    print(f"  ✓  Results exported to '{filename}'")


# Main

# get inputs
# run financial projection
# calculate returns
# run sensitivity analysis

# __main__ makes sure this runs only when executed directly

def main():

    # step 1: ask the user for all the inputs we need to model the deal
    inputs = get_inputs()

    # step 2: project the company's financials year by year and print the table (returns final EBITDA/remaining debt so step 3 can use it)
    final_ebitda, final_debt = project_financials(inputs)

    # step 3: use the end-of-holding-period numbers to calculate investor returns
    calculate_returns(inputs, final_ebitda, final_debt)

    # step 4: sensitivity table to stress-test base case assumptions
    sensitivity_analysis(inputs)

    # NEW step 5: optional Monte Carlo simulation
    print("  Run Monte Carlo simulation? (y/n): ", end="")
    if input().strip().lower() == "y":
        n         = _get_int(  "  Number of simulations (e.g. 5000):     ", min_val=100, max_val=100000)
        growth_lo = _get_float("  Growth rate lower bound (e.g. 0.05):   ", min_val=0.0, max_val=1.0, allow_zero=True)
        growth_hi = _get_float("  Growth rate upper bound (e.g. 0.20):   ", min_val=0.0, max_val=1.0, allow_zero=True)
        exit_lo   = _get_float("  Exit multiple lower bound (e.g. 6.0):  ", min_val=0.1)
        exit_hi   = _get_float("  Exit multiple upper bound (e.g. 10.0): ", min_val=0.1)
        monte_carlo(inputs, n_simulations=n,
                    growth_lo=growth_lo, growth_hi=growth_hi,
                    exit_lo=exit_lo,     exit_hi=exit_hi)

    # NEW step 6: optional CSV export
    print("  Export results to CSV? (y/n): ", end="")
    if input().strip().lower() == "y":
        fname = input("  Filename (press Enter for 'lbo_output.csv'): ").strip()
        if not fname:
            fname = "lbo_output.csv"
        if not fname.endswith(".csv"):
            fname += ".csv"
        export_to_csv(inputs, fname)

if __name__ == "__main__":
    main()
