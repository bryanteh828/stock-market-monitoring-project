# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 15:58:27 2019

@author: tehy

"""
import os
import math
from datetime import datetime
import sys

import fredapi
from fredapi import Fred
import pandas_datareader.data as web

import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from matplotlib.offsetbox import AnchoredText

import scipy.stats as ss

#import mplfinance as mpf
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

try:
    ticker = sys.argv[1]
    if ticker == 'gspc' or ticker == 'hsi' or ticker == 'klse': ticker = '^'+ ticker
    print('analyzing ticker ' + ticker + '..')
except:
    sys.exit('no ticker specified..')
###########################################################################################################################


#start_date = input('what is your start date? (in decimals, e.g. 2018.12 or 2019.06)')
#end_date = input('what is your end date? (in decimals, e.g. 2018.12 or 2019.06)')


def rsi(input_col, window_length):
    up, down = input_col.copy(), input_col.copy() 
    up[up < 0], down[down > 0] = 0, 0
    roll_up2, roll_down2 = up.rolling(window_length).mean(), down.abs().rolling(window_length).mean()
    rs = roll_up2 / roll_down2 
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi

def macd(input_col, short, long, exp):
    exp1, exp2 = input_col.ewm(span=short, adjust=False).mean(), input_col.ewm(span=long, adjust=False).mean()
    macd = exp1 - exp2
    exp3 = macd.ewm(span=exp, adjust=False).mean()
    macd_exp3 = list(macd - exp3)
    crossovers = [0]*len(macd_exp3)
    for i in range(len(macd_exp3)-1):
        if   (macd_exp3[i] > 0) and (macd_exp3[i-1] < 0): crossovers[i] = 1
        elif (macd_exp3[i] < 0) and (macd_exp3[i-1] > 0): crossovers[i] = -1
    return exp1, exp2, exp3, macd, crossovers

def bol_band(input_col, bol_period):
    mean = input_col.rolling(window = bol_period).mean()
    std = input_col.rolling(window = bol_period).std()     
    upper = mean + (std*2)
    lower = mean - (std*2)
    smaller_upper = mean + (std*1)
    smaller_lower = mean - (std*1)
    return mean, upper, lower, smaller_upper, smaller_lower

def reposition(x, move):
    box = ax1.get_position()
    box.y1 = box.y1 - move
    ax1.set_position(box)
    return
######################################################ø#####################################################################
    
try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')

df = pd.read_csv(ticker + '_data.csv')
df = df.dropna(subset=['Close'])
df['index'] = df['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
df['int_date'] = df['index'].apply(lambda x: float(str(x.year)+'.0'+str(x.month)) if x.month < 10 else float(str(x.year)+'.'+str(x.month)))
df = df.sort_values(['index'])

###########################################################################################################################

# df['DGS_3MO_10'] = df['DGS10'] - df['DGS3MO']
df['Close_ror'] = (df['Close']-df['Close'].shift(1))/df['Close']
period = 20
df['RSI'] = rsi(df['Close_ror'], period)
bol_period = 20
df['bol_ma'], df['Upper Band'], df['Lower Band'],  df['Smaller Upper Band'], df['Smaller Lower Band'] = bol_band(df['Close'],bol_period)
short_period, long_period, exp_period = 50, 200, 50
df['ma_50'], df['ma_200'],e,w,q= macd(df['Close'],short_period, long_period, exp_period)
short_period, long_period, exp_period = 12, 26, 9
df['ma_short'], df['ma_long'], df['ma_longshort'],df['macd'], df['crossovers'] = macd(df['Close'],short_period, long_period, exp_period)

df.to_csv(ticker + '_data.csv',index=False)
###########################################################################################################################

# if(list(df['int_date'])[-1] - int(list(df['int_date'])[-1]))<0.06:
#     start_date = (list(df['int_date'])[-1]-0.06-0.88)
# else:
#     start_date = (list(df['int_date'])[-1]-0.06)

start_date = (list(df['int_date'])[-1]-3)
    
if(list(df['int_date'])[-1] - int(list(df['int_date'])[-1]))<0.02:
    start_date2 = (list(df['int_date'])[-1]-0.02-0.88)
else:
    start_date2 = (list(df['int_date'])[-1]-0.02)
df_short2 = df[(df['int_date']>=float(start_date2))]

end_date = ''

if start_date != '':
    try: df_short = df[(df['int_date']>=float(start_date))]
    except:sys.exit('cant process what you typed')
    if end_date != '':
        try:df_short = df_short[(df_short['int_date']<=float(end_date))]
        except:sys.exit('cant process what you typed')
else:
    if end_date != '':
        try:df_short = df[(df['int_date']<=float(end_date))]
        except:sys.exit('cant process what you typed')
    else:
        df_short=df


#######################################################################################################################################

x = df_short['index']
y = df_short['Close']
y1=df_short['ma_200']
y2=df_short['ma_50']
plt.style.use('classic')
fig3 = plt.figure(figsize=[23.5,11.5])
gs = fig3.add_gridspec(8, 8)
ax1 = fig3.add_subplot(gs[0:4, 1:-2])
plt.plot(x,y,label ='Close',color='black',marker='o',alpha=0.6,markersize=2.2)
plt.plot(x,y2,label = '50ma',color='dodgerblue',alpha=0.35)
plt.plot(x,y1,label = '200ma',color='blue',alpha=0.35)
ax1.fill_between(df_short['index'], df_short['Lower Band'], df_short['Upper Band'], color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')

ax1.axhline(np.array(list(y)[-260:]).max(),color='grey',label='YTD high/low',lw=1.3,alpha=0.7,linestyle='dotted')
value = round(100*(np.array(list(y)[-260:]).max()-list(y)[-1])/list(y)[-1],1)
ytd_max = value
label = str(round(np.array(list(y)[-260:]).max(),2))
plt.annotate( label , (list(x)[-1],np.array(list(y)[-260:]).max()) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')
label ='+'+str(value)+'%'
plt.annotate( label , (list(x)[-1],np.array(list(y)[-260:]).max()) , textcoords ="offset points" , xytext=(0,-10) , size =10, ha='center',weight='bold')

x = df_short[df_short.RSI<30]['index']
y2 = df_short[df_short.RSI<30]['Close']
ax1.scatter(x,y2,color = 'limegreen',s=38,alpha=1,label='RSI sell trigger')
x = df_short[df_short.RSI>70]['index']
y2 = df_short[df_short.RSI>70]['Close']
ax1.scatter(x,y2,color = 'tomato',s=38,alpha=1,label='RSI buy trigger')
plt.legend(prop={'size': 10},loc='upper left')

ax1.axhline(list(y)[-1],linestyle='dotted',color='blueviolet',label='today',lw=1.3)
label = str(round(list(y)[-1],2))
plt.annotate( label ,(list(x)[-1],list(y)[-1]) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')

ax1.axhline(np.array(list(y)[-260:]).min(),color='grey',label='YTD low',lw=1.3,alpha=0.7,linestyle='dotted')
value = round(100*(-list(y)[-1]+np.array(list(y)[-260:]).min())/list(y)[-1],1)
ytd_min = value
label = str(round(np.array(list(y)[-260:]).min(),2))
plt.annotate( label , (list(x)[-1],np.array(list(y)[-260:]).min()) , textcoords ="offset points" , xytext=(0,-10) , size = 9, ha='center')
label = str(value)+'%'
plt.annotate( label , (list(x)[-1],np.array(list(y)[-260:]).min()) , textcoords ="offset points" , xytext=(0,4) , size = 10, ha='center', weight='bold')


plt.title(ticker.upper()+' last 2 years:',loc='left',fontweight='bold')
ax1.fill_between(df_short['index'], df_short['Smaller Lower Band'], df_short['Smaller Upper Band'], color='grey',alpha=0.3,label='bollinger-'+str(bol_period))
ymin, ymax = ax1.get_ylim() # get yaxis limits for boxplot below...

###########################################################################

ax1 = fig3.add_subplot(gs[4:6, 1:-2])
x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']
ax1.plot(x,y2,label='Close/200ma',color='black',marker='o',alpha=0.6,markersize=2.2)
ax1.plot(x,y,label='50ma/200ma',color='dodgerblue',alpha=0.35)
ax1.axhline(y=0,label='200ma',color='blue',alpha=0.35,lw=1.2)
ax1.axhline(y=y2.median(),label='mean',color='black',alpha=0.6,lw=1.2)
trend_median = y2.median()
x = df_short[df_short.RSI<30]['index']
y2 = 100*(df_short[df_short.RSI<30]['Close']-df_short[df_short.RSI<30]['ma_200'])/df_short[df_short.RSI<30]['ma_200']
ax1.scatter(x,y2,color = 'limegreen',s=38,alpha=1,label='RSI buy trigger')
x = df_short[df_short.RSI>70]['index']
y2 = 100*(df_short[df_short.RSI>70]['Close']-df_short[df_short.RSI>70]['ma_200'])/df_short[df_short.RSI>70]['ma_200']
ax1.scatter(x,y2,color = 'tomato',s=38,alpha=1,label='RSI sell trigger')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ymin, ymax = ax1.get_ylim() # get yaxis limits for boxplot below...

x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']

ax1.fill_between(df_short['index'], y2.mean()+y2.std()*2, y2.mean()-y2.std()*2, color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.fill_between(df_short['index'], y2.mean()+y2.std(), y2.mean()-y2.std(), color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')

x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']
if list(y2)[-1]>y2.mean(): label = '+'+str(round((list(y2)[-1]-y2.mean())/y2.std(),2))+' SD'
else: label = str(round((list(y2)[-1]-y2.mean())/y2.std(),2))+' SD'
plt.annotate( label , (list(x)[-1],np.array(y2.mean()+y2.std()*2.1)) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')
trend_sd = round((list(y2)[-1]-y2.mean())/y2.std(),2)
###########################################################################

ax1 = fig3.add_subplot(gs[4:6,:1])
x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']
sns.boxplot(y2,orient='v',color='grey')
plt.ylim([ymin,ymax])
trend_percentile = int(ss.percentileofscore(y2, list(y2)[-1]))
trend_mean = round(y2.median(),1)
ax1.axhline(list(y2)[-1],linestyle='dotted',color='blueviolet',label=str(trend_percentile)+'th percentile',lw=1.3)
plt.legend(prop={'size': 10},loc='best')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter() )
ax1.axhline(y=0,label='200ma',color='blue',alpha=0.35,lw=1.2)
plt.ylabel('% to 200ma')

###########################################################################

ax1 = fig3.add_subplot(gs[6:,1:-2])
ax1.plot(df_short['index'],df_short.RSI,color = 'black',alpha=0.6,label='RSI '+str(period),marker='o',markersize=2.2)
plt.legend(prop={'size': 10},loc='upper left')
ax1.scatter(df_short[df_short.RSI<30]['index'],df_short[df_short.RSI<30].RSI,color = 'limegreen',s=38,alpha=1)
ax1.scatter(df_short[df_short.RSI>70]['index'],df_short[df_short.RSI>70].RSI,color = 'tomato',s=38,alpha=1)
ax1.axhline(y=70, color='black',linestyle='--')
ax1.axhline(y=50, color='blue',alpha=0.35,lw=1.2)
ax1.axhline(y=30, color='black',linestyle='--')
ymin, ymax = ax1.get_ylim() # get yaxis limits for boxplot below...
ax1.fill_between(df_short['index'], df_short['RSI'].mean()+df_short['RSI'].std()*2, df_short['RSI'].mean()-df_short['RSI'].std()*2, color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.fill_between(df_short['index'], df_short['RSI'].mean()+df_short['RSI'].std(), df_short['RSI'].mean()-df_short['RSI'].std(), color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
if list(df_short['RSI'])[-1]>df_short['RSI'].mean(): label = '+'+str(round((list(df_short['RSI'])[-1]-df_short['RSI'].mean())/df_short['RSI'].std(),2))+' SD'
else: label = str(round((list(df_short['RSI'])[-1]-df_short['RSI'].mean())/df_short['RSI'].std(),2))+' SD'
plt.annotate( label , (list(df_short['index'])[-1],np.array(df_short['RSI'].mean()+df_short['RSI'].std()*2.1)) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')
rsi_sd = round((list(df_short['RSI'])[-1]-df_short['RSI'].mean())/df_short['RSI'].std(),2)
ax1.axhline(y=df_short.RSI.median(),color='black',alpha=0.6,lw=1.2)
median_rsi = df_short.RSI.median() 

###########################################################################

ax1 = fig3.add_subplot(gs[6:,:1])
sns.boxplot(df_short.RSI,orient='v',color='grey')
rsi_percentile = int(ss.percentileofscore(df_short.RSI,list(df_short.RSI)[-1]))
ax1.axhline(list(df_short.RSI)[-1],linestyle='dotted',color='blueviolet',label=str(rsi_percentile)+'th percentile',lw=1.3)
plt.legend(prop={'size': 10},loc='best')
plt.ylim([ymin,ymax])
ax1.axhline(y=70, color='black',linestyle='--')
ax1.axhline(y=50, color='black')
ax1.axhline(y=30, color='black',linestyle='--')
plt.ylabel('RSI')


#######################################################################################################################################

x = df_short2['index']
y = df_short2['Close']
y1=df_short2['ma_200']
y2=df_short2['ma_50']

ax1 = fig3.add_subplot(gs[0:2,-2:])
plt.title(ticker.upper()+' last 60 days:',loc='left',fontweight='bold')
plt.plot(x,y,label ='Close',color='black',marker='o',alpha=0.6,markersize=2.8)
plt.plot(x,y2,label = 'Close 50ma',color='dodgerblue',alpha=0.35)
plt.plot(x,y1,label = 'Close 200ma',color='blue',alpha=0.35)
# ax1.fill_between(df_short2['index'], df_short2['Upper Band'], df_short2['Lower Band'], color='grey',alpha=0.25,label='bollinger-'+str(bol_period))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
plt.xticks(rotation=90)
ax1.fill_between(df_short2['index'], df_short2['Lower Band'], df_short2['Upper Band'], color='grey',alpha=0.1,label='bollinger-'+str(bol_period))
ax1.fill_between(df_short2['index'], df_short2['Smaller Lower Band'], df_short2['Smaller Upper Band'], color='grey',alpha=0.3,label='bollinger-'+str(bol_period))

x = df_short2[df_short2.RSI<30]['index']
y = df_short2[df_short2.RSI<30]['Close']
ax1.scatter(x,y,color = 'lightgreen',s=38)
x = df_short2[df_short2.RSI>70]['index']
y = df_short2[df_short2.RSI>70]['Close']
ax1.scatter(x,y,color = 'tomato',s=38)

###########################################################################

ax1 = fig3.add_subplot(gs[4:6,-2:])
x = df_short2['index']
y = 100*(df_short2['ma_50']-df_short2['ma_200'])/df_short2['ma_200']
y2 = 100*(df_short2['Close']-df_short2['ma_200'])/df_short2['ma_200']
ax1.plot(x,y2,label='Close/200ma',color='black',marker='o',alpha=0.6,markersize=2.8)
ax1.plot(x,y,label='50ma/200ma',color='dodgerblue',alpha=0.35)
ax1.axhline(y=0,label='200ma',color='blue',alpha=0.35,marker='o',markersize=4,lw=1.2)
ax1.axhline(y=trend_median,label='200ma',color='black',alpha=0.35,marker='o',markersize=4,lw=1.2)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
y1 = [0]*len(df_short2)
y2 =100*(df_short2['Close']-df_short2['ma_200'])/df_short2['ma_200']
x=df_short2['index']
ax1.fill_between(x, y1, y2,where=y2>=y1,facecolor='green',alpha=0.1)
ax1.fill_between(x, y1, y2,where=y2<=y1,facecolor='red',alpha=0.1)
ax1.yaxis.set_major_formatter(mtick.PercentFormatter() )
plt.xticks(rotation=90)
x = df_short2[df_short2.RSI<30]['index']
y2 = 100*(df_short2[df_short2.RSI<30]['Close']-df_short2[df_short2.RSI<30]['ma_200'])/df_short2[df_short2.RSI<30]['ma_200']
ax1.scatter(x,y2,color = 'lightgreen',s=38)
x = df_short2[df_short2.RSI>70]['index']
y2 = 100*(df_short2[df_short2.RSI>70]['Close']-df_short2[df_short2.RSI>70]['ma_200'])/df_short2[df_short2.RSI>70]['ma_200']
ax1.scatter(x,y2,color = 'tomato',s=38)

###########################################################################

ax1 = fig3.add_subplot(gs[2:4, -2:])
x = df_short2['index']
y = 100*(df_short2['Close']-df_short2['Close'].shift(1))/df_short2['Close']
y = y.fillna(0)
ax1.bar(x,y,label='% change',alpha=0)
plt.legend(prop={'size': 10},loc='lower left')
ax1.bar(x[y>0],y[y>0],color='limegreen',label='% change')
ax1.bar(x[y<=0],y[y<=0],color='tomato',label='% change')
# ax1.axhline(y=0,label='200ma',color='blue',alpha=0.35,lw=2.5)
# plt.ylabel('% to 200ma')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter() )
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
plt.xticks(rotation=90)

label = '+' + str(len(y[y>0])) +' days'
at = AnchoredText(label, prop=dict(size=9.5,color='darkgreen'), frameon=True, loc='upper right')
at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
ax1.add_artist(at)

label = '-' + str(len(y[y<0])) +' days'
at = AnchoredText(label, prop=dict(size=9.5,color='darkred'), frameon=True, loc='lower right')
at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
ax1.add_artist(at)

###########################################################################

ax1 = fig3.add_subplot(gs[6:,-2:])
ax1.plot(df_short2['index'],df_short2.RSI,color = 'black',alpha=0.5,label='RSI '+str(period),marker='o',markersize=2.8)
plt.legend(prop={'size': 10},loc='best')
ax1.scatter(df_short2[df_short2.RSI<30]['index'],df_short2[df_short2.RSI<30].RSI,color = 'lightgreen',s=38)
ax1.scatter(df_short2[df_short2.RSI>70]['index'],df_short2[df_short2.RSI>70].RSI,color = 'tomato',s=38)
ax1.axhline(y=70, color='black',linestyle='--')
ax1.axhline(y=50, color='blue',linewidth=1.2,alpha=0.35)
ax1.axhline(y=30, color='black',linestyle='--')
ax1.axhline(y=median_rsi,color='black',alpha=0.35,marker='o',markersize=4,lw=1.2)

y1= [50]*len(df_short2)
y2=df_short2['RSI']
x=df_short2['index']
ax1.fill_between(x, y1, y2,where=y2>=y1,facecolor='red',alpha=0.1)
ax1.fill_between(x, y1, y2,where=y2<=y1,facecolor='green',alpha=0.1)
# ax1.fill_between(x=df_short2['index'], y1=df_short2['macd'], where=y1<50, facecolor='red', interpolate=True)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
plt.xticks(rotation=90)

plt.tight_layout()
#######################################################################################################################################

plt.savefig('plots.png')

#Generate report for analysis

weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_of_week = weekDays[list(df['index'])[-1].date().weekday()]
week_of_year = list(df['index'])[-1].date().isocalendar()[1]

horizon=23
x1 = list(df['ma_200'])[-horizon:]
x0 = list(df['Close'])[-horizon:]
uptrend_days = 0
for i in range(-horizon,0):
    if x0[i]-x1[i]>=0: uptrend_days+=1 
sentiment1 = round((100*uptrend_days/horizon-50)/50,2)
if round((100*uptrend_days/horizon-50)/50,2) > 0:
    sentiment1 = '+'+str(round((100*uptrend_days/horizon-50)/50,2))
else:
    sentiment1 = str(round((100*uptrend_days/horizon-50)/50,2))
if uptrend_days/horizon < 0.35: trend_analysis = 'downtrend'
elif uptrend_days/horizon > 0.65: trend_analysis = 'uptrend'
else: trend_analysis = 'sideways'

horizon=69
x1 = list(df['ma_200'])[-horizon:]
x0 = list(df['Close'])[-horizon:]
uptrend_days = 0
for i in range(-horizon,0):
    if x0[i]-x1[i]>=0: uptrend_days+=1 
sentiment6 = round((100*uptrend_days/horizon-50)/50,2)
if round((100*uptrend_days/horizon-50)/50,2) > 0:
    sentiment6 = '+'+str(round((100*uptrend_days/horizon-50)/50,2))
else:
    sentiment6 = str(round((100*uptrend_days/horizon-50)/50,2))

horizon=138
x1 = list(df['ma_200'])[-horizon:]
x0 = list(df['Close'])[-horizon:]
uptrend_days = 0
for i in range(-horizon,0):
    if x0[i]-x1[i]>=0: uptrend_days+=1 
sentiment3 = round((100*uptrend_days/horizon-50)/50,2)
if round((100*uptrend_days/horizon-50)/50,2) > 0:
    sentiment3 = '+'+str(round((100*uptrend_days/horizon-50)/50,2))
else:
    sentiment3 = str(round((100*uptrend_days/horizon-50)/50,2))

horizon=254
x1 = list(df['ma_200'])[-horizon:]
x0 = list(df['Close'])[-horizon:]
uptrend_days = 0
for i in range(-horizon,0):
    if x0[i]-x1[i]>=0: uptrend_days+=1 
sentiment4 = round((100*uptrend_days/horizon-50)/50,2)
if round((100*uptrend_days/horizon-50)/50,2) > 0:
    sentiment4 = '+'+str(round((100*uptrend_days/horizon-50)/50,2))
else:
    sentiment4 = str(round((100*uptrend_days/horizon-50)/50,2))
if uptrend_days/horizon < 0.35: trend2_analysis = 'downtrend'
elif uptrend_days/horizon > 0.65: trend2_analysis = 'uptrend'
else: trend2_analysis = 'sideways'


try:
    horizon=1270
    x1 = list(df['ma_200'])[-horizon:]
    x0 = list(df['Close'])[-horizon:]
    uptrend_days = 0
    for i in range(-horizon,0):
        if x0[i]-x1[i]>=0: uptrend_days+=1 
    sentiment5 = round((100*uptrend_days/horizon-50)/50,2)
    if round((100*uptrend_days/horizon-50)/50,2) > 0:
        sentiment5 = '+'+str(round((100*uptrend_days/horizon-50)/50,2))
    else:
        sentiment5 = str(round((100*uptrend_days/horizon-50)/50,2))
    if uptrend_days/horizon < 0.35: trend_analysis5 = 'downtrend'
    elif uptrend_days/horizon > 0.65: trend_analysis5 = 'uptrend'
    else: trend_analysis5 = 'sideways'
except:
    trend_analysis5 =trend2_analysis 
    sentiment5 = sentiment4


if list(df['RSI'])[-1]<50: sentiment2 = 'BUY TRIGGER' 
else: sentiment2 = 'SELL TRIGGER'

x1 = list(df['ma_200'])[-1]
x0 = list(df['Close'])[-1]
price_difference = str(round(100*(x0-x1)/x1,1))+'%'
if x0-x1<0: word = 'below'
else: word = 'above'
if abs((x0-x1)/x1)<0.05: deviation = 'NEAR'
else: deviation = 'FAR'

x1 = list(df['ma_50'])[-1]
x0 = list(df['Close'])[-1]
price2_difference = str(round(100*(x0-x1)/x1,1))+'%'
if x0-x1<0: word2 = 'below'
else: word2 = 'above'

week_difference = []
for i in range(-6,-22,-5):
    week_difference.append(str(round(100*(round(list(df['Close'])[-1],1)-round(list(df['Close'])[i],1))/round(list(df['Close'])[i],1),1))+'%')
    
horizon = 20
down_breakout = 0
x0 = list(df['Smaller Lower Band'])[-horizon:]
x1 = list(df['Close'])[-horizon:]
for i in range(-horizon,0):
    if x1[i]<x0[i]: down_breakout +=1
down_breakout = -down_breakout
 
up_breakout = 0
x0 = list(df['Smaller Upper Band'])[-horizon:]
x1 = list(df['Close'])[-horizon:]
for i in range(-horizon,0):
    # print(x1[i],x0[i])
    if x1[i]>x0[i]: up_breakout +=1
up_breakout = up_breakout


#bollinger calculations:
df['Band Perc'] = (df['Upper Band']-df['Lower Band'])/(4*df['Close'])
volatility_5yr = str(round(100*(df['Band Perc'][-1270:].mean()),1))
volatility_1yr = str(round(100*(df['Band Perc'][-254:].mean()),1))
volatility_1mo = str(round(100*(df['Band Perc'][-23:].mean()),1))
volatility_1wk = str(round(100*(df['Band Perc'][-5:].mean()),1))
volatility_lastday = str(round(100*(df['Band Perc'][-1:].mean()),1))
    

std = (list(df['Upper Band'])[-1]-list(df['Lower Band'])[-1])/4
mean = (list(df['Upper Band'])[-1]+list(df['Lower Band'])[-1])/2
boll_range = round((list(df['Close'])[-1]-mean)/std,1)
if up_breakout>0 and down_breakout==0: boll_trend = 'UPTREND BREAKOUT'
elif up_breakout==0 and down_breakout<0: boll_trend ='DOWNTREND BREAKOUT'
else: boll_trend = 'BOTH BREAKOUT'

#triggers
if sentiment2 == 'SELL TRIGGER' and trend_analysis.upper() =='DOWNTREND': decision = 'SELL ALERT on 1mo-DOWNTREND' 
elif sentiment2 == 'BUY TRIGGER' and trend_analysis.upper() =='UPTREND': decision = 'BUY ALERT on 1mo-UPTREND'
elif sentiment2 == 'BUY TRIGGER' and trend_analysis.upper() =='SIDEWAYS': decision = 'BUY ALERT on 1mo-SIDEWAYS'
elif sentiment2 == 'SELL TRIGGER' and trend_analysis.upper() =='SIDEWAYS': decision = 'SELL ALERT on 1mo-SIDEWAYS'
else: 
    if trend_analysis.upper() =='DOWNTREND': decision='NO ACTION on 1mo-DOWNTREND'
    elif trend_analysis.upper() =='SIDEWAYS': decision='NO ACTION on 1mo-SIDEWAYS'
    else: decision='NO ACTION on 1mo-UPTREND'
    
if sentiment2 == 'SELL TRIGGER' and trend2_analysis.upper() =='DOWNTREND': decision2 = 'SELL ALERT on 1yr-DOWNTREND' 
elif sentiment2 == 'BUY TRIGGER' and trend2_analysis.upper() =='UPTREND': decision2 = 'BUY ALERT on 1yr-UPTREND'
elif sentiment2 == 'BUY TRIGGER' and trend2_analysis.upper() =='SIDEWAYS': decision2 = 'BUY ALERT on 1yr-SIDEWAYS'
elif sentiment2 == 'SELL TRIGGER' and trend2_analysis.upper() =='SIDEWAYS': decision2 = 'SELL ALERT on 1yr-SIDEWAYS'
else: 
    if trend2_analysis.upper() =='DOWNTREND': decision2='NO ACTION on 1yr-DOWNTREND'
    elif trend2_analysis.upper() =='SIDEWAYS': decision2='NO ACTION on 1yr-SIDEWAYS'
    else: decision2='NO ACTION on 1yr-UPTREND'

    
if sentiment2 == 'SELL TRIGGER' and trend_analysis5.upper() =='DOWNTREND': decision5 = 'SELL ALERT on 5yr-DOWNTREND' 
elif sentiment2 == 'BUY TRIGGER' and trend_analysis5.upper() =='UPTREND': decision5 = 'BUY ALERT on 5yr-UPTREND'
elif sentiment2 == 'BUY TRIGGER' and trend_analysis5.upper() =='SIDEWAYS': decision5 = 'BUY ALERT on 5yr-SIDEWAYS'
elif sentiment2 == 'SELL TRIGGER' and trend_analysis5.upper() =='SIDEWAYS': decision5 = 'SELL ALERT on 5yr-SIDEWAYS'
else: 
    if trend_analysis5.upper() =='DOWNTREND': decision5='NO ACTION on 5yr-DOWNTREND'
    elif trend_analysis5.upper() =='SIDEWAYS': decision5='NO ACTION on 5yr-SIDEWAYS'
    else: decision5='NO ACTION on 5yr-UPTREND'

#######################################################################################################################################
#write analysis notes for email

f= open("text.txt","w+")
f.write(str(list(df['index'])[-1].date())+': \n')
#write most recent price
if list(df['Close'])[-1] < 5:
    f.write('                '+str(round(list(df['Close'])[-1],2))+'..\n')
else:
    f.write('                '+str(round(list(df['Close'])[-1],1))+'..\n')
f.write('                '+str(price_difference)+' '+word.upper()+' 200ma..\n')
f.write('                '+str(price2_difference)+' '+word2.upper()+' 50ma..'+'\n')
f.write('                '+str(trend_mean)+'% 5yr mean trend..'+'\n')
    
f.write('\n')


#write stock triggers
f.write('RSI-20 is on a '+ sentiment2 +' '+str(int(list(df['RSI'])[-1]))+'..\n')

f.write('\n')
 
#write summary
# f.write('Stock is on\n')

# f.write('                ' +sentiment5+ ' 5yr '+trend_analysis5.upper()+'..\n')
# f.write('                ' +sentiment4+ ' 1yr '+trend2_analysis.upper()+'..\n')
# f.write('                '+sentiment1+ ' 1mo '+trend_analysis.upper()+'..\n')


f.write('Stock trend is on:\n')
trend_5yr = str(round((100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200'])[-1270:].median(),1))
trend_1yr = str(round((100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200'])[-254:].median(),1))
trend_1mo = str(round((100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200'])[-23:].median(),1))
f.write('                '+trend_5yr+'% 5yr..'+'\n')
f.write('                '+trend_1yr+'% 1yr..'+'\n')
f.write('                '+trend_1mo+'% 1mo..'+'\n')


f.write('\n')

f.write('bollinger-20 is on a '+boll_trend+ ' ['+str(up_breakout)+', '+str(down_breakout)+']\n')

f.write('\n')

f.write('                '+volatility_5yr+'% 5yr volatility..'+'\n')
f.write('                '+volatility_1yr+'% 1yr volatility..'+'\n')
f.write('                '+volatility_1mo+'% 1mo volatility..'+'\n')
f.write('                '+volatility_1wk+'% 1wk volatility..'+'\n')

f.write('\n')

f.write('----------------------------------\n')
f.write('Detailed analysis:\n\n')

f.write('Range: \n')
if list(df['Close'])[-1] < 5:
    f.write('       '+str(round(list(df['Close'])[-1],2))+' for Close..\n')
else:
    f.write('       '+str(round(list(df['Close'])[-1],1))+' for Close..\n')
f.write('       '+'+'+str(ytd_max)+'% to YTD high..\n')
f.write('       '+str(ytd_min)+'% to YTD low..\n')

f.write('\n')

f.write('Trend: \n')
f.write('       '+str(trend_mean)+'% for mean trend..'+'\n')
f.write('       '+str(round(list(df['ma_50'])[-1],1))+' for 50ma..'+'\n')
f.write('       '+str(round(list(df['ma_200'])[-1],1))+' for 200ma..'+'\n')

f.write('\n')

f.write('      '+sentiment1+' last 30 days..\n')
f.write('      '+sentiment6+' last 90 day..\n')
f.write('      '+sentiment3+' last 180 day..\n')
f.write('      '+sentiment4+' last 1 year..\n')
f.write('      '+sentiment5+' last 5 years..\n\n')

f.write('Volatility:\n')
f.write('      '+str(volatility_5yr)+'% for 5yr std..\n')
f.write('      '+str(volatility_1yr)+'% for 1yr std..\n')
f.write('      '+str(volatility_1mo)+'% for 1mo std..\n')
f.write('      '+str(volatility_1wk)+'% for 1wk std..\n')
f.write('      '+str(volatility_lastday)+'% for last day std..\n')
f.write('      '+str(boll_range)+' SD on this day..\n')
f.write('      '+str(up_breakout)+'days on upper bollinger..\n')
f.write('      '+str(down_breakout)+'days on lower bollinger..\n\n')

f.write('concluding week ' +str(list(df['index'])[-1].date().isocalendar()[1])+' analysis, '+str(list(df['index'])[-1].date())+', '+day_of_week+'...\n')

f.close() 

f= open("text.txt","r")
print(f.read())
f.close() 

##########################################################################################################################################
#update data onto summary sheet
try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')

ticker_list = pd.read_csv('tickers.csv')

newdata = []
newdata.append(list(ticker_list[ticker_list.ticker==ticker].country)[-1])
newdata.append(list(ticker_list[ticker_list.ticker==ticker].name)[-1])
try:newdata.append(list(ticker_list[ticker_list.ticker==ticker].industry)[-1])
except:newdata.append('unknown')
newdata.append(ticker)
newdata.append(str(list(df_short['index'])[-1]))
newdata.append(str(list(df_short['Close'])[-1]))
newdata.append(str(list(df_short['ma_200'])[-1]))
newdata.append(str(list(df_short['ma_50'])[-1]))
newdata.append(sentiment5)
newdata.append(str(list(df_short['RSI'])[-1]))
newdata.append(str((list(df_short['Close'])[-1]-list(df_short['ma_200'])[-1])/list(df_short['ma_200'])[-1]))
newdata.append(sentiment1)
newdata.append(str((list(df_short['Close'])[-1]-list(df_short['ma_50'])[-1])/list(df_short['ma_50'])[-1]))
newdata.append(sentiment4)
trend = float(sentiment5)
band_trend1 = 1 if trend >= 0.6 else 2 if trend >= 0.2 else 3 if trend >= -0.2 else 4
newdata.append(band_trend1)
trend = list(df_short['RSI'])[-1]
band_trend2 = 1 if trend <= 35 else 2 if trend <= 45 else 3 if trend <= 60 else 4
newdata.append(band_trend2)
trend = (list(df_short['Close'])[-1]-list(df_short['ma_200'])[-1])/list(df_short['ma_200'])[-1]
band_trend3 = 1 if trend < -0.15 else 2 if trend < -0.05 else 3 if trend < 0.8 else 4
newdata.append(band_trend3)
newdata.append(2*band_trend1+band_trend2+band_trend3)
newdata.append(ytd_max)
newdata.append(ytd_min)
newdata.append(trend_percentile)
newdata.append(rsi_percentile)
newdata.append(trend_mean)
newdata.append(volatility_5yr)
newdata.append(volatility_1mo)
last_5_days = df_short['RSI'][-5:]
newdata.append(len(last_5_days[last_5_days>70]))
newdata.append(len(last_5_days[last_5_days<30]))
newdata.append(trend_sd)
newdata.append(rsi_sd)

record = pd.read_csv('records.csv')

try: 
    last_date = datetime.strptime( list(record[record.ticker==ticker].date_of_analysis)[-1] ,'%Y-%m-%d %H:%M:%S').date()
    print('last date of record is',last_date,'..')
except:
    last_date = datetime(1990,1,1).date()
    print('no record, new entry..')

if (last_date < list(df_short2['index'][-1:])[-1].date()): 
    record.loc[len(record)] = newdata
    print('updating records..')
else: print('records are already up-to-date..')
    
record.to_csv('records.csv',index=False)

try: 
    ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%Y-%m-%d') if type(x) == str else datetime(1990,1,1).date())
except:
    try: ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%m/%d/%Y') if type(x) == str else datetime(1990,1,1).date())
    except: ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%d/%m/%Y') if type(x) == str else datetime(1990,1,1).date())
    
try:
    if (list(ticker_list[ticker_list.ticker==ticker].last_date_analysis)[-1] < list(df_short2['index'][-1:])[-1].date()):
        ticker_loc = list(ticker_list[ticker_list.ticker==ticker].index)[-1]
        ticker_analysis_date = list(ticker_list.last_date_analysis.fillna(0))
        ticker_analysis_date[ ticker_loc] =  list(df_short2['index'][-1:])[-1].date()
        ticker_list['last_date_analysis'] = ticker_analysis_date
        print('updating ticker_list...')
    else:
        print('tickers_list already up-to-date..')
except:
    print('fail to update dates..')

ticker_list.to_csv('tickers.csv',index=False)
    
#######################################################################################################################################