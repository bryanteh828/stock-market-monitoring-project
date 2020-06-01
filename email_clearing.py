# -*- coding: utf-8 -*-
"""
Created on Fri May  8 19:14:10 2020

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

record = pd.read_csv('records.csv')

record_copy = record.iloc[ [ ] , : ]
    
record_copy.to_csv('records.csv',index=False)


record_2 = pd.read_csv('records_2.csv')


record_2_copy = record_2.iloc[ [ ] , : ]
    
record_2_copy.to_csv('records_2.csv',index=False)
