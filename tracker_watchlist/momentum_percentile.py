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

#Import
input_dir = r'/Users/tehyuqi/dropbox'
output_dir = r'/Users/tehyuqi/stockdata'
output_chart = 'momentum_percentile.png'

os.chdir(input_dir)

df = pd.read_csv('records.csv')
plt.style.use('seaborn-whitegrid')

#Preprocessing
df.industry.value_counts()
df['fewer_industry'] = df.industry.apply(lambda x: 
                                         'tech' if 'tech' in x else 
                                         'bank' if 'bank' in x else 
                                         'travel' if 'travel' in x else 
                                         'index' if 'index' in x else 
                                         'semicon'if 'semicon' in x else 
                                         'manufacturing' if 'manufacturing' in x else 
                                         'supermarket' if 'supermarket' in x else
                                         'others')

#plotting
group = 'fewer_industry'

#################
plt.figure(figsize=(19,8.5))
plt.clf()
ax1 = plt.subplot(1,2,1)
col = 'rsi_percentile'
m,b = np.polyfit(np.array(df['trend_mean']),np.array(df[col]),1)
df['model'] = df['trend_mean'].mul(m).add(b)
df['below'] = df.apply(lambda x: 1 if x[col] <= x['model'] else 0,axis=1)


plt.title('Date: ' + df['date_of_analysis'].str.split(' ').str.get(0).max(),loc='left',fontweight='bold')
for i in df[group].unique():
    subgroup = df[(df[group]==i)&(df['below']==1)]
    plt.scatter(subgroup['trend_mean'],subgroup[col],label=i,alpha=0.75)
for i in df[group].unique():
    subgroup = df[(df[group]==i)&(df['below']==0)]
    plt.scatter(subgroup['trend_mean'],subgroup[col],label=i,alpha=0.25)
    
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('Momentum ~ RSI-14 days (range 0:100)',fontweight='bold')
ax1.axhline(y=50,alpha=0.4,color='black')
ax1.axvline(x=0,alpha=0.4,color='black')
for x, y in zip( df['trend_mean'] ,df[col]):
  label = list(df[(df['trend_mean']==x)&(df[col]==y)]['name'])[-1]
  print(label)
  plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')
  
plt.axhline(list(df[df['name']=='sp500'][col])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='sp500']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axhline(list(df[df['name']=='hangseng'][col])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='hangseng']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.legend()
plt.plot(df['trend_mean'],m*df['trend_mean']+b,label='fit',color='black',alpha=0.4)
sns.regplot(df['trend_mean'],df[col],x_ci=99,scatter=False, line_kws={'alpha': 0})
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
#################
ax1 = plt.subplot(1,2,2)
col = 'trend_percentile'
m,b = np.polyfit(np.array(df['trend_mean']),np.array(df[col]),1)
df['model'] = df['trend_mean'].mul(m).add(b)
df['below'] = df.apply(lambda x: 1 if x[col] <= x['model'] else 0,axis=1)


plt.title('Date: ' + df['date_of_analysis'].str.split(' ').str.get(0).max(),loc='left',fontweight='bold')
for i in df[group].unique():
    subgroup = df[(df[group]==i)&(df['below']==1)]
    plt.scatter(subgroup['trend_mean'],subgroup[col],label=i,alpha=0.75)
for i in df[group].unique():
    subgroup = df[(df[group]==i)&(df['below']==0)]
    plt.scatter(subgroup['trend_mean'],subgroup[col],label=i,alpha=0.25)
    
plt.xlabel('Trend ~ 200MA of 5 years (range -1:1)',fontweight='bold')
plt.ylabel('Momentum ~ RSI-14 days (range 0:100)',fontweight='bold')
ax1.axhline(y=50,alpha=0.4,color='black')
ax1.axvline(x=0,alpha=0.4,color='black')
for x, y in zip( df['trend_mean'] ,df[col]):
  label = list(df[(df['trend_mean']==x)&(df[col]==y)]['name'])[-1]
  print(label)
  plt.annotate( label , (x,y) , textcoords ="offset points" , xytext=(0,8) , size = 7.5, ha='center')
  
plt.axhline(list(df[df['name']=='sp500'][col])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='sp500']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.axhline(list(df[df['name']=='hangseng'][col])[-1],color='green',alpha=0.13,linestyle='--')
plt.axvline(list(df[df['name']=='hangseng']['trend_mean'])[-1],color='green',alpha=0.13,linestyle='--')
plt.legend()
plt.plot(df['trend_mean'],m*df['trend_mean']+b,label='fit',color='black',alpha=0.4)
sns.regplot(df['trend_mean'],df[col],x_ci=99,scatter=False, line_kws={'alpha': 0})
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()

os.chdir(output_dir)
plt.savefig(output_chart)
