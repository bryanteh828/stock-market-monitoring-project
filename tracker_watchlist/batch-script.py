import os
import pandas as pd
import sys
import threading

def extract(ticker):
    os.chdir(pp_dir)
    scripts = ['price_pull.py',
               'price_anlys.py']
    for script in scripts:
        try: os.system(f'python3 {script} {ticker}')
        except: sys.exit('script error..')

pp_dir = r'/Users/tehyuqi/dropbox/pull_price'
script_dir = r'/Users/tehyuqi/dropbox/tracker_watchlist'
input_dir = r'/Users/tehyuqi/dropbox'

os.chdir(script_dir)
try:
    os.system(r'python3 erase.py')
except: 
    sys.exit('script error')

os.chdir(input_dir)
df = pd.read_csv('tickers.csv')
tickers = df.ticker.unique()

#pull price
for k in range(len(tickers)):
    threads = []
    
    t = threading.Thread(target = extract, args=[tickers[k]])
    t.start()
    threads.append(t)
    
for thread in threads:
    thread.join()

#charting
os.chdir(script_dir)
scripts = ['momentum.py',
           'momentum_percentile.py',
           'ytd.py',
           'ps_pe.py',
           'email.py']

for script in scripts:
    try: os.system(f'python3 {script}')
    except: sys.exit('Script error')

