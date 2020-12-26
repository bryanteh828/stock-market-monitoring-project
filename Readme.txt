---------------------------------------------------------------------------------
How to use:

multiple scripts >>
	>> Track watchlist - script 1a-b, 2a-b, 4a-d *sequence in batch-script.py
	>> Track portfolio - script 1a-b, 2a-b, 3a-c *sequence in batch-script.py
	>> Track a list of Stocks (not necessarily stocks you have bought) - script 3a.

single script >>
	>> Pull a stock's price - script 2a
	>> Pull a stock's balance sheet - script 1a
---------------------------------------------------------------------------------
scripts description below:
1. pull_financials >> income statements, balance sheet, cash flow statements
2. pull_price >> stock prices (daily)
3. tracker_portfolio >> simulate portfolio (value overtime)


1. pull_financials >>

	a. financials_pull.py >> input of stock ticker & pull stock financials via BeautifulSoup & output financials. (also need to configure directory for files in script)

2. pull_price >>
	
	a. price_pull.py >> input of stock ticker & pull stock price via API & output stock prices as .csv (also need to configure directory for files in the script)
	b. price_anlys.py >> input stock prices as .csv & build dashboard

3. tracker_portfolio >>

	a. portfolio_analysis.py >> input price purchases, utilizes script 2a, 2b & output dashboard as .png
	b. portfolio_email.py >> input dashboard as .png & send email
	c. batch-script.py >> automates script 3a, 3b, 2a, 2b.

4. tracker_watchlist >>

	a. erase.py >> erases record.csv
	b. momentum.py / momentum_percentile.py / ps_pe.py / ytd.py >> charts from records.csv
	c. send_email.py >> send charts as email + table from records.csv
	d. batch-script.py >> automates script 1a, 1b, 4a-c.
---------------------------------------------------------------------------------