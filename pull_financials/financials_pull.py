import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import warnings
warnings.filterwarnings('ignore')

ticker = sys.argv[1]
# ticker = 'tsm'

path = r'/Users/tehyuqi/stockdata'

if not (os.path.exists(path + r'/stock_data')):
    try:
        os.mkdir(path + r'/stock_data')
    except OSError:
        print ("Creation of the directory %s failed" % path + r'/stock_data')
    else:
        print ("Successfully created the 1/2 directory %s " % path + r'/stock_data')
if not os.path.exists(path + r'/stock_data/gathered') :
    try:
        os.mkdir(path + r'/stock_data/gathered')
    except OSError:
        print ("Creation of the directory %s failed" % path + r'/stock_data')
    else:
        print ("Successfully created the 2/2 directory %s " % path + r'/stock_data')

os.chdir(path + r'/stock_data')

# # # collected html data
def get_html(ticker,i):
    if i == 0:
        html = requests.get('https://www.marketwatch.com/investing/stock/' +  ticker + '/financials/balance-sheet','html.parser')
    elif i == 1:
        html = requests.get('https://www.marketwatch.com/investing/stock/' + ticker + '/financials','html.parser')
    elif i == 2:
        html = requests.get('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/cash-flow','html.parser')  
    elif i == 3:
        html = requests.get('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/balance-sheet/quarter','html.parser')
    elif i == 4:
        html = requests.get('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/income/quarter','html.parser')
    elif i == 5:
        html = requests.get('https://www.marketwatch.com/investing/stock/' + ticker + '/financials/cash-flow/quarter','html.parser')  
    html_2 = BeautifulSoup(html.content)
    return html_2

# # # scrapped balance sheet data
def parse_html(html_2,i):

    tr_1= html_2.find_all('tr',{'class':['table__row is-highlighted','table__row']})
      
    timestamp = []
    for line in tr_1:
        for j in line.find_all('th',{'class':'overflow__heading'}):
            if len(timestamp) <= 4 and j.text.isnumeric(): timestamp.append(j.text)
            elif len(timestamp) <= 4 and bool(re.match('.*-.*-.*',j.text)): timestamp.append(j.text)
    
    html_2_dict = {}
    k = 0
    for line in tr_1: 
        count = 0
        for l in line.find_all('td',{'class':'overflow__cell'}):
            if count == 0: 
                title = l.find_all('div')[0].text
            if count != 0 and count < 6: 
                html_2_dict[str(k) + ' ' + title + ' ' +  timestamp[count-1]]= l.text
            count +=1
        k+=1        
    return html_2_dict


# # # transformed as pandas, with some datacleaning [rid first char]
#df_1 - balance sheet in 'gathered' format
def df_transform(html_2_dict,i):

    df_1 = pd.DataFrame.from_dict(html_2_dict,orient='index').reset_index().rename(columns = {'index':'title',0:'value'})
    
    df_1['no'] = df_1.title.str.split('(\d+)').str.get(1)

    if i < 3: df_1['year'] = df_1.title.str.split('(\d+)').str.get(3)
    else: df_1['year'] = df_1.title.str.split('( \d*-.*-.*)').str.get(1).str.replace(' ','')
    
    df_1['title'] = df_1.title.str.split('(\d+)').str.get(2).apply(lambda x: x[1:-1])   
    df_1['title'] = df_1['title'].str.replace('\n','')
    df_1['title'] = df_1['title'] + ' ' + df_1['no']
    df_1['value'] = df_1['value'].apply(convert)

    df_1_pivot = df_1.pivot(columns='year',index='title',values='value')
    df_1_pivot['no'] = df_1_pivot.index.str.split(' ').str.get(-1)
    df_1_pivot = df_1_pivot.sort_values('no')
    
    df_1_pivot = df_1_pivot.reset_index()
    df_1_pivot['title'] = df_1_pivot['title'].apply(lambda x: x[:-3])
    
    return df_1, df_1_pivot

def convert(x):
    
    x = x.replace(',','')
    
    if x[-1] == '-': return float(0)
    elif x[-1] == '%': return float(x[:-1])/100
    elif x[-1] == ')':
        if x[-2] == 'B': return float(x[1:-2])*-1000000000 #start pos1, ignore ( as well
        elif x[-2] == 'T': return float(x[1:-2])*-1000000000000 #start pos1, ignore ( as well
        elif x[-2] == 'M': return float(x[1:-2])*-1000000 #start pos1, ignore ( as well
        elif x[-2] == 'K': return float(x[1:-2])*-1000 #start pos1, ignore ( as well
        else: return float(x[1:-1].replace(',',''))
    else:
        if x[-1] == 'B': return float(x[:-1])*1000000000 #start pos0
        elif x[-1] == 'T': return float(x[:-1])*-1000000000000 #start pos1, ignore ( as well
        elif x[-1] == 'M': return float(x[:-1])*1000000 #start pos0
        elif x[-1] == 'K': return float(x[:-1])*1000000 #start pos0
        else: return float(x.replace(',',''))
    return float(0)

for i in range(0,3):
    
    html_2 = get_html(ticker,i)
    html_2_dict = parse_html(html_2,i)
    df_1, df_1_pivot = df_transform(html_2_dict,i)

    if i == 0:
        print('\tprocessing balancesheet...')
        df_1_pivot.to_csv(ticker+'_balancesheet.csv',index=False)
        os.chdir(path + r'/stock_data/gathered')
        df_1.to_csv(ticker+ '_gathered_balancesheet.csv', index=False)
        os.chdir(path + r'/stock_data')
    if i == 1:
        print('\tprocessing income...')
        df_1_pivot.to_csv(ticker+'_income.csv',index=False)
        os.chdir(path + r'/stock_data/gathered')
        df_1.to_csv(ticker+ '_gathered_income.csv', index=False)
        os.chdir(path + r'/stock_data')
    if i == 2:
        print('\tprocessing cash flow...')
        df_1_pivot.to_csv(ticker+'_cashflow.csv',index=False)
        os.chdir(path + r'/stock_data/gathered')
        df_1.to_csv(ticker+ '_gathered_cashflow.csv', index=False)
        os.chdir(path + r'/stock_data')

    # if i == 3:
    #     print('processing balancesheet (quarterly)...')
    #     df_1_pivot.to_csv(ticker+'_balancesheet_q.csv',index=False)
    #     os.chdir(path + r'/stock_data/gathered')
    #     df_1.to_csv(ticker+ '_gathered_balancesheet_q.csv', index=False)
    #     os.chdir(path + r'/stock_data')
    # if i == 4:
    #     print('processing income (quarterly)...')
    #     df_1_pivot.to_csv(ticker+'_income_q.csv',index=False)
    #     os.chdir(path + r'/stock_data/gathered')
    #     df_1.to_csv(ticker+ '_gathered_income_q.csv', index=False)
    #     os.chdir(path + r'/stock_data')
    # if i == 5:
    #     print('processing cash flow (quarterly)...')
    #     df_1_pivot.to_csv(ticker+'_cashflow_q.csv',index=False)
    #     os.chdir(path + r'/stock_data/gathered')
    #     df_1.to_csv(ticker+ '_gathered_cashflow_q.csv', index=False)
    #     os.chdir(peath + r'/stock_data')

# print('done....')
