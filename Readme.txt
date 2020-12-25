How this is used:

>> Track portfolio - script 2c.
>> Stock Prices dashboard - script 3a.

scripts description below:

1. pull_price >> pull stock prices with an input of a stock ticker
	
	a. price_pull.py >> extracts stock prices with an input of a stock ticker & output stock prices as .csv 
	b. price_anlys.py >> input stock prices as .csv & output dashboard.

2. tracker_portfolio >> builds a dashboard to show portfolio health

	a. portfolio_analysis.py >> input price purchases, utilizes "pull_price" scripts * output dashboard as .png
	b. portfolio_email.py >> input dashboard as .png & send email
	c. batch-script.py >> automates script 2a, 2b, 1a, 1b.