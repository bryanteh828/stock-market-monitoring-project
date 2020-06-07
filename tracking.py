# -*- coding: utf-8 -*-
"""
Created on Sat May 16 13:33:56 2020

@author: USER
"""

import pandas as pd
import os
from datetime import datetime
from datetime import timedelta

try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')

df = pd.read_csv('transactions.csv')

df['cost_precommision'] = df['stockprice']*df['stocks']
df['commision_perc'] = round(100*df['commision']/df['cost_precommision'],3)
df['cost'] = df['commision']+df['cost_precommision']
df['unitcost'] = df['cost']/df['stocks']
df['commision_forex'] = (df['forex_bank']-df['forex'])*df['cost']
df['cost_sgd'] = df['cost']*df['forex_bank'] 

df['cost_with_forex'] = df['cost']+df['commision_forex']
df['unitcost_with_forex'] = df['cost_with_forex']/df['stocks']

ticker_list = pd.read_csv('tickers.csv')
ticker_list

df = df.drop(columns = ['ticker'])
df = df.merge(ticker_list[['name','ticker']],how = 'left',left_on = 'name',right_on ='name')

try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')

last_day_price = {}
last_day = {}
for ticker in df.ticker.unique():
    data = pd.read_csv(ticker+'_data.csv')
    last_day_price[ticker] = list(data['Close'])[-1]
    last_day[ticker] = list(data['index'])[-1]
    
try: df['purchase_date'] = df['purchase_date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
except:
    try: df['purchase_date'] = df['purchase_date'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    except: df['purchase_date'] = df['purchase_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
df['lastday_price'] = df.apply(lambda x: last_day_price[x['ticker']],axis = 1)
df['lastday_date'] = df.apply(lambda x: datetime.strptime(last_day[x['ticker']], '%Y-%m-%d'),axis = 1)
df['appreciation'] = round(100*(df['lastday_price']-df['unitcost'])/df['unitcost'],2)
df['market_value'] = df['cost_sgd']*(1+df['appreciation']/100)
df['change'] = df['market_value']-df['cost_sgd']
df['duration'] = df.apply(lambda x: (x['lastday_date'] - x['purchase_date']).days,axis=1)

try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')

df.to_csv('transactions.csv',index=False)


