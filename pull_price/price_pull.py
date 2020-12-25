import sys
import os
from datetime import datetime
import pandas_datareader.data as web
        
output_dir = r'/Users/tehyuqi/stockdata'

def DataReader(series,api,start_date):
    end = datetime(datetime.today().year,datetime.today().month,datetime.today().day)
    ds = web.DataReader(series,api,start_date,end).reset_index()
    ds.columns = ['index',series]
    return ds

try:
    ticker = sys.argv[1]
    if ticker == 'gspc' or ticker == 'hsi' or ticker == 'klse': ticker = '^'+ ticker
except:
    sys.exit('no ticker specified..')

try:
    start_date = '1971-01-01'   
    df = web.DataReader(ticker,'yahoo',start_date).reset_index()
    df.columns = ['index','High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close']  
    print('pulled',ticker,'..')
except:
    print('failed',ticker,'..')

os.chdir(output_dir)
df.to_csv(ticker + '_data.csv', index = False)