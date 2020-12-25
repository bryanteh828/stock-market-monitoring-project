import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import scipy.stats as ss

import os
import sys
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

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
#################################################################################
# read argument
try:
    ticker = sys.argv[1]
    if ticker == 'gspc' or ticker == 'hsi' or ticker == 'klse': ticker = '^'+ ticker
    print('analyzing ticker ' + ticker + '..')
except:
    sys.exit('no ticker specified..')
    

#################################################################################
# read ticker & stock price
price_dir = r'/Users/tehyuqi/stockdata'
summary_dir = r'/Users/tehyuqi/dropbox'

os.chdir(summary_dir)
ticker_list = pd.read_csv('tickers.csv')
portfolio = pd.read_csv('transactions.csv')

try:
    portfolio.purchase_date = portfolio.purchase_date.apply(lambda x: datetime.strptime(x, '%d/%m/%y'))
except: 
    portfolio.purchase_date = pd.to_datetime(portfolio.purchase_date)
try: 
    portfolio.sell_date = pd.to_datetime(portfolio.sell_date,format='%d/%m/%y')
except: 
    portfolio.sell_date = pd.to_datetime(portfolio.sell_date)
try:
    portfolio = portfolio[portfolio.ticker == ticker]
    buy_date = portfolio.purchase_date.reset_index(drop=True)
    sell_date = portfolio.sell_date.reset_index(drop=True)
    sell_date = sell_date.fillna(pd.to_datetime(datetime.now().date()))
except:
    pass

os.chdir(price_dir)
df = pd.read_csv(ticker + '_data.csv')
df = df.dropna(subset=['Close'])
df['index'] = df['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
df['int_date'] = df['index'].apply(lambda x: float(str(x.year)+'.0'+str(x.month)) if x.month < 10 else float(str(x.year)+'.'+str(x.month)))
df = df.sort_values(['index'])

################################################################################# 
# processing
period = 20
bol_period = 20
ma_short_period, ma_long_period, ma_exp_period = 50, 200, 50
df['Close_ror'] = df['Close'].pct_change()
df['RSI'] = rsi(df['Close_ror'], period)
df['bol_ma'], \
df['Upper Band'], \
df['Lower Band'], \
df['Smaller Upper Band'], \
df['Smaller Lower Band'] = bol_band(df['Close'],bol_period)
df['ma_50'], df['ma_200'],e,w,q= macd(df['Close'],ma_short_period, ma_long_period, ma_exp_period)
df['rolling_min'] = df['Close'].rolling(261).min()
df['rolling_max'] = df['Close'].rolling(261).max()
df['3mo_ror'] = df['Close'].pct_change(64)
df.to_csv(ticker + '_data.csv',index=False)
################################################################################# 
# check buy sell date

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

###########################################################################
# Main Chart
plt.style.use('ggplot')
fig3 = plt.figure(figsize=[23.5,11.5])
gs = fig3.add_gridspec(11, 8)
ax1 = fig3.add_subplot(gs[0:5, :-1])
x  = df_short['index']
y  = df_short['Close']
y1 = df_short['ma_200']
y3 = df_short['rolling_min']
y4 = df_short['rolling_max']
y98 = df_short['Lower Band']
y99 = df_short['Upper Band']
plt.plot(x,y,label ='Close',color='black',alpha=0.6)
plt.plot(x,y1,label = '200ma',color='blue',alpha=0.8)
plt.plot(x,y3,label ='52W min',color='orange',alpha=0.3)
plt.plot(x,y4,label ='52W max',color='orange',alpha=0.3)
ax1.fill_between(x,y98,y99, color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')

for i in range(len(buy_date)):
    lw = 2.2
    try:
        y5 = df_short[(df_short['index']>=pd.to_datetime(buy_date).values[i])&(df_short['index']<=pd.to_datetime(sell_date).values[i])]['Close']
        x2 = df_short[(df_short['index']>=pd.to_datetime(buy_date).values[i])&(df_short['index']<=pd.to_datetime(sell_date).values[i])]['index']
        plt.plot(x2,y5,color='black',linewidth=lw)
        lw+=2.2
    except:
        pass


ax1.axvline(x=x.values[-1],color='black',alpha=0.4)
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

ax1.axhline(list(y)[-1],linestyle='dotted',color='black',label='today',lw=1.3)
label = str(round(list(y)[-1],2))
plt.annotate( label ,(list(x)[-1],list(y)[-1]) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')

value = round(100*(-list(y)[-1]+np.array(list(y)[-260:]).min())/list(y)[-1],1)
ytd_min = value
label = str(round(np.array(list(y)[-260:]).min(),2))
plt.annotate( label , (list(x)[-1],np.array(list(y)[-260:]).min()) , textcoords ="offset points" , xytext=(0,-10) , size = 9, ha='center')
label = str(value)+'%'
plt.annotate( label , (list(x)[-1],np.array(list(y)[-260:]).min()) , textcoords ="offset points" , xytext=(0,4) , size = 10, ha='center', weight='bold')


plt.title(ticker_list[ticker_list['ticker']==ticker]['name'].values[0].upper(),loc='left',fontweight='bold')
ax1.fill_between(df_short['index'], df_short['Smaller Lower Band'], df_short['Smaller Upper Band'], color='grey',alpha=0.1,label='bollinger-'+str(bol_period))
ymin, ymax = ax1.get_ylim() # get yaxis limits for boxplot below...


#plot future plots
forecast_days = 90
try:start = pd.to_datetime(buy_date.values[0])
except:start = list(df_short['index'])[-1]
try:end = pd.to_datetime(buy_date.values[0])+timedelta(days=forecast_days)
except:end = list(df_short['index'])[-1]+timedelta(days=forecast_days)
    
result = []
for i in range(0,250):
    np.random.seed(i)
    dist = np.random.choice( df_short['Close'].pct_change().dropna(),size=df_short['Close'].count() )
    new_dates=pd.date_range(start,end,freq='B')
    new_dist= np.random.choice(dist,size = len(new_dates) )
    df_future = pd.Series(new_dist,index=new_dates).add(1)
    df_future = df_short[df['index']==start].set_index('index')['Close'].append(df_future).cumprod()
    result.append((df_future.values[-1]-df_future.values[0])/df_future.values[0])

x_firstchart = ax1.get_xlim()

result = np.array(result)
for i in [np.quantile(result,0.15),np.quantile(result,0.5),np.quantile(result,0.85)]:
    forecast = np.linspace(df_future.values[0],\
                           df_future.values[0]*(1+i),len(new_dates)+1)
    plt.plot(df_future.index,forecast,color='black')
    label= str(round(i*100,1))+'%'
    plt.annotate( label , (df_future.index[-1],forecast[-1]) , textcoords ="offset points" , xytext=(4,0) , size = 10 ,color='black' , ha='left')

###########################################################################
# 3-month ror chart
x  = df_short['index']
y2 = 100*df_short['3mo_ror']
ax1 = fig3.add_subplot(gs[5:7, :-1])
ax1.plot(x,y2,color='black')
ax1.axhline(y=0,label='200ma',color='blue',alpha=0.35,lw=1.2)
ax1.axhline(y=y2.median(),label='mean',color='black',alpha=0.6,lw=1.2)
ax1.fill_between(df_short['index'], y2.mean()+y2.std()*2, y2.mean()-y2.std()*2, color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.fill_between(df_short['index'], y2.mean()+y2.std(), y2.mean()-y2.std(), color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.axvline(x=x.values[-1],color='black',alpha=0.4)
ax1.set_xlim(x_firstchart)
ax1.scatter(df_short[df_short.RSI<30]['index'],100*df_short[df_short.RSI<30]['3mo_ror'],color = 'limegreen',s=38,alpha=1)
ax1.scatter(df_short[df_short.RSI>70]['index'],100*df_short[df_short.RSI>70]['3mo_ror'],color = 'tomato',s=38,alpha=1)
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())

ymin, ymax = ax1.get_ylim()
bigger_max = abs(np.max([ymin,ymax]))
ax1.set_ylim([-bigger_max,bigger_max])
ymin, ymax = ax1.get_ylim()

try:
    df_temp = df_short[(df_short['index']>=pd.to_datetime(buy_date).values[0])&(df_short['index']<=pd.to_datetime(sell_date).values[0])]
    y5 = 100*df_temp['3mo_ror']
    x2 = df_temp['index']
    plt.plot(x2,y5,color='black',linewidth=2.2)
except:
    pass
    print('pass')

###########################################################################
# 3-month distribution chart

ax1 = fig3.add_subplot(gs[5:7, -1:])
sns.boxplot(result*100,orient='h')
ax1.axvline( 0,color='blue')
current_result = 100*(df['Close'].values[-1] - df['Close'].values[-65])/df['Close'].values[-65]
ax1.axvline(current_result,color='red')
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('3 month return')
plt.xlim([ymin,ymax])
percentile = int(ss.percentileofscore(result*100,current_result))
if percentile <50:
    plt.title(str(percentile)+'/100',loc='left',color='green')
else:
    plt.title(str(percentile)+'/100',loc='left',color='red')  
###########################################################################
# moving average chart

ax1 = fig3.add_subplot(gs[7:9, :-1])
x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']
ax1.plot(x,y2,label='Close/200ma',color='black',alpha=0.6)
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

x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']

ax1.fill_between(df_short['index'], y2.mean()+y2.std()*2, y2.mean()-y2.std()*2, color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.fill_between(df_short['index'], y2.mean()+y2.std(), y2.mean()-y2.std(), color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.axvline(x=x.values[-1],color='black',alpha=0.4)

x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']
if list(y2)[-1]>y2.mean(): label = '+'+str(round((list(y2)[-1]-y2.mean())/y2.std(),2))+' SD'
else: label = str(round((list(y2)[-1]-y2.mean())/y2.std(),2))+' SD'
plt.annotate( label , (list(x)[-1],np.array(y2.mean()+y2.std()*2.1)) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')
trend_sd = round((list(y2)[-1]-y2.mean())/y2.std(),2)
ax1.set_xlim(x_firstchart)

ymin, ymax = ax1.get_ylim()
bigger_max = abs(np.max([ymin,ymax]))
ax1.set_ylim([-bigger_max,bigger_max])
ymin, ymax = ax1.get_ylim()

try:
    df_temp = df_short[(df_short['index']>=pd.to_datetime(buy_date).values[0])&(df_short['index']<=pd.to_datetime(sell_date).values[0])]
    y5 = 100*(df_temp['Close']-df_temp['ma_200'])/df_temp['ma_200']
    x2 = df_temp['index']
    plt.plot(x2,y5,color='black',linewidth=2.2)
except:
    pass
    print('pass')
    
###########################################################################

ax1 = fig3.add_subplot(gs[7:9,-1:])
x = df_short['index']
y = 100*(df_short['ma_50']-df_short['ma_200'])/df_short['ma_200']
y2 = 100*(df_short['Close']-df_short['ma_200'])/df_short['ma_200']
sns.boxplot(y2,orient='h')
trend_percentile = int(ss.percentileofscore(y2, list(y2)[-1]))
trend_mean = round(y2.median(),1)
ax1.axvline(list(y2)[-1],color='red',label=str(trend_percentile)+'th perc')
ax1.xaxis.set_major_formatter(mtick.PercentFormatter() )
ax1.axvline(x=0,label='200ma',color='blue',alpha=0.35,lw=1.2)
plt.xlabel('% to 200ma')
plt.xlim([ymin,ymax])
if trend_percentile <50:
    plt.title(str(trend_percentile)+'/100',loc='left',color='green')
else:
    plt.title(str(trend_percentile)+'/100',loc='left',color='red')
###########################################################################

ax1 = fig3.add_subplot(gs[9:,:-1])
ax1.plot(df_short['index'],df_short.RSI,color = 'black',alpha=0.6,label='RSI '+str(period))
# plt.legend(prop={'size': 10},loc='upper left')
ax1.scatter(df_short[df_short.RSI<30]['index'],df_short[df_short.RSI<30].RSI,color = 'limegreen',s=38,alpha=1)
ax1.scatter(df_short[df_short.RSI>70]['index'],df_short[df_short.RSI>70].RSI,color = 'tomato',s=38,alpha=1)

ax1.axhline(y=50, color='blue',alpha=0.35,lw=1.2)

ax1.set_ylim([0,100])
ymin, ymax = ax1.get_ylim()
ax1.fill_between(df_short['index'], df_short['RSI'].mean()+df_short['RSI'].std()*2, df_short['RSI'].mean()-df_short['RSI'].std()*2, color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
ax1.fill_between(df_short['index'], df_short['RSI'].mean()+df_short['RSI'].std(), df_short['RSI'].mean()-df_short['RSI'].std(), color='grey',alpha=0.1,label='bollinger-'+str(bol_period)+' 1~2 SD')
if list(df_short['RSI'])[-1]>df_short['RSI'].mean(): label = '+'+str(round((list(df_short['RSI'])[-1]-df_short['RSI'].mean())/df_short['RSI'].std(),2))+' SD'
else: label = str(round((list(df_short['RSI'])[-1]-df_short['RSI'].mean())/df_short['RSI'].std(),2))+' SD'
plt.annotate( label , (list(df_short['index'])[-1],np.array(df_short['RSI'].mean()+df_short['RSI'].std()*2.1)) , textcoords ="offset points" , xytext=(0,4) , size = 9, ha='center')
rsi_sd = round((list(df_short['RSI'])[-1]-df_short['RSI'].mean())/df_short['RSI'].std(),2)
ax1.axhline(y=df_short.RSI.median(),color='black',alpha=0.6,lw=1.2)
median_rsi = df_short.RSI.median() 
ax1.set_xlim(x_firstchart)

try:
    df_temp = df_short[(df_short['index']>=pd.to_datetime(buy_date).values[0])&(df_short['index']<=pd.to_datetime(sell_date).values[0])]
    y5 = df_temp['RSI']
    x2 = df_temp['index']
    plt.plot(x2,y5,color='black',linewidth=2.2)
except:
    pass
    print('pass')
    
ax1.axvline(x=x.values[-1],color='black',alpha=0.4)
# ax1.axvline(x=x.values[-1]-np.timedelta64(365,'D'),color='black',alpha=0.4)
# ax1.axvline(x=x.values[-1]-np.timedelta64(365*2,'D'),color='black',alpha=0.4)
# ax1.axvline(x=x.values[-1]-np.timedelta64(365*3,'D'),color='black',alpha=0.4)
###########################################################################

ax1 = fig3.add_subplot(gs[9:,-1:])
sns.boxplot(df_short.RSI,orient='h')

ax1.axvline(list(df_short.RSI)[-1],color='red')
plt.xlim([ymin,ymax])
ax1.axvline(50, color='blue')
plt.xlabel('RSI')
rsi_percentile = int(ss.percentileofscore(df_short.RSI,list(df_short.RSI)[-1]))
if rsi_percentile <50:
    plt.title(str(rsi_percentile)+'/100',loc='left',color='green')
else:
    plt.title(str(rsi_percentile)+'/100',loc='left',color='red')  

ax1 = fig3.add_subplot(gs[:4, -1:])
plt.axis('off')


table_data=[df['Close'].values[-1].astype(int),
             df['ma_200'].values[-1].astype(int),
             str(round(result.mean()*100,1))+'%',
             str(round(np.quantile(result,0.15)*100,1))+'%',
             str(round(100*len(result[result>0])/len(result),1))+'%']
items = ['Price','200MA','Pred'+str(forecast_days),'StandDev','Success %']
plot_table = pd.DataFrame(table_data,columns =['Data'],index = items).reset_index()
table = ax1.table(cellText=plot_table.values, colLabels=plot_table.columns,loc='center left',colWidths=[0.5 for x in plot_table.columns])

cellDict = table.get_celld()
for i in range(0,len(plot_table.columns)):
    cellDict[(0,i)].set_height(.1)
    for j in range(1,len(plot_table.values)+1):
        cellDict[(j,i)].set_height(.1)
        
plt.tight_layout()

#Save charts
os.chdir(r'/Users/tehyuqi/dropbox/technical_charts')
plt.savefig(ticker_list[ticker_list['ticker']==ticker]['name'].values[0]+'.png')

if len(portfolio)>0 and (pd.Series(sell_date).isnull().values[0] or pd.Series(sell_date).values[0] != datetime.now().date()):
    os.chdir(r'/Users/tehyuqi/dropbox/portfolio_stocks')
    plt.savefig(ticker_list[ticker_list['ticker']==ticker]['name'].values[0]+'.png')
    
if ticker_list[ticker_list.ticker==ticker]['file'].values[0] == 'p1':
    os.chdir(r'/Users/tehyuqi/dropbox/p1')
    plt.savefig(ticker_list[ticker_list['ticker']==ticker]['name'].values[0]+'.png')

os.chdir(summary_dir)

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
    
##########################################################################################################################################
#update data onto summary sheet

os.chdir(summary_dir)

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
newdata.append(round(result.mean()*100,2))
newdata.append(round(result.std()*100,2))
newdata.append(round(100*len(result[result>0])/len(result),2))
newdata.append(100*(df['Close'].values[-1] - df['Close'].values[-65])/df['Close'].values[-65])

# 'Pred'+str(forecast_days),'StandDev','Success %'
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
    
record.to_csv('records.csv',index=False)

try: 
    ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%Y-%m-%d') if type(x) == str else datetime(1990,1,1).date())
except:
    try: ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%m/%d/%Y') if type(x) == str else datetime(1990,1,1).date())
    except:
        try: ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%d/%m/%y') if type(x) == str else datetime(1990,1,1).date())
        except:
            try:
                ticker_list.last_date_analysis  = ticker_list.last_date_analysis.apply(lambda x: datetime.strptime(x,'%m/%d/%y') if type(x) == str else datetime(1990,1,1).date())
            except:
                pass
    
try:
    if (list(ticker_list[ticker_list.ticker==ticker].last_date_analysis)[-1] < list(df_short2['index'][-1:])[-1].date()):
        ticker_loc = list(ticker_list[ticker_list.ticker==ticker].index)[-1]
        ticker_analysis_date = list(ticker_list.last_date_analysis.fillna(0))
        ticker_analysis_date[ ticker_loc] =  list(df_short2['index'][-1:])[-1].date()
        ticker_list['last_date_analysis'] = ticker_analysis_date
        print('updating ticker_list...')
except:
    print('fail to update dates..')

ticker_list.to_csv('tickers.csv',index=False)
    
#######################################################################################################################################