from edgar import Company, set_identity
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import simpledialog
from Labels_Library import revenue_labels, net_income_labels, asset_labels, equity_labels

set_identity("YourOwnEmail@email.com")

"""
This script is the main program of the ROE DuPont Decomposition project. 
It retrieves historical 10-K XBRL data from SEC filings, 
extracts key financial statement items including net income, total sales, total assets, and shareholders' equity, 
and calculates DuPont-related ratios such as profit margin, asset turnover, financial leverage, and ROE.

Because financial statement labels may vary across companies and years, 
the program uses a label library together with both exact-match and partial-match searches to locate the required items. 
If abnormal ratios are detected, the output should be reviewed manually to confirm whether the selected labels are appropriate.

This tool is designed to automate and simplify historical ROE decomposition analysis that would otherwise require manual lookup from SEC filings.
"""


#input stock & years and initialize
tk.Tk().withdraw()
user_input = simpledialog.askstring("ROE DuPont Input", "Enter ticker and years:").split()

stock_choice = user_input[0]

years_choice = []

for y in range(len(user_input) - 1):
    years_choice.append(int(user_input[y + 1]))


#initializes
stock = Company(stock_choice)

filings = stock.get_filings(form= "10-K", amendments = False).head(12)

#define a fetch value function
def find_value(df, labels, year):
    #first round strict equals the label in label libraries
    for label in labels:
        rows = df.loc[df["label"].fillna("").str.strip().str.lower() == label.lower(), year].dropna()

        if len(rows) > 0:
            label_used = df.loc[rows.index[0], "label"]
            print(f"Lable: {label_used} is used for {year}, please check if this is the correct lebel")
            return rows.values[0]
    #if fails, do second round of whether label contains the label library, 
        #such that labels like "Total Nasdaq stockholders' equity" could be found
    for label in labels:
        vague_rows = df.loc[df["label"].fillna("").str.strip().str.lower().str.contains(label.lower(), na=False, regex=False), year].dropna()

        if len(vague_rows) ==  1:
            label_used = df.loc[vague_rows.index[0], "label"]
            print(f"Using Vague Search, lable: {label_used} is used for year {year}, please check if this is the correct lebel")
            return vague_rows.values[0]
        
        if len(vague_rows) > 1:
            label_used = df.loc[vague_rows.index[0], "label"]
            print(f"!!!THERE ARE MULTIPLE LABELS POSSIBLE FOR THIS ITEM!!!, lable {label_used} is used for year {year}, checking if this is the correct lebel from original SEC file is strongly recommended")
            return vague_rows.values[0]
        
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
        filing_year = int(str(file.filing_date)[:4])
        if filing_year < year - 3 or filing_year > year + 3:
            continue
        xbrl = file.xbrl()
        '''
        uncomment if you want to debug and see the year of file being searched
        print(f"looking through file of {file.filing_date}")
        '''
        if xbrl is None:
            print(f"Skipping filing with no XBRL: {file.filing_date}")
            continue
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
        filing_year = int(str(file.filing_date)[:4])
        if filing_year < year - 3 or filing_year > year + 3:
            continue
        xbrl = file.xbrl()
        '''
        uncomment if you want to debug and see the year of file being searched
        print(f"looking through file of {file.filing_date}")
        '''
    
        if xbrl is None:
            print(f"Skipping filing with no XBRL: {file.filing_date}")
            continue
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

    if profit_marginR > 80 or profit_marginR < -50 or asset_turnoverR > 300 or asset_turnoverR < 5 or financial_leverageR > 1000:
        print("WARNING: DuPont ratios look abnormal. Label selection may be incorrect. Please check the labels carefully.")

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