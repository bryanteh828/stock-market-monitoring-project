import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from datetime import datetime
import pandas as pd

# 1 - set directory

charts = ['momentum.png',
          'momentum_percentile.png',
          'ytd.png',
          'ebidta.png',
          'ps_pe.png']

csv_input_dir = r'/Users/tehyuqi/dropbox'
chart_input_dir = r'/Users/tehyuqi/stockdata'

# 2 - read datatable
os.chdir(csv_input_dir)
ticker_list = pd.read_csv('tickers.csv')
watch_list = list(ticker_list[ticker_list.watchlist=='yes']['name'])

df = pd.read_csv('records.csv')
df['performance'] = df['performance'].astype(int)
df['pred_winrate'] = df['pred_winrate'].div(100).round(2)
df['performance_sd'] = df['performance'].sub(df['pred_mean']).div(df['pred_std']).round(1)

transactions = pd.read_csv('transactions.csv')
purchased_tickers = list(transactions['name'].unique())

html = """\
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
    padding: 3px;
    border-collapse: collapse;
    border-bottom: 1px solid #ddd;
    word-break: break-word;
}

table { table-layout: fixed; display: inline; width:50%;font-size: 11px}
table tr th:nth-child(1) {width: 13%}
table tr th:nth-child(2) {width: 13%}
table tr th:nth-child(3) {width: 8%}
table tr th:nth-child(4) {width: 8%}
table tr th:nth-child(5) {width: 8%}
table tr th:nth-child(6) {width: 6%}
table tr th:nth-child(7) {width: 8%}
table tr th:nth-child(8) {width: 6%}
table tr th:nth-child(9) {width: 8%}
table tr th:nth-child(10) {width: 8%}
table tr th:nth-child(11) {width: 6%}
table tr th:nth-child(12) {width: 8%}

table tr td:nth-child(3) {text-align: left}
table tr td:nth-child(4) {text-align: center}
table tr td:nth-child(5) {text-align: center}
table tr td:nth-child(6) {text-align: center}
table tr td:nth-child(7) {text-align: center}
table tr td:nth-child(8) {text-align: center}
table tr td:nth-child(9) {text-align: center}
table tr td:nth-child(10) {text-align: center}
table tr td:nth-child(11) {text-align: center}
table tr td:nth-child(12) {text-align: center}

.table-left th{background-color:RGB(0,0,0);color: white;}
.table-right th{background-color:RGB(0,0,0);color: white;}
</style>
</head>
<body>
<div>
<table border="0" cellspacing="0" cellpadding="0" class="table-left"><tbody></tbody></table>"""

table1 = df[['industry','name','Close','trend_mean','Close_200ma','trend_sd','rsi14','rsi_sd','pred_mean','performance','performance_sd','pred_winrate']]
table1 = table1.sort_values(['trend_mean'],ascending=False)
table1['Close'] = table1['Close'].apply \
                  (lambda x: int(x) if x>=100 else round(x,1) if x>8 else round(x,2) )
table1['trend_sd'] = table1['trend_sd'].apply(lambda x: round(x,1))
table1['rsi_sd'] = table1['rsi_sd'].apply(lambda x: round(x,1))
table1 = table1.head(int(len(table1)/2+1))
# table1['gap'] = -df['trend_mean'] + 100*df['Close_200ma']
# table1['gap'] = table1['gap'].apply(lambda x: str(round(x,1))+'%')
table1['rsi14'] = table1['rsi14'].apply(lambda x: int(x))
table1['trend_mean'] = table1['trend_mean'].apply(lambda x: str(round(x,2))+'%')
table1['Close_200ma'] = table1['Close_200ma'].apply(lambda x: str(round(100*x,1))+'%')
table1['pred_mean']=table1['pred_mean'].astype(int)
table1['performance'] = table1['performance'].astype(str).apply(lambda x: x+'%')
# table1['pred_winrate']=table1['pred_winrate'].astype(int)
# table1['performance']=table1['performance'].astype(str).apply(lambda x: x+'')

header = ['Industry','Ticker','Price','5yr Trend','Current Trend','Trend STD','RSI20','RSI STD','3-month Predict','3-month Actual','Actual STD','3-month +ve %']
header_string = '<tr> '
for i in header:
    header_string = header_string + '<th> ' + i + ' </th> '
header_string=header_string+' </tr>'

row10 = table1.iloc[:,-1].median()
# TR
all_row_string = ''
for j in range(len(table1)):
    row = table1.iloc[j,:].values     
    row_string = '<tr>'
    k=0
    for i in row:
        if k in [0,1,2,3]:
            if row[1] in ['hangseng','sp500']:
                row_string+='<td  style="background-color:#526FFF"> ' + str(i) + ' </td> '
            elif row[1] in watch_list:
                row_string+='<td  style="background-color:#FFEFD5"> ' + str(i) + ' </td> '
            else:
                row_string+='<td> ' + str(i) + ' </td> '
        elif k in [4,5]:
            if row[5]<0:color_gradient = (243-abs(row[5])*100,243,243-abs(row[5])*100)
            else: color_gradient = (243,243-abs(row[5])*100,243-abs(row[5])*100)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '
        elif k in [6,7]:
            if row[7]<0:color_gradient = (243-abs(row[7])*100,243,243-abs(row[7])*100)
            else: color_gradient = (243,243-abs(row[7])*100,243-abs(row[7])*100)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '
        elif k in [8]:
            color_gradient = (243,243,243)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i)+'%' + ' </td> '
        elif k in [11]:
            if row[11]>0:color_gradient = (243-(abs(row[11])-.50)*55/10,243,\
                                           243-(abs(row[11])-.50)*55/10)
            else: color_gradient = (243,243-abs((row[11]-.50))*55/10,243-abs((row[11]-.50))*55/10)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '
        elif k in [9,10]:
            if row[10]<0:color_gradient = (243-abs(row[10])*100,243,243-abs(row[10])*100)
            else: color_gradient = (243,243-abs(row[10])*100,243-abs(row[10])*100)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '
        else: row_string+='<td> '+str(i)+' </td> '
        k+=1
    row_string += '</tr>'
    all_row_string+=row_string

html += """\
    <div><p style="font-size:21px"><br>
       Stocks Watchlist</p></div>
       <div>
<table border="0" cellspacing="0" cellpadding="0" class="table-left"><tbody>"""

html += header_string
html += all_row_string

html += '</tbody></table>'

# 4th Table
table1 = df[['industry','name','Close','trend_mean','Close_200ma','trend_sd','rsi14','rsi_sd','pred_mean','performance','performance_sd','pred_winrate']]
table1 = table1.sort_values(['trend_mean'],ascending=True)
table1 = table1.head(int(len(table1)/2))
table1['Close'] = table1['Close'].apply(lambda x: int(x) if x>=100 else round(x,1) if x>8 else round(x,2))
table1['trend_sd'] = table1['trend_sd'].apply(lambda x: round(x,1))
table1['rsi_sd'] = table1['rsi_sd'].apply(lambda x: round(x,1))
table1['rsi14'] = table1['rsi14'].apply(lambda x: int(x))
table1['trend_mean'] = table1['trend_mean'].apply(lambda x: str(round(x,2))+'%')
table1['Close_200ma'] = table1['Close_200ma'].apply(lambda x: str(round(100*x,1))+'%')
table1['pred_mean']=table1['pred_mean'].astype(int)
table1['performance'] = table1['performance'].astype(str).apply(lambda x: x+'%')
# table1['pred_winrate']=table1['pred_winrate'].astype(int)
# table1['pred_std']=table1['pred_std'].astype(int)

# TH
header = ['Industry','Ticker','Price','5yr Trend','Current Trend','Trend STD','RSI20','RSI STD','3-month Predict','3-month Actual','Actual STD','3-month +ve %']
header_string = '<tr> '
for i in header:
    header_string = header_string + '<th> ' + i + ' </th> '
header_string=header_string+' </tr>'


# TR
all_row_string = ''
for j in range(len(table1)):
    row = table1.iloc[j,:].values     
    row_string = '<tr>'
    k=0
    for i in row:
        if k in [0,1,2,3]:
            if row[1] in ['hangseng','sp500']:
                row_string+='<td  style="background-color:#526FFF"> ' + str(i) + ' </td> '
            elif row[1] in watch_list:
                row_string+='<td  style="background-color:#FFEFD5"> ' + str(i) + ' </td> '
            else:
                row_string+='<td> ' + str(i) + ' </td> '
        elif k in [4,5]:
            if row[5]<0:color_gradient = (243-abs(row[5])*100,243,243-abs(row[5])*100)
            else: color_gradient = (243,243-abs(row[5])*100,243-abs(row[5])*100)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '
        elif k in [6,7]:
            if row[7]<0:color_gradient = (243-abs(row[7])*100,243,243-abs(row[7])*100)
            else: color_gradient = (243,243-abs(row[7])*100,243-abs(row[7])*100)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '
        elif k in [8]:
            color_gradient = (243,243,243)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i)+'%' + ' </td> ' 
        elif k in [11]:
            if row[11]>0:color_gradient = (243-(abs(row[11])-0.50)*55/10,243,\
                                           243-(abs(row[11])-0.50)*55/10)
            else: color_gradient = (243,243-abs((row[11]-.50))*55/10,243-abs((row[11])-.50)*55/10)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '

        elif k in [9,10]:
            if row[10]<0:color_gradient = (243-abs(row[10])*100,243,243-abs(row[10])*100)
            else: color_gradient = (243,243-abs(row[10])*100,243-abs(row[10])*100)
            str_color_gradient = 'RGB'+str(color_gradient)
            row_string+='<td style="background-color:'+str_color_gradient+'"> ' + str(i) + ' </td> '

        k+=1
    row_string += '</tr>'
    all_row_string+=row_string

html += '<table border="0" cellspacing="0" cellpadding="0" class="table-right"><tbody>'
html += header_string
html += all_row_string
html += '</tbody>'
html += """</table></div></body></html>"""

# 11 - insert charts into the email body
body = 'Overall Analysis'
sender_email = "bryanpython123@gmail.com"

message = MIMEMultipart()
message["Subject"] = body
message["From"] = sender_email
message["To"] = sender_email

part2 = MIMEText(html, "html")
message.attach(part2)

os.chdir(chart_input_dir)

for chart in charts:
    img_data = open(chart, 'rb').read()
    image = MIMEImage(img_data, name=os.path.basename(chart))
    image.add_header('Dashboard', '<{}>'.format(chart))
    message.attach(image)

# 11 - send out the email

s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.ehlo()
s.login("bryanpython123@gmail.com", '1q2w#E$R')
s.sendmail(sender_email,'ichbinbryan@gmail.com', message.as_string())
# s.sendmail(sender_email,'zpteh717@yahoo.com', message.as_string())
s.quit()
