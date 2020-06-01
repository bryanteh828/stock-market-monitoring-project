# -*- coding: utf-8 -*-
"""
Created on Wed May  6 20:49:17 2020

@author: USER
"""
import os
import pandas as pd

try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')
    
df = pd.read_csv('records.csv')


index_data_to_transform = ['5yr_trend', 'rsi14', 'Close_200ma', '1mo_trend','Close_50ma', '1yr_trend']

for j in range(len(index_data_to_transform)):
    us_index = list(df[df['ticker']=='^gspc'][index_data_to_transform[j]])[-1]
    hk_index = list(df[df['ticker']=='^hsi'][index_data_to_transform[j]])[-1]
    
    is_us = ['us' in i for i in list(df.country)]
    index_price = []
    
    for i in range(len(df)):
        if is_us[i] == True: index_price.append(us_index)
        else: index_price.append(hk_index)
    
    df[ 'index_'+index_data_to_transform[j] ]=index_price
    df[ 'index_'+index_data_to_transform[j] ] = df[ index_data_to_transform[j] ]-df[ 'index_'+index_data_to_transform[j] ]
    
df.to_csv('records_2.csv',index=False)
