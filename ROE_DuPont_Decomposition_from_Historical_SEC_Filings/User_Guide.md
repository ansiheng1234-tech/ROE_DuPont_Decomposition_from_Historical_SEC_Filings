ROE DuPont Decomposition – User Guide

Disclaimer
    This tool automatically extracts financial data from SEC filings based on predefined label lists.
    Because financial statement labels can vary across companies and years, the accuracy of the
    extracted data depends on whether the correct labels are matched. Users should verify results
    with the original financial statements when necessary. The author is not responsible for any
    errors or consequences resulting from the use of this tool.


1 Overview

    This tool retrieves financial data from U.S. companies’ 10-K filings and performs a
    DuPont decomposition of Return on Equity (ROE).

    It uses predefined label libraries in Labels_Library.py to locate the following items
    from XBRL statements:

        Net Income
        Total Revenue
        Total Assets
        Shareholders’ Equity

    The program then calculates:

        Profit Margin
        Asset Turnover
        Financial Leverage
        ROE

    Results are saved to an Excel file. An optional trend chart can also be generated.


2 Prerequisites

    Install required packages

        pip install pandas matplotlib seaborn edgar-tool tk

    Required libraries:

        edgar – access SEC EDGAR filings
        tkinter – input dialog (usually included with Python)
        pandas, matplotlib, seaborn – data processing and visualization


    Set your identity

        In both scripts replace the email address used in set_identity() with your own:

            set_identity("your_email@example.com")

        This is required when accessing SEC servers.


3 File Descriptions

    Labels_Library.py
        Contains lists of possible labels used for matching financial statement items.

    ROE_DuPont_Decomposition.py
        Main program for extracting financial data and calculating DuPont ratios.

    Find_Nonstandard_Labels.py
        Utility script used to identify alternative labels when the main program
        cannot find a required item.


4 Running the Program

    Run the main script:

        python ROE_DuPont_Decomposition.py

    A dialog window will appear. Enter the ticker and fiscal years separated by spaces.

        Example input:
        AAPL 2020 2021 2022

    The program will search the relevant filings and generate an Excel file
    containing the DuPont analysis.


5 How the Script Works

    For each requested year the script:

        1. Searches recent 10-K filings for the company.
        2. Identifies statement columns containing the requested fiscal year.
        3. Extracts Net Income and Revenue from the income statement.
        4. Extracts Total Assets and Shareholders’ Equity from the balance sheet.
        5. Converts values to billions of dollars.
        6. Calculates the DuPont ratios.
        7. Saves the results to roe_analysis.xlsx.


6 Label Matching

    Financial statement labels are not standardized across companies.

    The script uses two matching methods:

        Exact match
            The label must match an entry in the label library.

        Partial match
            If no exact match is found, the script checks whether a library label
            appears inside a statement label.

            Example:

                Net income

            may match

                Net income attributable to common shareholders

    If multiple matches are found, the first result is used and a warning is printed.


7 Updating the Label Library

    If the program prints:

        Skipping {year}: incomplete data

    it means a required label was not found.

    To resolve this:

        1. Run the helper script

            python Find_Nonstandard_Labels.py

        2. Enter the same ticker and year.

        3. The script will display all available labels from the filing.

        4. Locate the correct label manually.

        5. Add it to the appropriate list in Labels_Library.py.

    Then run the main script again.


8 Abnormal Ratio Warnings

    The script prints a warning if any ratio appears unrealistic.

        Profit margin greater than 80% or below -50%
        Asset turnover greater than 300% or below 5%
        Financial leverage greater than 1000%

    This usually indicates that an incorrect label was matched.


9 Output

    The program generates:

        roe_analysis.xlsx

    The file contains the following metrics:

        Net Income ($bn)
        Total Sales ($bn)
        Total Assets ($bn)
        Shareholders' Equity ($bn)
        Profit Margin (%)
        Asset Turnover (%)
        Financial Leverage (%)
        ROE (%)


10 Notes

    Automated label matching may occasionally select the wrong line item
    when similar labels exist. When results appear unusual, check the
    original SEC filing and update the label library if necessary.