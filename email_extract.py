# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 15:58:27 2019

@author: tehy

"""
import sys
import os
import math
from datetime import datetime
from fredapi import Fred
import pandas_datareader.data as web
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#from sklearn.preprocessing import scale

try:
    ticker = sys.argv[1]
    if ticker == 'gspc' or ticker == 'hsi' or ticker == 'klse': ticker = '^'+ ticker
    print('gathering stock price of ticker ' + ticker + '..')
except:
    sys.exit('no ticker specified..')

def GetFred(series,start_date):
    fred = Fred(api_key='c2071cff4e0b1b57b6bf28bc81e41e63')
    ds = fred.get_series(series,observation_start = start_date)
    return ds

def DataReader(series,api,start_date):
    end = datetime(datetime.today().year,datetime.today().month,datetime.today().day)
    if api == 'quandl':
        my_key = 'V3xNxiZK7s3rRe9Cyf6G'
        ds = web.DataReader(series,api,start_date,end,api_key=my_key).reset_index()
    else: 
        ds = web.DataReader(series,api,start_date,end).reset_index()
    ds.columns = ['index',series]
    return ds

def FillNan(list_):
    list_ = list(list_)
    for i in range(len(list_)-1):
        if (not math.isnan(list_[i]) and math.isnan(list_[i+1])): list_[i+1] = list_[i] 
    return list_


        
start_date = '1971-01-01'   
 #   series_list= ['GDP','WILL5000PRFC'] 
 #   for i in series_list:
 #       try:
 #           df = GetFred(i, start_date).reset_index().rename(columns={0:i})
 #           if series_list.index(i) ==0: df_total = df.iloc[0:0,:].drop(columns=[i])
 #           df_total = df_total.merge(df,how='outer',left_on='index',right_on='index')
 #           print('sucess on..' + str(i))
 #       except:
 #           print(sys.exc_info()[0])
 #           print('failed on' + str(i))
        
    # start_date = datetime(1971,1,1)
    # series_list=[['FRED/CP','quandl'],
    #              ['FRED/JHDUSRGDPBR','quandl']]
    # #^gspc - sp500, fref/jhdusrgdpbr - recession
    # for i in series_list:
    #     try:
    #         df = DataReader(i[0],i[1],start_date)
    #         df_total = df_total.merge(df,how='left',left_on='index',right_on='index')
    #         print('sucess on..' + str(i))
    #     except:
    #         print(sys.exc_info()[0])
    #         print('failed on' + str(i))

try:
    df = web.DataReader(ticker,'yahoo',start_date).reset_index()
    print('success on ',ticker,'..')
except:
    print('failed on',ticker,'..')
df.columns = ['index','High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close']   
#df_total = df_total.merge(df[['index','High','Low','Open','Close']],how='left',left_on='index',right_on='index')

#df_total['GDP'] = FillNan(df_total['GDP'])
    # df_total['FRED/JHDUSRGDPBR'] = FillNan(df_total['FRED/JHDUSRGDPBR'])
    # df_total['FRED/CP'] = FillNan(df_total['FRED/CP'])
    
    #profits = DataReader('FRED/CP','quandl',start_date)
    #hy_corp = DataReader('ML/HYOAS','quandl',start_date)
    #bond_yield = DataReader('ML/AAAEY','quandl',start_date)
    #sp500 = DataReader('^GSPC','yahoo',start_date)
    #recession = DataReader('FRED/JHDUSRGDPBR','quandl',start_date)
    
    #df_total = df_total.sort_values(['index'])
    #df_total = df_total.merge(sp500[['Date','Close']],how='left',left_on='index',right_on='Date')
    #df_total = df_total.drop(columns=['Date']).rename(columns={'Close':'SP500'})
    #df_total = df_total.merge(profits.rename(columns={'Date':'index','Value':'profits'}),how='left',left_on='index',right_on='index')
    #df_total = df_total.merge(hy_corp.rename(columns={'DATE':'index','BAMLH0A0HYM2':'credit_spread'}),how='left',left_on='index',right_on='index')
    #df_total = df_total.merge(recession.rename(columns={'Date':'index','Value':'recession'}),how='left',left_on='index',right_on='index')

try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')
    
df.to_csv(ticker + '_data.csv')
print('done....')






