import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from datetime import datetime, timedelta
import warnings
import re
import seaborn as sns
warnings.filterwarnings('ignore')
plt.style.use('seaborn-whitegrid')

os.chdir(r'/Users/tehyuqi/Dropbox')
df = pd.read_csv('tickers.csv')

all_industry = df[['industry','ticker','name']]
all_tickers = df.ticker.unique()

print('getting US-only stocks..')
k=0
for i in all_tickers:
    if not ('.hk' in i or '.si' in i):
        try:
            
            os.chdir(r'/Users/tehyuqi/stockdata/stock_data')
            df = pd.read_csv(i+ '_income.csv')
            income = df.set_index('title').T
            income.columns = [re.sub(' ','',i) for i in income.columns]
            income['ticker'] = i
            
            os.chdir(r'/Users/tehyuqi/stockdata')
            df = pd.read_csv(i+'_data.csv')
            df['index'] = pd.to_datetime(df['index'])
            df['year'] = df['index'].apply(lambda x: x.year)       
            
            df['trend'] = 100*(df['Close'].sub(df['ma_200'])).div(df['ma_200'])
                
            income['price'] = df['Close'].values[-1]
            income['trend'] = df['trend'].round(2).values[-1]
            
            if k==0:
                total = income.loc[[],:]
            k+=1
            total = pd.concat([total,income])
            print(i)
        except:
            pass
            print(i,'fail..')

print('transforming data..')
output = total[~total['GrossIncome'].isnull()]
output = output[~output.index.isin(['no','Unnamed: 1'])]
output = output.merge(all_industry,how='left',left_on='ticker',right_on='ticker')

for i in output.columns:
    if output[i].isnull().sum() > 0:
        output = output.drop(columns=[i])

latest = output.reset_index()
latest['index'] = pd.to_datetime(latest['index'])
latest['rank'] = latest.groupby('ticker')['index'].rank(ascending=False)
latest = latest[latest['rank']==1]
latest['PE_ratio'] = latest['price'].div(latest['EPS(Basic)']).round(1).add(1).apply(np.log)
latest['PS_ratio'] = latest['price']\
.div(latest['Sales/Revenue'].div(latest['BasicSharesOutstanding'])).round(1).abs().add(1).apply(np.log)
latest['Market_Cap'] =latest['price']*latest['BasicSharesOutstanding'].add(1)


os.chdir(r'/Users/tehyuqi/Dropbox')
latest[['ticker','PE_ratio','PS_ratio','trend']].to_csv('deleteme.csv',index=False)

print('plotting data..')
print('ps ratio chart')
plt.figure(figsize=(19,8.5))
plt.clf()
ax1=plt.subplot(1,2,1)
for i in latest['industry'].unique():
    subgroup = latest[(latest['industry']==i)]
    plt.scatter(subgroup['trend'],subgroup['PS_ratio'],label=i,alpha=0.65)
plt.legend()
plt.axhline(1,color='black',alpha=0.2)
plt.axvline(0,color='black',alpha=0.2)

ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('P/S Ratio',fontweight='bold')

for x, y in zip( latest['trend'] ,latest['PS_ratio']):
    company_name = list(latest[(latest['trend']==x)&(latest['PS_ratio']==y)]['name'])[-1]
    value = int(np.exp(latest[latest.name==company_name]['PS_ratio'].values[0])-1)
    if value >= 1:
        value = int(np.exp(latest[latest.name==company_name]['PS_ratio'].values[0])-1)
    else:
        value = round(np.exp(latest[latest.name==company_name]['PS_ratio'].values[0])-1,1)    
    label = company_name + ' ' + str(value)
    plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')

ax1.set_yticklabels(np.exp(plt.yticks()[0]).astype(int)-1)  
ax1.set_yticklabels(np.exp(plt.yticks()[0]).astype(int)-1)
m,b = np.polyfit(np.array(latest['trend']),np.array(latest['PS_ratio']),1)
latest['model'] = latest['trend'].mul(m).add(b)
plt.plot(latest['trend'],m*latest['trend']+b,label='fit',color='black',alpha=0.4)
sns.regplot(latest['trend'],latest['PS_ratio'],x_ci=99,scatter=False, line_kws={'alpha': 0})

print('pe ratio chart')
ax1=plt.subplot(1,2,2)
for i in latest['industry'].unique():
    subgroup = latest[(latest['industry']==i)]
    plt.scatter(subgroup['trend'],subgroup['PE_ratio'],label=i,alpha=0.65)
plt.legend()
plt.axhline(1,color='black',alpha=0.2)
plt.axvline(0,color='black',alpha=0.2)
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('P/E Ratio',fontweight='bold')

m,b = np.polyfit(np.array(latest['trend']),np.array(latest['PE_ratio']),1)
latest['model'] = latest['trend'].mul(m).add(b)
plt.plot(latest['trend'],m*latest['trend']+b,label='fit',color='black',alpha=0.4)
sns.regplot(latest['trend'],latest['PE_ratio'],x_ci=99,scatter=False, line_kws={'alpha': 0})

#annotating
for x, y in zip( latest['trend'] ,latest['PE_ratio']):
    company_name = list(latest[(latest['trend']==x)&(latest['PE_ratio']==y)]['name'])[-1]
    value = int(np.exp(latest[latest.name==company_name]['PE_ratio'].values[0])-1)
    label = company_name + ' ' + str(value)
    plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')
try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')
    
plt.tight_layout()
plt.savefig('ps_pe.png')

plt.figure(figsize=(19,8.5))
plt.clf()
print('market cap chart')
ax1=plt.subplot(1,2,1)
for i in latest['industry'].unique():
    subgroup = latest[(latest['industry']==i)]
    plt.scatter(subgroup['trend'],subgroup['EBITDAMargin'],label=i,alpha=0.65)
plt.legend()
plt.axhline(0,color='black',alpha=0.2)
plt.axvline(0,color='black',alpha=0.2)
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('EBITDAMargin (Billions)',fontweight='bold')

#annotating
for x, y in zip( latest['trend'] ,latest['EBITDAMargin']):
    company_name = list(latest[(latest['trend']==x)&(latest['EBITDAMargin']==y)]['name'])[-1]
    value = round(latest[latest.name==company_name]['EBITDAMargin'].values[0],1)
    label = company_name + ' ' + str(value)
    plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')

ax1=plt.subplot(1,2,2)
for i in latest['industry'].unique():
    subgroup = latest[(latest['industry']==i)]
    plt.scatter(subgroup['trend'],subgroup['EBITDAGrowth'],label=i,alpha=0.65)
plt.legend()
plt.axhline(0,color='black',alpha=0.2)
plt.axvline(0,color='black',alpha=0.2)
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('EBITDAGrowth (Billions)',fontweight='bold')

#annotating
for x, y in zip( latest['trend'] ,latest['EBITDAGrowth']):
    company_name = list(latest[(latest['trend']==x)&(latest['EBITDAGrowth']==y)]['name'])[-1]
    value = round(latest[latest.name==company_name]['EBITDAGrowth'].values[0],1)
    label = company_name + ' ' + str(value)
    plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')



plt.tight_layout()
plt.savefig('ebidta.png')
