from edgar import set_identity, Company

set_identity("email@example.com")

def print_statement_labels(ticker, year_choice):
    company = Company(ticker)

    filings = company.get_filings(form="10-K")

    found = False

    for filing in filings:
        filing_date = str(filing.filing_date)

        xbrl = filing.xbrl()
        if xbrl is None:
            continue

        income_stmt = xbrl.statements.income_statement().to_dataframe()
        balance_stmt = xbrl.statements.balance_sheet().to_dataframe()

        income_year_cols = [col for col in income_stmt.columns if str(year_choice) in str(col)]
        balance_year_cols = [col for col in balance_stmt.columns if str(year_choice) in str(col)]

        if len(income_year_cols) == 0 and len(balance_year_cols) == 0:
            continue

        found = True
        print("=" * 80)
        print(f"Ticker: {ticker}")
        print(f"Requested Fiscal Year: {year_choice}")
        print(f"Filing Date: {filing_date}")
        print("=" * 80)

        print("\n[Income Statement Labels]")
        if "label" in income_stmt.columns:
            for i, label in enumerate(income_stmt["label"].fillna("").astype(str).tolist(), 1):
                print(f"{i}. {label}")
        else:
            print("No 'label' column found in income statement.")

        print("\n" + "=" * 80)

        print("\n[Balance Sheet Labels]")
        if "label" in balance_stmt.columns:
            for i, label in enumerate(balance_stmt["label"].fillna("").astype(str).tolist(), 1):
                print(f"{i}. {label}")
        else:
            print("No 'label' column found in balance sheet.")

        print("\n" + "=" * 80)
        break

    if not found:
        print(f"No 10-K statement found for {ticker} with fiscal year {year_choice}.")

ticker = input("Enter ticker: ").strip().upper()
year_choice = input("Enter fiscal year: ").strip()

print_statement_labels(ticker, year_choice)