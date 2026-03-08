from edgar import Company, set_identity
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import simpledialog

set_identity("ansiheng1234@gmail.com")


#input stock & years and initialize
tk.Tk().withdraw()
user_input = simpledialog.askstring("ROE DuPont Input", "Enter ticker and years:").split()

stock_choice = user_input[0]

years_choice = []

for y in range(len(user_input) - 1):
    years_choice.append(int(user_input[y + 1]))


#initializes
stock = Company(stock_choice)

filings = stock.get_filings(form= "10-K", amendments= None).head(12)


# create all possible labels for data we need since they are inconsistent in financial statements (Which is really annoying!)
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


#define a fetch value function
def find_value(df, labels, year):
    for label in labels:
        rows = df.loc[df["label"].fillna("").str.strip() == label, year]

        if len(rows) > 0:
            return rows.values[0]
        
    return None


#initialize the dataframe
metrics = [
    "Net Income ($bn)",
    "Total Sales ($bn)",
    "Total Assets ($bn)",
    "Shareholders' Equity ($bn)",
    "Profit Margin (%)",
    "Asset Turnover (%)",
    "Financial Leverage (%)",
    "ROE (%)"
]

df = pd.DataFrame(index = metrics)


#get data of desired years, put each into the dataframe
for year in years_choice:
    year_shown = None
    net_income = None
    total_sales = None
    total_asset = None
    shareholder_equity = None

    #loop through income statement and get net income and total sales
    for file in filings:
        xbrl = file.xbrl()
        income_stmt = xbrl.statements.income_statement().to_dataframe()
        year_dates = []

        for col in income_stmt.columns:
            if str(year) in str(col):
                year_dates.append(col)

        if len(year_dates) == 0:
            continue

        fiscal_year = year_dates[0]
        net_income = find_value(income_stmt, net_income_labels, fiscal_year) 
        total_sales = find_value(income_stmt, revenue_labels, fiscal_year) 

        if net_income is None or total_sales is None:
            net_income = None
            total_sales = None
            continue

        net_income = net_income / 1e9
        total_sales = total_sales /1e9
        break

    #loop through balance sheet to get total asset and shareholders' equity
    for file in filings:
        xbrl = file.xbrl()
        balance_stmt = xbrl.statements.balance_sheet().to_dataframe()
        year_dates = []

        for col in balance_stmt.columns:
            if str(year) in str(col):
                year_dates.append(col)

        if len(year_dates) == 0:
            continue

        fiscal_year = year_dates[0]
        total_asset = find_value(balance_stmt, asset_labels, fiscal_year) 
        shareholder_equity = find_value(balance_stmt, equity_labels, fiscal_year) 

        if total_asset is None or shareholder_equity is None:
            total_asset = None
            shareholder_equity = None
            continue
        
        total_asset = total_asset/ 1e9
        shareholder_equity = shareholder_equity / 1e9
        year_shown = fiscal_year
        break

    if None in [net_income, total_sales, total_asset, shareholder_equity]:
        print(f"Skipping {year}: incomplete data.")
        continue

    #calculate ROE related data
    profit_marginR = round(net_income / total_sales, 4) * 100
    asset_turnoverR = round (total_sales / total_asset, 4) * 100
    financial_leverageR = round (total_asset / shareholder_equity, 4) * 100
    roe = round (net_income / shareholder_equity, 4) * 100

    #put data into the dataframe
    df[year_shown] = [
        net_income,
        total_sales,
        total_asset,
        shareholder_equity,
        profit_marginR,
        asset_turnoverR,
        financial_leverageR,
        roe
    ]

#transpose to align with the sample list excel 
df = df.T
df.index.name = stock_choice
print(df.round(4))


#turn to excel
df.to_excel("roe_analysis.xlsx")
os.system("open roe_analysis.xlsx")


#seaborn ROE trend diagram (uncomment to see the ROE trend)
'''
sns.lineplot(data=df["ROE (%)"])
plt.title(stock_choice + " ROE Trend")
plt.show()
'''