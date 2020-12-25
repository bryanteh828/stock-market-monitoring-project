How this is used:

multiple scripts >>
	>> Track portfolio - script 2a, 2b, 3a, 3b, 3c
	>> Track a list of Stocks (not necessarily stocks you have bought) - script 3a.

single script >>
	>> Pull a stock's price - script 2a
	>> Pull a stock's balance sheet - script 1a

scripts description below:

1. pull_financials >> pulls stock balance sheet with input of a stock ticker

	a. financials_pull.py >> input of stock ticker & pull stock financials via BeautifulSoup & output financials. (also need to configure directory for files in script)


2. pull_price >> pulls stock prices with an input of a stock ticker
	
	a. price_pull.py >> input of stock ticker & pull stock price via API & output stock prices as .csv (also need to configure directory for files in the script)
	b. price_anlys.py >> input stock prices as .csv & build dashboard

3. tracker_portfolio >> builds a dashboard to show portfolio health

	a. portfolio_analysis.py >> input price purchases, utilizes script 2a, 2b & output dashboard as .png
	b. portfolio_email.py >> input dashboard as .png & send email
	c. batch-script.py >> automates script 3a, 3b, 2a, 2b.