# LBO32
Chloe McCormick, Nathan Robasciotti, and Anthony Wang's CS32 FP

# LBO Return Simulator
 
A terminal based financial model that simulates the returns of a leveraged buyout (LBO) usually acquired from an excel spreadsheet. The user inputs deal assumptions and the model projects year-by-year financials, calculates investor returns, runs a sensitivity analysis across different growth and exit scenarios, and optionally runs a Monte Carlo simulation to produce a distribution of outcomes.
 
---
 
## What It Does
 
The simulator walks through six steps:
 
1. **Input collection:** prompts the user for deal assumptions (purchase price, equity invested, revenue, margins, growth rate, interest rate, tax rate, capex, debt amortization, exit multiple, and holding period). Inputs are fully validated: non-numeric entries, negative values, and financially unreasonable combinations (e.g. equity ≥ purchase price, margin + capex ≥ 100%) are caught with a re-prompt rather than a crash
2. **Financial projection:** models the company year by year, computing EBITDA, interest, taxes, capex, free cash flow, and debt paydown. Flags a warning if free cash flow falls short of the scheduled debt amortization payment (potential covenant breach)
3. **Returns summary:** calculates exit enterprise value, equity value at exit, MOIC (multiple on invested capital), and IRR (internal rate of return)
4. **Sensitivity analysis:** prints a grid of MOIC outcomes across a range of revenue growth rates and exit multiples, stress-testing the base case assumptions
5. **Monte Carlo simulation** *(optional)*: runs the model thousands of times with random draws for growth rate, EBITDA margin, and exit multiple across user-specified ranges. Prints a text histogram of MOIC outcomes and summary statistics: median MOIC, median IRR, P10/P25/P75/P90, and the percentage of scenarios where MOIC ≥ 2x, MOIC ≥ 3x, and IRR ≥ 20%
6. **CSV export** *(optional)*: writes the year-by-year projection table and sensitivity grid to a `.csv` file that can be opened directly in Excel

---
 
## File Structure

The project is split across three files:

- **`lbo.py`:** contains all core model logic: `get_inputs()`, `project_financials()`, `calculate_returns()`, `sensitivity_analysis()`, `run_model_silent()`, and `export_to_csv()`. Also contains the input validation helpers `_get_float()` and `_get_int()`
- **`monte_carlo.py`:** contains the Monte Carlo simulation. Imports `run_model_silent()` directly from `lbo.py` so the simulation always uses identical financial logic to the main model
- **`main.py`:** entry point. Imports from both `lbo.py` and `monte_carlo.py` and runs all six steps in order. This is the only file you need to run

---

## How to Run
 
No packages or special setup required. The project uses only Python's built-in standard library (`csv` and `random`).
 
**Requirements:** Python 3.x
 
**Steps:**
 
1. Make sure `main.py`, `lbo.py`, and `monte_carlo.py` are all saved in the same folder on your machine
2. Open a terminal and navigate to that folder
3. Run:
```
python main.py
```
 
4. Enter your deal assumptions when prompted. Example inputs for a realistic mid-market LBO:
| Prompt | Example Value |
| --- | --- |
| Purchase Price ($M) | 100 |
| Equity Invested ($M) | 40 |
| Starting Revenue ($M) | 50 |
| EBITDA Margin | 0.25 |
| Revenue Growth Rate | 0.10 |
| Interest Rate | 0.08 |
| Exit EV/EBITDA Multiple | 8 |
| Holding Period (years) | 5 |
| Tax Rate | 0.25 |
| CapEx as % of Revenue | 0.03 |
| Annual Debt Amortization ($M) | 4 |

5. After the sensitivity analysis, you will be prompted whether to run the Monte Carlo simulation and whether to export results to CSV. Both are optional: press `n` to skip either.

---
 
## Key Concepts and Formulas
 
The financial logic is based on standard LBO modeling conventions:
 
- **EBITDA** = Revenue × EBITDA Margin
- **Taxes** = max((EBITDA − Interest) × Tax Rate, 0): interest is tax-deductible; no negative tax bill
- **CapEx** = Revenue × CapEx %: scales with the business each year
- **Free Cash Flow** = EBITDA − Interest − Taxes − CapEx
- **Exit Enterprise Value** = Final Year EBITDA × Exit Multiple
- **Equity at Exit** = Exit EV − Remaining Debt
- **MOIC** = Equity at Exit / Equity Invested
- **IRR** = MOIC^(1 / Holding Period) − 1
- **Monte Carlo IRR** = same formula applied to each simulated scenario; MOIC floored at 0.0001 before taking the exponent to avoid math errors on loss scenarios

For background on these concepts:
- [Investopedia - Leveraged Buyout (LBO)](https://www.investopedia.com/terms/l/leveragedbuyout.asp)
- [Investopedia - Multiple on Invested Capital (MOIC)](https://www.investopedia.com/terms/m/moic.asp)
- [Investopedia - Internal Rate of Return (IRR)](https://www.investopedia.com/terms/i/irr.asp)
- [Investopedia - Free Cash Flow](https://www.investopedia.com/terms/f/freecashflow.asp)
- [Investopedia - Debt Covenant](https://www.investopedia.com/terms/d/debtcovenant.asp)
For LBO modeling structure and logic:
- [Wall Street Prep - Basics of an LBO Model](https://www.wallstreetprep.com/knowledge/basics-of-an-lbo-model/): walkthrough of the five core steps of an LBO model (entry valuation, sources & uses, debt schedule, returns, sensitivity analysis)
- [Wall Street Prep - Simple LBO Model Tutorial](https://www.wallstreetprep.com/knowledge/financial-modeling-quick-lesson-simple-lbo-model/): video tutorial building a simple LBO from scratch, similar structure to our project
- [Breaking Into Wall Street - LBO Model Tutorials](https://breakingintowallstreet.com/kb/leveraged-buyouts-and-lbo-models/): covers IRR/MOIC calculations and debt repayment schedules
- [GitHub - JimCortes/LBO_Model](https://github.com/JimCortes/LBO_Model): a Python-based LBO model with sensitivity analysis, similar in scope to this project
For Python syntax used in this project:
- [Real Python - Dictionaries in Python](https://realpython.com/python-dicts/): reference for using dictionaries to store and pass structured data (used in `get_inputs()`)
- [W3Schools - Python For Loops](https://www.w3schools.com/python/python_for_loops.asp): reference for `for` loop and `range()` syntax (used in `project_financials()` and `run_model_silent()`)
- [Real Python - Python f-strings](https://realpython.com/python-f-strings/): reference for f-string formatting including column alignment with `:<` and `:>` (used in the output table)
- [Python Docs - csv module](https://docs.python.org/3/library/csv.html): reference for `csv.writer` and `csv.DictWriter` (used in `export_to_csv()`)
- [Python Docs - random module](https://docs.python.org/3/library/random.html): reference for `random.uniform()` (used in `monte_carlo()`)

---

## Testing

We verified the model is producing correct numbers in five ways:

1. **Manual verification:** ran a clean scenario ($100M purchase price, $50M equity, $50M debt, flat $10M EBITDA, 0% growth, no taxes, no capex, no amortization) and confirmed the debt balance in each year matched hand calculations
2. **Covenant breach edge case:** constructed a scenario with very high interest and capex that pushed FCF below the scheduled amortization payment and confirmed the warning printed correctly and the code used the scheduled payment rather than the insufficient FCF
3. **Final year paydown:** confirmed that when remaining debt is less than the scheduled amortization, the program caps the payment at actual remaining debt and does not produce a negative balance (the `min(annual_amort, debt)` line)
4. **Consistency check:** ran `project_financials()` and `run_model_silent()` side by side on five input sets and confirmed final EBITDA and final debt matched exactly each time — critical because the sensitivity analysis and Monte Carlo both depend on `run_model_silent()`
5. **IRR formula check:** verified that at 1.0x MOIC the IRR returns 0%, and at 2.0x over 5 years the IRR returns approximately 14.9%, matching the expected value of `2^(1/5) - 1`

---

## External Contributors and AI Use
 
**Generative AI:** We consulted Claude (Anthropic) as a reference tool while working through feedback from our TF on the second project milestone. Our TF asked us to add taxes and capital expenditures to the FCF calculation, replace the informal debt paydown logic with a proper amortization schedule, flag covenant breach scenarios, keep `run_model_silent()` in sync with `project_financials()`, add broader input validation with cross-input checks, implement a Monte Carlo simulation with summary statistics, add CSV export, and split the project into three files. We worked through these changes ourselves and used Claude to check our understanding of specific syntax questions. We reviewed, tested, and integrated all code ourselves.
 
The overall structure, functions, financial logic, and comments of the model were written by us.
