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
    purchase_price   = float(input("Purchase Price ($M):             "))

    # ask how much of that came from the PE firm's own pocket
    # (the rest is assumed to be debt / borrowed money)
    equity_invested  = float(input("Equity Invested ($M):            "))

    # ask what the company's revenue is at the start (year 0)
    revenue          = float(input("Starting Revenue ($M):           "))

    # EBITDA margin = what fraction of revenue turns into profit
    # e.g. 0.25 means 25 cents of every dollar of revenue is profit
    ebitda_margin    = float(input("EBITDA Margin (e.g. 0.25):       "))

    # how fast do we expect revenue to grow each year?
    # e.g. 0.10 means 10% growth per year
    growth_rate      = float(input("Revenue Growth Rate (e.g. 0.10): "))

    # what interest rate are we paying on our debt each year?
    interest_rate    = float(input("Interest Rate (e.g. 0.08):       "))

    # when we sell the company, what multiple of EBITDA will we get?
    # e.g. 8x means the buyer pays 8 times the company's annual profit
    exit_multiple    = float(input("Exit EV/EBITDA Multiple:         "))

    # how many years are we planning to hold this investment?
    holding_period   = int(input(  "Holding Period (years):          "))

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
    }

# Project financial year by year

# Get starting values and print header
# For each year:
#   grow revenue
#   compute EBITDA, interest, and FCF
#   pay down debt with positive FCF, capped at remaining debt
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

    # print a nice header so the table is easy to read
    print()
    print("-" * 65)
    print(f"{'Year':<6} {'Revenue':>10} {'EBITDA':>10} {'Interest':>10} {'Debt Paid':>10} {'Debt Left':>10}")
    print("-" * 65)

    # this is the main loop — we run through each year one at a time
    # range(1, years + 1) gives us [1, 2, 3, 4, 5] for a 5-year hold
    for year in range(1, years + 1):

        # revenue growth
        # each year, revenue goes up by the growth rate (e.g. if revenue was $20M and growth is 10%, now it's $22M)
        revenue = revenue * (1 + growth_rate)

        # EBITDA
        # multiply revenue by the margin (e.g. $22M revenue * 25% margin = $5.5M EBITDA)
        ebitda = revenue * ebitda_margin

        # Intrest Payment
        # every year we owe interest on however much debt is still outstanding ($60M of debt at 8% interest = $4.8M interest bill)
        interest = debt * interest_rate

        # Free cash flow: after paying interest, profit left (ignoring taxes and capex for now)
        free_cash_flow = ebitda - interest

        # Debt Paydown
        # if we made money this year (positive cash flow), use it to pay debt, if we didn't make money, we can't pay anything down
        if free_cash_flow > 0:
            debt_paid = min(free_cash_flow, debt)
        else:
            debt_paid = 0

        # reduce the outstanding debt by however much we just paid
        debt = debt - debt_paid

        # print all the numbers for this year in a nicely formatted row
        print(f"{year:<6} {revenue:>10.2f} {ebitda:>10.2f} {interest:>10.2f} {debt_paid:>10.2f} {debt:>10.2f}")

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

#   Same logic as project_financials() but with all the print statements removed

#   Sensitivity_analysis() calls this once per scenario and we don't want 20 tables on the screen, just the final numbers
#   pull the inputs, loop through the years, do the same math,n return final EBITDA and remaining debt at the end

def run_model_silent(inputs):

    # pull values out of the inputs dictionary, same as project_financials()
    revenue       = inputs["revenue"]
    debt          = inputs["debt"]
    growth_rate   = inputs["growth_rate"]
    ebitda_margin = inputs["ebitda_margin"]
    interest_rate = inputs["interest_rate"]
    years         = inputs["holding_period"]

    # same loop as before, grow revenue, calculate EBITDA, pay interest, pay down debt, just no printing this time
    for year in range(1, years + 1):

        revenue        = revenue * (1 + growth_rate)
        ebitda         = revenue * ebitda_margin
        interest       = debt * interest_rate
        free_cash_flow = ebitda - interest

        if free_cash_flow > 0:
            debt_paid = min(free_cash_flow, debt)
        else:
            debt_paid = 0

        debt = debt - debt_paid

    # calculate and return the final year's numbers
    final_ebitda = revenue * ebitda_margin
    final_debt   = debt

    return final_ebitda, final_debt

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

if __name__ == "__main__":
    main()
