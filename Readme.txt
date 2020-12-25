How this is used:

>> Track portfolio - script 2c.
>> Track a list of Stocks (not necessarily stocks you have bought) - script 3a.

scripts description below:

1. pull_price >> pulls stock prices with an input of a stock ticker
	
	a. price_pull.py >> input of stock ticker & pull stock price via API & output stock prices as .csv 
						(also need to configure directory of output file in script)
	b. price_anlys.py >> input stock prices as .csv & build dashboard

2. tracker_portfolio >> builds a dashboard to show portfolio health

	a. portfolio_analysis.py >> input price purchases, utilizes script 1a, 1b & output dashboard as .png
	b. portfolio_email.py >> input dashboard as .png & send email
	c. batch-script.py >> automates script 2a, 2b, 1a, 1b.