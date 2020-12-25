import os
import pandas as pd
import sys

script_dir = r'/Users/tehyuqi/dropbox/tracker_portfolio'

os.chdir(script_dir)
scripts = ['portfolio_analysis.py', #'portfolio_email.py']
           'portfolio_email.py']

for script in scripts:
    try: 
        os.system(r'python3 '+ script)
    except: 
        sys.exit('Script error')


  