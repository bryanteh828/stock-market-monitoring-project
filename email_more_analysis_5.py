# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:13:41 2020

@author: USER
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

########################################################################################################
#Import
try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')

df = pd.read_csv('records_2.csv')
plt.style.use('bmh')

########################################################################################################
#Preprocessing
df.industry.value_counts()
df['fewer_industry'] = df.industry.apply(lambda x: 'tech' if 'tech' in x else 'bank' if 'bank' in x else 'travel' if 'travel' in x else 'index' if 'index' in x else 'semicon'if 'semicon' in x else 'manufacturing' if 'manufacturing' in x else 'others')

########################################################################################################
#plotting
group = 'fewer_industry'

#################

m,b = np.polyfit(np.array(df['trend_mean']),np.array(df['ytd_max']),1)
plt.figure(figsize=(19,9))
plt.clf()
ax1 = plt.subplot(1,2,1)
plt.title('Date: ' + df['date_of_analysis'].str.split(' ').str.get(0).max(),loc='left',fontweight='bold')
for i in df[group].unique():
    plt.scatter(df[df[group]==i]['trend_mean'],df[df[group]==i]['ytd_max'],label=i,alpha=0.65)
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('Momentum ~ RSI-14 days (range 0:100)',fontweight='bold')

for x, y in zip( df['trend_mean'] ,df['ytd_max']):
  label = list(df[(df['trend_mean']==x)&(df['ytd_max']==y)]['name'])[-1]
  print(label)
  plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')
  

plt.axhline(list(df[df['name']=='sp500']['ytd_max'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='sp500']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axhline(list(df[df['name']=='hangseng']['ytd_max'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='hangseng']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.legend()
plt.plot(df['trend_mean'],m*df['trend_mean']+b,label='fit',color='black',alpha=0.04)
sns.regplot(df['trend_mean'],df['ytd_max'],x_ci=99,scatter=False, line_kws={'alpha': 0})
plt.ylabel('% gap to YTD high')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
# sns.regplot(df['trend_mean'],df['rsi14'],x_ci='ci',scatter=False,color='black',line_kws={'alpha':0.01})
#################
m,b = np.polyfit(np.array(df['trend_mean']),np.array(df['ytd_min']),1)


ax1 = plt.subplot(1,2,2)
for i in df[group].unique():
    plt.scatter(df[df[group]==i]['trend_mean'],df[df[group]==i]['ytd_min'],label=i,alpha=0.65)
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('Discount ~ /200MA (range -1:1)',fontweight='bold')
    
plt.plot(df['trend_mean'],m*df['trend_mean']+b,label='fit',color='black',alpha=0.04)
plt.axhline(list(df[df['name']=='sp500']['ytd_min'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='sp500']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axhline(list(df[df['name']=='hangseng']['ytd_min'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='hangseng']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')

sns.regplot(df['trend_mean'],df['ytd_min'],x_ci=99,scatter=False, line_kws={'alpha': 0})
for x, y in zip( df['trend_mean'] ,df['ytd_min']):
      label = list(df[(df['trend_mean']==x)&(df['ytd_min']==y)]['name'])[-1]
      print(label)
      plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,7.5) , size = 7.5 , ha='center')
plt.gca().invert_yaxis()
plt.ylabel('% gap to YTD low')
# print('sp500 momentum',list(df.rsi14[df.ticker=='^gspc'])[-1])
# print('hang seng momentum',list(df.rsi14[df.ticker=='^hsi'])[-1])
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')
plt.savefig('overall_5.png')
