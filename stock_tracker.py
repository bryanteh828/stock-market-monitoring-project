#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 21:56:44 2020

@author: tehyuqi
"""
import os
import sys
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

pull_data = False
sns.set()
plt.style.use('classic')
##################################################################################
if os.path.exists(r'C:\\Users\\USER\\Dropbox\\'):
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
    isMac = 0
else: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')
    isMac = 1

temp = pd.read_csv('tickers.csv')
df = pd.read_csv('transactions.csv')
df['purchase_date'] = df['purchase_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

tickers_needed = list(df.ticker.unique()) + ['^gspc','^hsi']
if pull_data == True:
    for ticker in tickers_needed:
        print('processing ticker',ticker,'...')
        try: os.system(r'python3 email_extract.py'+' '+ticker)
        except: sys.exit('Script error')
        try:os.system(r'python3 email_analysis.py'+' '+ticker)
        except: sys.exit('Script error')
#################################################################################
k=0
for i in df.ticker.unique():
    current_ticker = i
    
    #collect purchase_date to discard data before purchase_date
    try: current_purchase_date = list(df[df.ticker==i]['purchase_date'])[-1]
    except: pass
    print(current_ticker,current_purchase_date,'...')   
        
    #ticker data
    try: os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    except: os.chdir(r'/Users/tehyuqi/stockdata')
    df2 = pd.read_csv(i+'_data.csv')
    df2['index'] = df2['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df2['ticker'] = i
    df2['name'] = list(temp[temp.ticker==i]['name'])[0]
    df2['appreciation']=df2['Close']/df[df['ticker']==i]['unitcost'].values[0]-1
    df2_long = df2
    df2_long = df2_long[df2_long['index']>list(df2_long['index'])[-1]-timedelta(261*3)]
    df2 = df2[df2['index']>list(df[df.ticker==i]['purchase_date'])[-1]]

    #index data for comparison
    if '.hk' in i: df3 = pd.read_csv('^hsi'+'_data.csv')
    else: df3 = pd.read_csv('^gspc'+'_data.csv')
    df3['index'] = df3['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df3 = df3[df3['index']>list(df[df.ticker==i]['purchase_date'])[-1]]
    df3['appreciation']=df3['Close']/list(df3['Close'])[-0] - 1
    
    #merge index data into ticker data, for plotting
    df2['market_RSI'] = list(df3['RSI'])
    df2['market'] = list(df3['appreciation'])
    df2['market_ma_200'] = list(df3['ma_200'])
    df2['market_price'] = list(df3['Close'])
    
    #create overall df of ticker, index data
    if k==0:
        df_copy = df2.iloc[[],:]
        df_copy_long = df2.iloc[[],:]
    
    #concatenate ticker, index data into an overall df
    df_copy = pd.concat([df_copy,df2])
    df_copy_long = pd.concat([df_copy_long,df2_long])
    k+=1 
#########################################################################################  
#1 - compare stock, index performance timeline as baseline comparison
fig3 = plt.figure(figsize=[23.5,11.5])
gs = fig3.add_gridspec(8, 9)
ax1 = fig3.add_subplot(gs[:4, :5])
color = sns.color_palette("muted")
# index_color = ['pink','grey']
color[len(df_copy.ticker.unique())]=(0.45, 0.45, 0.45)
color[len(df_copy.ticker.unique())+1]=(0.35, 0.35, 0.35)
i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = df_copy[df_copy.ticker==j]['appreciation']*100
    label = list(df_copy[df_copy.ticker==j]['name'])[0]
    plt.plot(x,y,color=color[i],marker='o',label=label,alpha=1,markersize=3)
    i+=1
plt.axhline(y=0,color='black',alpha=0.4)
plt.legend(loc='upper left',prop={"size":10.5})

i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = df_copy[df_copy.ticker==j]['market']*100
    plt.plot(x,y,color=color[i],alpha=0.3)
    i+=1

ax1b = ax1.twinx()
ax1b.set_ylim(tuple(np.array([ax1.get_ylim()[0],ax1.get_ylim()[1]])))
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1b.yaxis.set_major_formatter(mtick.PercentFormatter())
#########################################################################################
#2 - compare stock, index RSI timeline as baseline comparison
ax1 = fig3.add_subplot(gs[4:6, :5])
i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = df_copy[df_copy.ticker==j]['RSI']
    label = j
    plt.plot(x,y,color=color[i],marker='o',label=label,alpha=1,markersize=3)
    x1 = df_copy[df_copy.ticker==j]['index']
    y1 = df_copy[df_copy.ticker==j]['market_RSI']
    if '.hk' in j: plt.plot(x1,y1,color=color[6],alpha=1,linewidth=2.5)
    else: plt.plot(x1,y1,color=color[7],alpha=1,linewidth=2.5)
    i+=1
plt.axhline(y=50,color='black',alpha=0.4)
ax1b = ax1.twinx()
ax1b.set_ylim(tuple(np.array([ax1.get_ylim()[0],ax1.get_ylim()[1]])))

temp = pd.read_csv('^hsi'+'_data.csv')
temp['ticker']='^hsi'
temp['name'] = 'hangseng'
temp['index'] = temp['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
temp = temp[temp['index']>list(temp['index'])[-1]-timedelta(261*3)]
df_copy_long_temp = pd.concat([df_copy_long,temp])

temp = pd.read_csv('^gspc'+'_data.csv')
temp['ticker']='^gspc'
temp['name'] = 'sp500'
temp['index'] = temp['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
temp = temp[temp['index']>list(temp['index'])[-1]-timedelta(261*3)]
df_copy_long_temp = pd.concat([df_copy_long_temp,temp])
#########################################################################################
#3 - compare stock, index RSI boxplot as baseline comparison
ax1 = fig3.add_subplot(gs[4:6, 5:])
x = 'name'
y = 'RSI'
sns.boxplot(x=x,y=y,data=df_copy_long_temp,palette=color)
plt.axhline(y=50,color='black',alpha=0.4,linewidth=2.5)

j=0
for i in df_copy_long_temp.ticker.unique():
    y = list(df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'])[-1]
    # Add some random "jitter" to the x-axis
    x = i
    plt.plot(x, y, 'r.',alpha=1,markersize=8)
    j+=1

index_sd = []
for i in ['^hsi','^gspc']:
    mean = df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'].mean()
    std = df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'].std()
    last_day = list(df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'])[-1]
    index_sd.append(round((last_day-mean)/std,1))

plt.title('market RSI condition: '+ str(index_sd[0])+'(hsi) '+str(index_sd[1]) +'(sp500)',loc='left')
ax1.set(xlabel=None)
ax1.set(ylabel=None)
#########################################################################################
#4 - compare stock, index Trend timeline as baseline comparison
ax1 = fig3.add_subplot(gs[6:, :5])
i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = 100*(df_copy[df_copy.ticker==j]['Close'] - df_copy[df_copy.ticker==j]['ma_200'])/df_copy[df_copy.ticker==j]['ma_200']
    y2 = 100*(df_copy[df_copy.ticker==j]['market_price'] - df_copy[df_copy.ticker==j]['market_ma_200'])/df_copy[df_copy.ticker==j]['market_ma_200']
    plt.plot(x,y,color=color[i],marker='o',label=j,alpha=1,markersize=3)
    if '.hk' in j: plt.plot(x,y2,color=color[6],label=j+' control',alpha=.8,linewidth=2.5)
    else: plt.plot(x,y2,color=color[7],label=j+' control',alpha=.8,linewidth=2.5)
    i+=1
plt.axhline(y=0,color='black',alpha=0.4)
ax1b = ax1.twinx()
ax1b.set_ylim(tuple(np.array([ax1.get_ylim()[0],ax1.get_ylim()[1]])))
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1b.yaxis.set_major_formatter(mtick.PercentFormatter())
#########################################################################################
#5 - compare stock, index Trend boxplot as baseline comparison
ax1 = fig3.add_subplot(gs[6:, 5:])
df_copy_long_temp['trend_gap'] = 100*(df_copy_long_temp['Close'] - df_copy_long_temp['ma_200'])/df_copy_long_temp['ma_200']
df_copy_long['trend_gap'] = 100*(df_copy_long['Close'] - df_copy_long['ma_200'])/df_copy_long['ma_200']
x = 'name'
y = 'trend_gap'
sns.boxplot(x=x,y=y,data=df_copy_long_temp,palette=color)
plt.axhline(y=0,color='black',alpha=0.4,linewidth=2.5)

j=0
for i in df_copy_long_temp.ticker.unique():
    y = list(df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'])[-1]
    x = i
    plt.plot(x, y, 'r.',alpha=0.9,markersize=8)
    j+=1
    
index_sd = []
for i in ['^hsi','^gspc']:
    mean = df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'].mean()
    std = df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'].std()
    last_day = list(df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'])[-1]
    index_sd.append(round((last_day-mean)/std,1))

plt.title('Market trend condition: '+ str(index_sd[0])+'(hsi) '+str(index_sd[1]) +'(sp500)',loc='left')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1.set(xlabel=None)
ax1.set(ylabel=None)
##################################################################################
#6 - This is the table
market_beat = []
for i in df_copy.ticker.unique():
    market_beat.append(str(round(100*(list(df_copy[df_copy.ticker==i]['appreciation'])[-1]-list(df_copy[df_copy.ticker==i]['market'])[-1]),1))+'%')
  
rsi = []
for i in df_copy_long.ticker.unique():
    rsi.append(round(list(df_copy_long[df_copy_long.ticker==i]['RSI'])[-1]))

trend = []
for i in df_copy_long.ticker.unique():
    trend.append(str(round(list(df_copy_long[df_copy_long.ticker==i]['trend_gap'])[-1],1))+'%')
    
rsi_sd = []
for i in df_copy_long.ticker.unique():
    mean = df_copy_long[df_copy_long.ticker==i]['RSI'].mean()
    std = df_copy_long[df_copy_long.ticker==i]['RSI'].std()
    rsi_sd.append(round((list(df_copy[df_copy.ticker==i]['RSI'])[-1]-mean)/std,1))
    
trend_sd = []
for i in df_copy_long.ticker.unique():
    mean = df_copy_long[df_copy_long.ticker==i]['trend_gap'].mean()
    std = df_copy_long[df_copy_long.ticker==i]['trend_gap'].std()
    last_day = list(df_copy_long[df_copy_long.ticker==i]['trend_gap'])[-1]
    trend_sd.append(round((last_day-mean)/std,1))                             

ax1 = fig3.add_subplot(gs[:2, 5:])
df_plot_table = df[['name','unitcost','lastday_price','duration','appreciation']]
df_plot_table['market +/-'] = market_beat
df_plot_table['rsi'] = rsi
df_plot_table['trend gap'] = trend
df_plot_table['rsi STD'] = rsi_sd
df_plot_table['trend STD'] = trend_sd
df_plot_table['appreciation'] = df_plot_table['appreciation'].apply(lambda x: str(x)+'%')
for i in ['unitcost','lastday_price']:
    df_plot_table[i] = df_plot_table[i].apply(lambda x: round(x,2))
df_plot_table.columns = ['Name','Cost','Current','Days','Profit','Market +/-','RSI','Trend','RSI sd','Trend sd']
table =ax1.table(cellText=df_plot_table.values, colLabels=df_plot_table.columns, loc='center')

#styling the table
table.scale(1.1, 1.8)
table.auto_set_font_size(False)
table.set_fontsize(10)
plt.axis('off')
##################################################################################
#7 - this is the horizontal barchart
ax1 = fig3.add_subplot(gs[2:4, 5:])

df_temp = df[['cost_sgd','market_value','name']]
df_temp.columns = ['Cost','Value','name']
df_temp.set_index('name').T.plot(kind='barh', stacked=True,ax=ax1,legend=False,color=color)

#annotate individual purchase price
sum_of_x=0
for x in df_temp.set_index('name').Cost:
    sum_of_x += x/2
    plt.annotate(int(x),(sum_of_x,0.075),textcoords="offset points",xytext=(0,12),size=10,ha='center')
    sum_of_x += x/2

#annotate individual market price
sum_of_x=0
for x in df_temp.set_index('name').Value:
    sum_of_x += x/2
    plt.annotate(int(x),(sum_of_x,1.075),textcoords ="offset points",xytext=(0,12),size=10,ha='center')
    sum_of_x += x/2

#title
start = int(df_temp.Cost.sum())   
end = int(df_temp.Value.sum()) 
delta = end - start
delta_perc = round(100*(end*1.0-start*1.0)/start,1)
plt.title('Portfolio: '+str(start) + ' to '+str(end)+', change: '+str(delta)+', '+str(delta_perc)+'%',loc='left')

plt.tight_layout()
plt.savefig('my_stocks.png')
##################################################################################