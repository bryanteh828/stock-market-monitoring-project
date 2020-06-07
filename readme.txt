Purpose of the scripts and how to use it.

A - Daily Stock Market Report

Summary:
1 - Outputs:
    - Stock analysis of individual stocks
    - Summary view of 70+ stocks
    - A list of stocks in .csv format (see ticker.csv)

2 - Inputs:
    - Yahoo API on individual stock prices
3 - Automation: A Windows Scheduler, on my Windows Laptop

Scripts:
0 - batch_technical_analysis.py		Automates script 1-8.	
1 - email_extract.py			Extracts stock price from yahoo.com.
2 - email_analysis.py			Analyse with pandas, numpy (RSI, MA).
					save analysis in .txt file
					save visualisation in .png file.
					save summary analysis to a .csv file.
3 - email_email.py			Emails .txt and .png file to user.
4 - email_email_more_processing.py 	Further process the summary .csv file.
5 - email_more_analysis_2.py		Analyse summary of 70+ stock data into .png.
6 - email_more_analysis_4.py		Analyse summary of 70+ stock data into .png.
7 - email_more_analysis_5.py		Analyse summary of 70+ stock data into .png.
8 - email_email_overall.py		Emails summary of 70+ stock data.


B - A Portfolio Tracker

1 - Outputs: Portfolio's performance in visualized plots/tables
2 - Input: A record of stock purchase in .csv format (see transactions.csv)
3 - Automation: A Windows Scheduleer, on my Windows Laptop

Results are through email

Scripts:
0 - tracking.py				processes your initial .csv file of portfolio
1 - stock_tracker.py			Analyse individual stock performance (RSI, MA)
					Compare to index performance
2 - email_email_mystocks.py		Emails analysis of your portfolio.
					