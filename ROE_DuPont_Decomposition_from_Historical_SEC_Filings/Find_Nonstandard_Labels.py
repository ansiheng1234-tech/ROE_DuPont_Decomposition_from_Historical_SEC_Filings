from edgar import set_identity, Company

set_identity("YourOwnEmail@email.com")

'''
This script is a utility tool used in the ROE DuPont Decomposition project to inspect financial statement labels in SEC XBRL filings.

Because financial statement items often use inconsistent naming across companies and years (e.g., “Net income”, “Net earnings”, etc.), the main extraction program may occasionally fail to locate the correct label. 

This script is used to print all available income statement and balance sheet labels for a given company and fiscal year, allowing manual inspection of possible alternatives.

The script is intended only as a diagnostic tool when label matching fails.

The initial version of this script was generated with assistance from GPT and has been tested to work reliably for the purpose of label inspection.
'''

def print_statement_labels(ticker, year_choice):
    company = Company(ticker)

    filings = company.get_filings(form="10-K", amendments=False).head(12)

    found = False

    for filing in filings:
        filing_date = str(filing.filing_date)
        print(f"looking at file {filing_date}")

        xbrl = filing.xbrl()
        if xbrl is None:
            continue

        income_obj = xbrl.statements.income_statement()
        balance_obj = xbrl.statements.balance_sheet()

        if income_obj is None or balance_obj is None:
            continue

        income_stmt = income_obj.to_dataframe()
        balance_stmt = balance_obj.to_dataframe()

        # 防止 abstract / dimension 列不存在
        for col in ["abstract", "dimension"]:
            if col not in income_stmt.columns:
                income_stmt[col] = False
            if col not in balance_stmt.columns:
                balance_stmt[col] = False

        income_year_cols = [col for col in income_stmt.columns if str(year_choice) in str(col)]
        balance_year_cols = [col for col in balance_stmt.columns if str(year_choice) in str(col)]

        # 必须 income 和 balance 都有这个年份，才用这份 filing
        if len(income_year_cols) == 0 or len(balance_year_cols) == 0:
            continue

        found = True
        print("=" * 80)
        print(f"Ticker: {ticker}")
        print(f"Requested Fiscal Year: {year_choice}")
        print(f"Filing Date: {filing_date}")
        print("=" * 80)

        print("\n[DEBUG]")
        print("Income columns:")
        print(income_stmt.columns.tolist())
        print("\nIncome year cols:")
        print(income_year_cols)

        print("\nBalance columns:")
        print(balance_stmt.columns.tolist())
        print("\nBalance year cols:")
        print(balance_year_cols)

        print("\n" + "=" * 80)

        print("\n[Income Statement Labels]")
        if "label" in income_stmt.columns:
            year_col = income_year_cols[0]
            print(f"Using income year column: {year_col}")

            filtered = income_stmt.loc[
                income_stmt[year_col].notna()
                & (~income_stmt["abstract"].fillna(False))
                & (~income_stmt["dimension"].fillna(False)),
                "label"
            ]

            for i, label in enumerate(filtered.fillna("").astype(str).tolist(), 1):
                print(f"{i}. {label}")
        else:
            print("No 'label' column found in income statement.")

        print("\n" + "=" * 80)

        print("\n[Balance Sheet Labels]")
        if "label" in balance_stmt.columns:
            year_col = balance_year_cols[0]
            print(f"Using balance year column: {year_col}")

            filtered = balance_stmt.loc[
                balance_stmt[year_col].notna()
                & (~balance_stmt["abstract"].fillna(False))
                & (~balance_stmt["dimension"].fillna(False)),
                "label"
            ]

            for i, label in enumerate(filtered.fillna("").astype(str).tolist(), 1):
                print(f"{i}. {label}")
        else:
            print("No 'label' column found in balance sheet.")

        print("\n" + "=" * 80)
        break

    if not found:
        print(f"No 10-K statement found for {ticker} with fiscal year {year_choice}.")

ticker = input("Enter ticker: ").strip().upper()
year_choice = int(input("Enter fiscal year: ").strip())

print_statement_labels(ticker, year_choice)