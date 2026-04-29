# main.py
#
#   Entry point for the LBO Return Simulator.
#   Imports the LBO model from lbo.py and the Monte Carlo simulation from monte_carlo.py.
#   Run this file to use the program: python main.py

from lbo         import get_inputs, project_financials, calculate_returns, sensitivity_analysis, export_to_csv
from monte_carlo import run_monte_carlo

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

    # NEW step 5: optional Monte Carlo simulation — run_monte_carlo() lives in monte_carlo.py
    print("  Run Monte Carlo simulation? (y/n): ", end="")
    if input().strip().lower() == "y":
        run_monte_carlo(inputs)

    # NEW step 6: optional CSV export — export_to_csv() lives in lbo.py
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
