# LBO32
Chloe McCormick, Nathan Robasciotti, and Anthony Wang's CS32 FP

# LBO Return Simulator
 
A terminal based financial model that simulates the returns of a leveraged buyout (LBO) usually acquired from an excel spreadsheet. The user inputs deal assumptions and the model projects year-by-year financials, calculates investor returns, and runs a sensitivity analysis across different growth and exit scenarios.
 
---
 
## What It Does
 
The simulator walks through four steps:
 
1. **Input collection** — prompts the user for deal assumptions (purchase price, equity invested, revenue, margins, growth rate, interest rate, tax rate, capex, debt amortization, exit multiple, and holding period)
2. **Financial projection** — models the company year by year, computing EBITDA, interest, taxes, capex, free cash flow, and debt paydown. Flags a warning if free cash flow falls short of the scheduled debt amortization payment (potential covenant breach)
3. **Returns summary** — calculates exit enterprise value, equity value at exit, MOIC (multiple on invested capital), and IRR (internal rate of return)
4. **Sensitivity analysis** — prints a grid of MOIC outcomes across a range of revenue growth rates and exit multiples, stress-testing the base case assumptions
---
 
## How to Run
 
No packages or special setup required. The project uses only Python's built-in standard library.
 
**Requirements:** Python 3.x
 
**Steps:**
 
1. Make sure `main.py` is saved locally on your machine
2. Open a terminal and navigate to the folder containing `main.py`
3. Run:
```
python main.py
```
 
4. Enter your deal assumptions when prompted. Example inputs for a realistic mid-market LBO:
| Prompt, Example Value |
| Purchase Price ($M), 100
| Equity Invested ($M), 40
| Starting Revenue ($M), 50
| EBITDA Margin, 0.25
| Revenue Growth Rate, 0.10
| Interest Rate, 0.08
| Exit EV/EBITDA Multiple, 8
| Holding Period (years), 5
| Tax Rate, 0.25
| CapEx as % of Revenue, 0.03
| Annual Debt Amortization ($M), 4 |
 
---
 
## Key Concepts and Formulas
 
The financial logic is based on standard LBO modeling conventions:
 
- **EBITDA** = Revenue × EBITDA Margin
- **Taxes** = max((EBITDA − Interest) × Tax Rate, 0) — interest is tax-deductible; no negative tax bill
- **CapEx** = Revenue × CapEx % — scales with the business each year
- **Free Cash Flow** = EBITDA − Interest − Taxes − CapEx
- **Exit Enterprise Value** = Final Year EBITDA × Exit Multiple
- **Equity at Exit** = Exit EV − Remaining Debt
- **MOIC** = Equity at Exit / Equity Invested
- **IRR** = MOIC^(1 / Holding Period) − 1
For background on these concepts:
- [Investopedia — Leveraged Buyout (LBO)](https://www.investopedia.com/terms/l/leveragedbuyout.asp)
- [Investopedia — Multiple on Invested Capital (MOIC)](https://www.investopedia.com/terms/m/moic.asp)
- [Investopedia — Internal Rate of Return (IRR)](https://www.investopedia.com/terms/i/irr.asp)
- [Investopedia — Free Cash Flow](https://www.investopedia.com/terms/f/freecashflow.asp)
- [Investopedia — Debt Covenant](https://www.investopedia.com/terms/d/debtcovenant.asp)
For LBO modeling structure and logic:
- [Wall Street Prep — Basics of an LBO Model](https://www.wallstreetprep.com/knowledge/basics-of-an-lbo-model/) — walkthrough of the five core steps of an LBO model (entry valuation, sources & uses, debt schedule, returns, sensitivity analysis)
- [Wall Street Prep — Simple LBO Model Tutorial](https://www.wallstreetprep.com/knowledge/financial-modeling-quick-lesson-simple-lbo-model/) — video tutorial building a simple LBO from scratch, similar structure to our project
- [Breaking Into Wall Street — LBO Model Tutorials](https://breakingintowallstreet.com/kb/leveraged-buyouts-and-lbo-models/) — covers IRR/MOIC calculations and debt repayment schedules
- [GitHub — JimCortes/LBO_Model](https://github.com/JimCortes/LBO_Model) — a Python-based LBO model with sensitivity analysis, similar in scope to this project
For Python syntax used in this project:
- [Real Python — Dictionaries in Python](https://realpython.com/python-dicts/) — reference for using dictionaries to store and pass structured data (used in `get_inputs()`)
- [W3Schools — Python For Loops](https://www.w3schools.com/python/python_for_loops.asp) — reference for `for` loop and `range()` syntax (used in `project_financials()` and `run_model_silent()`)
- [Real Python — Python f-strings](https://realpython.com/python-f-strings/) — reference for f-string formatting including column alignment with `:<` and `:>` (used in the output table)
---
 
## External Contributors and AI Use
 
**Generative AI:** We used Claude (Anthropic) to help implement feedback provided by our TF on the second project milestone. Specifically, our TF asked us to:
- Add taxes and capital expenditures to the free cash flow calculation
- Replace the informal "pay whatever FCF allows" debt paydown with a proper amortization schedule
- Flag a warning when free cash flow falls short of the scheduled amortization payment (covenant breach scenario)
- Ensure `run_model_silent()` stays in sync with `project_financials()` so the sensitivity grid and year-by-year table use identical logic
We described the feedback to Claude and used it to implement those changes in `main.py`. We reviewed all of the code it produced, verified that it matched our TF's instructions, and tested it with sample inputs. The overall structure, original functions, comments, and financial logic of the model were written by us.
 
**No other external code sources were used.** The financial formulas are standard LBO modeling conventions referenced from Investopedia (linked above).

