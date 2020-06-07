Map of scripts:

A - Stock Market Report

Summary:
1 - Outputs 2 results:
    - stock trend of individual stocks
    - summary view of 70+ stocks
2 - Inputs:
    - Yahoo API on stock prices
3 - Result are through email


Scripts:
0 - batch_technical_analysis.py		Automates script 1-8.	
1 - email_extract.py			Extracts stock price from yahoo.com.
2 - email_analysis.py			Analyse with pandas, numpy (RSI, MA).
					save analysis in .txt file
					save visualisation in .png file.
					save summary analysis to a .csv file.
3 - email_email.py			Emails .txt and .png file to user.
4 - email_email_more_processing.py 	Further process the summary .csv file.
5 - email_more_analysis_2.py		Analyse summary on 70+ stock data into .png.
6 - email_more_analysis_4.py		Analyse summary on 70+ stock data into .png.
7 - email_more_analysis_5.py		Analyse summary on 70+ stock data into .png.
8 - email_email_overall.py		Emails summary of 70+ stock data.


B - A Portfolio Tracker

1 - Outputs:
    - Portfolio's performance in visualized plots/tables
2 - Input:
    - a saved .csv file of your stock purchases.

Results are through email

Scripts:
0 - tracking.py				processes your initial .csv file of portfolio
1 - stock_tracker.py			Analyse individual stock performance (RSI, MA)
					Compare to index performance
2 - email_email_mystocks.py		Emails analysis of your portfolio.
					