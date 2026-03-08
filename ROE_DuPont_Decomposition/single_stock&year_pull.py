from edgar import Company, set_identity

set_identity("your_email@example.com")

company = Company("INTU")
year_choice = "2019"
filings = company.get_filings(form="10-K")

# possible label candidates
revenue_labels = [
    "Net sales",
    "Net revenue",
    "Net revenues",
    "Revenue",
    "Revenues",
    "Total revenue",
    "Total revenues",
    "Total net revenues",
    "Total net revenue"
]

net_income_labels = [
    "Net income",
    "Net income (loss)",
    "Net earnings",
    "Net income attributable to Nasdaq",
    "Net earnings (loss)"
]

asset_labels = [
    "Total assets",
]

equity_labels = [
    "Total stockholders' equity",
    "Total stockholders’ equity",
    "Total shareholders' equity",
    "Total shareholders’ equity",
    "Stockholders' equity",
    "Stockholders’ equity",
    "Shareholders' equity",
    "Total Nasdaq stockholders' equity",
    "Total Nasdaq stockholders’ equity",
    "Total equity",
    "Shareholders’ equity"
]

def find_value(df, labels, year):
    for label in labels:
        rows = df.loc[df["label"] == label, year]
        if len(rows) > 0:
            return rows.values[0]
    return None


# -------- income statement --------

for filing in filings:
    xbrl = filing.xbrl()
    income_stmt = xbrl.statements.income_statement().to_dataframe()

    year_dates = []
    for col in income_stmt.columns:
        if year_choice in str(col):
            year_dates.append(col)

    if len(year_dates) == 0:
        continue

    year = year_dates[0]
    print(year)

    revenue = find_value(income_stmt, revenue_labels, year)
    net_income = find_value(income_stmt, net_income_labels, year)

    if revenue is not None and net_income is not None:
        break

print("Revenue:", revenue)
print("Net Income:", net_income)


# -------- balance sheet --------

for filing in filings:
    xbrl = filing.xbrl()
    balance_stmt = xbrl.statements.balance_sheet().to_dataframe()

    year_dates = []
    for col in balance_stmt.columns:
        if year_choice in str(col):
            year_dates.append(col)

    if len(year_dates) == 0:
        continue

    year = year_dates[0]

    assets = find_value(balance_stmt, asset_labels, year)
    equity = find_value(balance_stmt, equity_labels, year)

    if assets is not None and equity is not None:
        break

print("Total Assets:", assets)
print("Total Equity:", equity)