import os
import sys
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt ; plt.style.use('ggplot')
import matplotlib.ticker as mtick
import seaborn as sns ; sns.set()

pull_data = False
input_dir = r'/Users/tehyuqi/dropbox'
output_dir = r'/Users/tehyuqi/dropbox'

"""
OUTPUT is DASHBOARD of PORTFOLIO
TWO INPUTS needed (1)ticker + stock name; (2)transaction records

(1)sample
country	name	industry	ticker
us	thetradedesk	tech	ttd
us	uber	tech	uber
us	equinix	tech	eqix
us	oracle	tech	orcl
us	paypal	tech	pypl

(2)sample
name	ticker	purchase_date	stockprice	stocks	cost	unitcost	cost_sgd	price	duration	appreciation	lastday_price	market_value
adobe	adbe	14/7/20	438.3407407	27	11835.2	438.3407407	16574.01408		163	13.7	498.5400085	18849.62621
alibaba	baba	4/8/20	240.3313253	83	19947.5	244.2491959	27868.35142		141.5	-7.4	221.7098999	25816.61929
costco	cost	9/6/20	309.2359375	32	9895.55	309.2359375	13783.86783		198	17.2	362.5499878	16160.20665
"""

#Tickers
os.chdir(input_dir)
temp = pd.read_csv('tickers.csv')

#Purchases
df = pd.read_csv('transactions.csv')
#sample


try: 
    df['purchase_date'] = df['purchase_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
except:
    df['purchase_date'] = df['purchase_date'].apply(lambda x: datetime.strptime(x, '%d/%m/%y'))

#Pull Tickers [if needed]
tickers_needed = list(df.loc[ df['price'].isnull() ] .ticker.unique()) + ['^gspc','^hsi']
scripts_needed = ['price_pull.py','price_anlys.py']
if pull_data == True:
    for ticker in tickers_needed:
        print('pulling',ticker,'...')
        for script in scripts_needed:
            try: 
                os.system(r'python3 ' + script +' '+ticker)
            except: 
                sys.exit('Script error')

#Summary of position
df = df.loc[df['price'].isnull()]

df.purchase_date = pd.to_numeric(df.purchase_date)
df = df.groupby(['name','ticker']).agg({
    'purchase_date':'mean',
    'stockprice':'mean',
    'stocks':'sum',
    'cost':'sum',
    'unitcost':'mean',
    'duration':'mean',
    'appreciation':'mean',
    'price':'mean',
    'lastday_price':'mean',
    'market_value':'sum'
    }).reset_index()

df['stockprice']=df['cost'].div(df['stocks'])
# df['appreciation']=df['market_value'].div(df['cost']).sub(1).mul(100).round(1)
df.purchase_date = pd.to_datetime(df.purchase_date)

#Prices of position
k=0
for current_ticker in df.ticker.unique():

    try: 
        current_purchase_date = list(df[df.ticker==current_ticker]['purchase_date'])[-1]
    except: 
        pass
    
    print(current_ticker,current_purchase_date.date())   

    #get data
    os.chdir(r'/Users/tehyuqi/stockdata')
    df2 = pd.read_csv(current_ticker + '_data.csv')
    df2['index'] = df2['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    
    #new columns
    cost_of_purchase = df[df['ticker'] == current_ticker]['unitcost'].values[0]
    df2['appreciation']= df2['Close'].div(cost_of_purchase).sub(1)
    df2['ticker'] = current_ticker
    df2['name'] = temp[temp.ticker == current_ticker]['name'].values[0]
        
    #three years
    df2_long = df2.copy()
    years = 3
    period = list(df2_long['index'])[-1] - timedelta(days = 365 * years)
    df2_long = df2_long[df2_long['index'] > period]
    
    #only purchased
    df2 = df2[df2['index'] > current_purchase_date]
    
    #get index [as benchmark]
    if '.hk' in current_ticker: 
        df3 = pd.read_csv('^hsi'+'_data.csv')
    else: 
        df3 = pd.read_csv('^gspc'+'_data.csv')
    
    df3['index'] = df3['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df3 = df3[df3['index'] > current_purchase_date]
    df3['appreciation']=df3['Close']/list(df3['Close'])[-0] - 1
    
    #join index
    df2['market_RSI'] = list(df3['RSI'])
    df2['market'] = list(df3['appreciation'])
    df2['market_ma_200'] = list(df3['ma_200'])
    df2['market_price'] = list(df3['Close'])
    
    #output
    if k==0:
        df_copy = df2.iloc[[],:]
        df_copy_long = df2.iloc[[],:]
    df_copy = pd.concat([df_copy,df2])
    df_copy_long = pd.concat([df_copy_long,df2_long])
    k+=1 

#first price
first_price = {}
for k in df.ticker.unique():
    first_price[k] = df[df.ticker==k].unitcost.values[0]

last_price = {}
for k in df.ticker.unique():
    last_price[k] = df_copy_long[df_copy_long.ticker==k].Close.values[-1]

df['lastday_price'] = df['ticker'].apply(lambda x: last_price[x]) 
df['market_value'] = df['lastday_price'].mul(df['stocks'])
df['appreciation'] = df['lastday_price'].sub(df['stockprice']).div(df['stockprice']).mul(100).round(1)
df['duration'] = (datetime.now() - df['purchase_date']).apply(lambda x: x.days)
#purchase date
#total
purchase_date = {}
k=0
for i in df.ticker.unique():
    purchase = df[df.ticker==i].purchase_date.min()
    if k==0:
        total = df_copy.loc[[],['Close','index','ticker']]
        k+=1
        
    target = df_copy_long[(df_copy_long.ticker==i)&\
                          (df_copy_long['index']>=purchase)][['Close','index','ticker']]
    purchase_date[i] = target.reset_index(drop=True).loc[0,'index']
    total = pd.concat([total,target])
    
total = total.merge(df[['ticker','stocks']],how='left',left_on='ticker',right_on='ticker')
total['value'] = total['Close'].mul(total['stocks']).mul(1.35)
total['first_price'] = total.ticker.apply(lambda x: first_price[x])
total['rate'] = total['Close'].div(total['first_price']) 
total['cost'] = total['first_price'].mul(total['stocks']).mul(1.35)

#plot
fig3 = plt.figure(figsize=[18,8])
gs = fig3.add_gridspec(8, 9)

# add colour
color = sns.color_palette("deep")
color.append((0.45, 0.45, 0.45))
color.append((0.6, 0.6, 0.6))

#portfolio
ax1 = fig3.add_subplot(gs[:4, :5])
plt.xticks(rotation=0)
summary = total.groupby('index').agg({'value':sum,'cost':sum})
summary['perc'] = summary['value'].div(summary['cost']).sub(1).mul(100).rolling(5).mean()
summary[['value','cost']].plot(ax=ax1,alpha=0.75,linewidth=2.1,rot=0)
ax1b = ax1.twinx()
summary[['perc']].plot(ax=ax1b,color='grey',alpha=0.5,linewidth=2.1,rot=0)

# ax1.axes.set_yticklabels([str(int(i/1000))+'K' for i in ax1.axes.get_yticks()])
ax1.grid(b=None)
ax1b.grid(b=None)
ax1b.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.legend([])
plt.title('Portfolio >>',loc='left',fontweight='bold')

#individual stock
ax1 = fig3.add_subplot(gs[4:, :5])
plt.title('Individual Stocks >>',loc='left',fontweight='bold')
i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = df_copy[df_copy.ticker==j]['appreciation']*100
    label = list(df_copy[df_copy.ticker==j]['name'])[0]
    plt.plot(x,y,color=color[i],label=label,alpha=0.75,linewidth=2.1)
    if y.values[-1]<0: label = str(round(y.values[-1],1))+'%'+' '+j
    else: label = '+'+str(round(y.values[-1],1))+'%'+'  '+j
    plt.annotate(label , (x.values[-1],y.values[-1]) , textcoords ="offset points" \
                 , xytext=(45,0), size =13 , ha='center',color=color[i])
    i+=1
plt.axhline(y=0,color='black',alpha=0.4)
plt.legend(loc='upper left',prop={"size":11.5})


i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = df_copy[df_copy.ticker==j]['market']*100
    plt.plot(x,y,color=color[i],alpha=0)
    i+=1
weekday = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

ax1b = ax1.twinx()
ax1b.set_ylim(tuple(np.array([ax1.get_ylim()[0],ax1.get_ylim()[1]])))
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1b.axes.get_yaxis().set_ticks([])
ax1b.axhline(y=0,color='black',alpha=0.4)
ax1.grid(b=None)

#add index
temp = pd.read_csv('^hsi'+'_data.csv')
temp['ticker']='^hsi'
temp['name'] = 'hangseng'
temp['index'] = temp['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
temp = temp[temp['index']>list(temp['index'])[-1]-timedelta(365*3)]
df_copy_long_temp = pd.concat([df_copy_long,temp])

temp = pd.read_csv('^gspc'+'_data.csv')
temp['ticker']='^gspc'
temp['name'] = 'sp500'
temp['index'] = temp['index'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
temp = temp[temp['index']>list(temp['index'])[-1]-timedelta(365*3)]
df_copy_long_temp = pd.concat([df_copy_long_temp,temp])

market_rsi_sd = []
for i in ['^hsi','^gspc']:
    mean = df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'].mean()
    std = df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'].std()
    last_day = list(df_copy_long_temp[df_copy_long_temp['ticker']==i]['RSI'])[-1]
    market_rsi_sd.append(round((last_day-mean)/std,1))

#Trend
ax1 = fig3.add_subplot(gs[4:, 5:])
plt.title('Stock Trend >>',loc='left',fontweight='bold')
i=0
for j in df_copy.ticker.unique():
    x = df_copy[df_copy.ticker==j]['index']
    y = 100*(df_copy[df_copy.ticker==j]['Close'] - df_copy[df_copy.ticker==j]['ma_200'])/df_copy[df_copy.ticker==j]['ma_200']
    y2 = 100*(df_copy[df_copy.ticker==j]['market_price'] - df_copy[df_copy.ticker==j]['market_ma_200'])/df_copy[df_copy.ticker==j]['market_ma_200']
    plt.plot(x,y,color=color[i],label=j,linewidth=2.1,alpha=0.75)
    if '.hk' in j: plt.plot(x,y2,color=color[-1],label=j+' control',alpha=.6,linewidth=1.9)
    else: plt.plot(x,y2,color=color[-2],label=j+' control',alpha=.6,linewidth=1.9)
    i+=1
plt.axhline(y=0,color='black',alpha=0.4)
ax1b = ax1.twinx()
ax1b.set_ylim(tuple(np.array([ax1.get_ylim()[0],ax1.get_ylim()[1]])))
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1b.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1.axes.get_yaxis().set_ticks([])
ax1.grid(b=None)
ax1b.grid(b=None)

df_copy_long_temp['trend_gap'] = 100*(df_copy_long_temp['Close'] - df_copy_long_temp['ma_200'])/df_copy_long_temp['ma_200']
df_copy_long['trend_gap'] = 100*(df_copy_long['Close'] - df_copy_long['ma_200'])/df_copy_long['ma_200']
x = 'name'
y = 'trend_gap'

market_trend_sd = []
for i in ['^hsi','^gspc']:
    mean = df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'].mean()
    std = df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'].std()
    last_day = list(df_copy_long_temp[df_copy_long_temp['ticker']==i]['trend_gap'])[-1]
    market_trend_sd.append(round((last_day-mean)/std,1))

#Table
market_beat = []
rsi = []
trend = []
rsi_sd = []
trend_sd = []
for i in df_copy.ticker.unique():
    market_beat.append(str(round(100*(list(df_copy[df_copy.ticker==i]['appreciation'])[-1]\
                        -list(df_copy[df_copy.ticker==i]['market'])[-1]),1))+'%')
        
    rsi.append(round(list(df_copy_long[df_copy_long.ticker==i]['RSI'])[-1]))
    
    trend.append(str(round(list(df_copy_long[df_copy_long.ticker==i]\
                                ['trend_gap'])[-1],1))+'%')

    mean = df_copy_long[df_copy_long.ticker==i]['RSI'].mean()
    std = df_copy_long[df_copy_long.ticker==i]['RSI'].std()
    rsi_sd.append(round((list(df_copy[df_copy.ticker==i]['RSI'])[-1]-mean)/std,1))
    
    mean = df_copy_long[df_copy_long.ticker==i]['trend_gap'].mean()
    std = df_copy_long[df_copy_long.ticker==i]['trend_gap'].std()
    last_day = list(df_copy_long[df_copy_long.ticker==i]['trend_gap'])[-1]
    trend_sd.append(round((last_day-mean)/std,1))                             

df_plot_table =df.loc[df['price'].isnull()][['ticker','name','unitcost','duration','appreciation',\
                   'cost','lastday_price','market_value']]
    
df_plot_table['name'] = df_copy.ticker.unique()
df_plot_table['market +/-'] = market_beat
df_plot_table['rsi'] = rsi
df_plot_table['trend gap'] = trend
df_plot_table['rsi STD'] = rsi_sd
df_plot_table['trend STD'] = trend_sd

df_plot_table['market rsi STD'] = df_plot_table.apply(lambda x: market_rsi_sd[0] if '.hk' \
                                                      in x['ticker'] else market_rsi_sd[1],\
                                                      axis=1)
df_plot_table['market trend STD'] = df_plot_table.apply(lambda x: market_trend_sd[0] if \
                                                        '.hk' in x['ticker'] else \
                                                        market_trend_sd[1],axis=1)
df_plot_table['appreciation'] = df_plot_table['appreciation'].apply(lambda x: str(x)+'%')
df_plot_table['cost'] = df_plot_table['cost'].apply(lambda x: int(x))
df_plot_table['market_value'] = df_plot_table['market_value'].apply(lambda x: int(x))

for i in ['unitcost','lastday_price']:
    df_plot_table[i] = df_plot_table[i].apply(lambda x: round(x,2))

df_plot_table.columns = ['Ticker','Name','Cost','Days','Profit','Cost Val','Current',\
                         'Cur Val','Market +/-','RSI','Trend','RSI sd','Trend sd',\
                         'M RSI sd','M Trend sd']
    
df_plot_table['Total Profit']=df_plot_table['Cur Val']-df_plot_table['Cost Val']
plot_table = df_plot_table[['Name','Days','Current','Cost','Profit', 'Cost Val',\
                            'Total Profit','Market +/-']]
plot_table = plot_table.sort_values('Total Profit',ascending = False)
    
ax1 = fig3.add_subplot(gs[:2,5:])
table =ax1.table(cellText=plot_table.values, colLabels=plot_table.columns, \
                 loc='upper left',colWidths=[(0.018*len(plot_table[x].astype(str).max()))\
                 if (0.018*len(plot_table[x].astype(str).max())) > 0.13 else 0.13 \
                 for x in plot_table.columns])

cellDict = table.get_celld()
for i in range(0,len(plot_table.columns)):
    cellDict[(0,i)].set_height(.18)
    for j in range(1,len(plot_table.values)+1):
        cellDict[(j,i)].set_height(.165)

for j in range(0,len(plot_table)):
    # table[(j+1,0)].set_facecolor(color[j])
    for i in range(1,len(plot_table.columns)):
        if i != 6: table[(j+1),i]._loc = 'center'
        else: table[(j+1),i]._loc = 'right'
    if plot_table.values[j,4][0] == '-' : table[(j+1,4)]._text.set_color('red')
    else: table[(j+1,4)]._text.set_color('green')
    if plot_table.values[j,7][0] == '-' : table[(j+1,7)]._text.set_color('red')
    else: table[(j+1,7)]._text.set_color('green')
    if plot_table.values[j,6] < 0 : table[(j+1,6)]._text.set_color('red')
    else: table[(j+1,6)]._text.set_color('green')


        
table.auto_set_font_size(False)
table.set_fontsize(10.5)
plt.axis('off')

#Tables
ax1 = fig3.add_subplot(gs[2:4, 5:])

plot_table = df_plot_table[['Name', 'Trend','Trend sd',\
                            'RSI', 'RSI sd','M Trend sd','M RSI sd']]
table =ax1.table(cellText=plot_table.values, colLabels=plot_table.columns, \
                 loc='upper left',colWidths=[(0.018*len(plot_table[x].astype(str).max()))\
                 if (0.018*len(plot_table[x].astype(str).max())) > 0.13 else 0.13 \
                 for x in plot_table.columns])

cellDict = table.get_celld()
for i in range(0,len(plot_table.columns)):
    cellDict[(0,i)].set_height(.18)
    for j in range(1,len(plot_table.values)+1):
        cellDict[(j,i)].set_height(.165)               
        
for j in range(len(plot_table)):
    for i in range(2,len(plot_table.columns)):
        table[(j+1,i)]._loc = 'center'
        if i == 3:
            if plot_table.values[j,i] < 50: table[(j+1,i)]._text.set_color('red')
            else: table[(j+1,i)]._text.set_color('green')            
        else:
            if plot_table.values[j,i] < 0: table[(j+1,i)]._text.set_color('red')
            else: table[(j+1,i)]._text.set_color('green')
             
for j in range(len(plot_table)):
    if plot_table.values[j,1][0] == '-': table[(j+1,1)]._text.set_color('red')
    else: table[(j+1,1)]._text.set_color('green')
    table[(j+1,1)]._loc = 'center'

table.auto_set_font_size(False)
table.set_fontsize(10.5)
plt.axis('off')

plt.tight_layout()
plt.show()


os.chdir(output_dir)
plt.savefig('portfolio.png')
#################################################################################