# -*- coding: utf-8 -*-
"""
Created on Tue May  5 16:22:23 2020
@author: USER
"""

import os
import pandas as pd
import sys


if os.path.exists(r'C:\\Users\\USER\\Dropbox\\'):
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
    isMac = 0
else: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')
    isMac = 1
# os.listdir()

print('clearing temporary data log')
do_email = 1
df = pd.read_csv('tickers.csv')

if not isMac:
    try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_clearing.py')
    except: sys.exit('Script error')





    tickers = df.ticker.unique()
    for ticker in tickers:
        try: os.system(r'C:\Users\USER\Anaconda3\python.exe email_extract.py'+' '+ticker)
        except: sys.exit('Script error')
        try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_analysis.py'+' '+ticker)
        except: sys.exit('Script error')

        if do_email:
            try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_email.py'+' '+ticker)
            except: sys.exit('Script error')
        print('done with',ticker)
        
    try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_processing.py'+' '+ticker)
    except: sys.exit('Script error')

    # try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis.py'+' '+ticker)
    # except: sys.exit('Script error')


    try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis_4.py'+' '+ticker)
    except: sys.exit('Script error')

    try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis_5.py'+' '+ticker)
    except: sys.exit('Script error')

    try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis_volatility.py'+' '+ticker)
    except: sys.exit('Script error')

    try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis_2.py'+' '+ticker)
    except: sys.exit('Script error')

    # try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis_3.py'+' '+ticker)
    # except: sys.exit('Script error')

    if do_email:
        try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_email_overall.py'+' '+ticker)
        except: sys.exit('Script error')
else:
    try:os.system(r'python3 email_clearing.py')
    except: sys.exit('Script error')



    tickers = df.ticker.unique()
    for ticker in tickers:
        try: os.system(r'python3 email_extract.py'+' '+ticker)
        except: sys.exit('Script error')
        try:os.system(r'python3 email_analysis.py'+' '+ticker)
        except: sys.exit('Script error')

        if do_email:
            try:os.system(r'python3 email_email.py'+' '+ticker)
            except: sys.exit('Script error')
        print('done with',ticker)
        
    try:os.system(r'python3 email_more_processing.py'+' '+ticker)
    except: sys.exit('Script error')

    # try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis.py'+' '+ticker)
    # except: sys.exit('Script error')


    try:os.system(r'python3 email_more_analysis_4.py'+' '+ticker)
    except: sys.exit('Script error')

    try:os.system(r'python3 email_more_analysis_5.py'+' '+ticker)
    except: sys.exit('Script error')

    try:os.system(r'python3 email_more_analysis_volatility.py'+' '+ticker)
    except: sys.exit('Script error')

    try:os.system(r'python3 email_more_analysis_2.py'+' '+ticker)
    except: sys.exit('Script error')

    # try:os.system(r'C:\Users\USER\Anaconda3\python.exe email_more_analysis_3.py'+' '+ticker)
    # except: sys.exit('Script error')

    if do_email:
        try:os.system(r'python3 email_email_overall.py'+' '+ticker)
        except: sys.exit('Script error')




