import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from datetime import datetime
import pandas as pd

# 1 - set directory

try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')

# 2 - read datatable

df = pd.read_csv('records_2.csv')
transactions = pd.read_csv('transactions.csv')
purchased_tickers = list(transactions['name'].unique())

# 3 - process, transform datatable
table1 = df[['industry','name','Close','trend_mean','Close_200ma','rsi14','trend_sd','rsi_sd']]
table1['Close'] = table1['Close'].apply(lambda x: str(int(x)) if x >= 100 else str(round(x,1)) if x > 8 else str(round(x,2)))
table1['trend_sd'] = table1['trend_sd'].apply(lambda x: round(x,1))
table1['rsi_sd'] = table1['rsi_sd'].apply(lambda x: round(x,1))
# table1['gap'] = - df['trend_mean'] + 100*df['Close_200ma']
# table1['gap'] = table1['gap'].apply(lambda x: str(round(x,1))+'%')
table1['rsi14'] = table1['rsi14'].apply(lambda x: int(x))
table1['trend_mean'] = table1['trend_mean'].apply(lambda x: str(round(x,2))+'%')
table1['Close_200ma'] = table1['Close_200ma'].apply(lambda x: str(round(100*x,1))+'%')
table1 = table1.sort_values(['rsi14'],ascending=True)
table1 = table1.head(int(len(table1)/2+1))

# 4 - filter datatable and convert to html datatable format

header = ['Industry','Ticker','Price','5yr Trend','Current Trend','RSI20','Trend STD','RSI STD']
header_string = '<tr> '
for i in header:
    header_string = header_string + '<th style="background-color: #4CAF50;color: white;"> ' + i + ' </th> '
header_string=header_string+' </tr>'

all_row_string = ''
for j in range(len(table1)):
    row = table1.iloc[j,:].values
    if row[1] in ['hangseng','sp500']:
        row_string = '<tr style="background-color:#D1D0CE"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string 
    elif (row[5]<45 and row[4][0] !='-'):
        row_string = '<tr style="background-color:#EBF4FA"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string
    else:
        row_string = '<tr> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string  

# 5 - build the html starting parts and html datatable

html = """\
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
    padding: 3px;
    border-collapse: collapse;
    border-bottom: 1px solid #ddd
    text-align: center;
}

table { table-layout: fixed; }
td { width: 25%; }
</style>
</head>
  <body>
    <p style="font-size:20px"><br>
       1 - Short Term Momentum Buyers and Sellers: </p>
       <table border="0" cellspacing="0" cellpadding="0">
<table border="0" cellspacing="0" cellpadding="0" style="width:50%;float:left"><tbody>"""
html += header_string
html += all_row_string
html += '</tbody></table>'

# 6 - filter datatable into a 2nd time as a 2nd html datatable

table1 = df[['industry','name','Close','trend_mean','Close_200ma','rsi14','trend_sd','rsi_sd']]
table1['Close'] = table1['Close'].apply(lambda x: str(int(x)) if x >= 100 else str(round(x,1)) if x > 8 else str(round(x,2)))
table1['trend_sd'] = table1['trend_sd'].apply(lambda x: round(x,1))
table1['rsi_sd'] = table1['rsi_sd'].apply(lambda x: round(x,1))
# table1['gap'] = -df['trend_mean'] + 100*df['Close_200ma']
# table1['gap'] = table1['gap'].apply(lambda x: str(round(x,1))+'%')
table1['rsi14'] = table1['rsi14'].apply(lambda x: int(x))
table1['trend_mean'] = table1['trend_mean'].apply(lambda x: str(round(x,2))+'%')
table1['Close_200ma'] = table1['Close_200ma'].apply(lambda x: str(round(100*x,1))+'%')
table1 = table1.sort_values(['rsi14'],ascending=False)
table1 = table1.head(int(len(table1)/2+1))

header = ['Industry','Ticker','Price','5yr Trend','Current Trend','RSI20','Trend STD','RSI STD']
header_string = '<tr> '
for i in header:
    header_string = header_string + '<th style="background-color: #7f3123;color: white;"> ' + i + ' </th> '
header_string+=' </tr>'

all_row_string = ''
for j in range(len(table1)):
    row = table1.iloc[j,:].values
    if row[1] in ['hangseng','sp500']:
        row_string = '<tr style="background-color:#D1D0CE"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string 
    elif row[5]>60 and row[4][0]=='-':
        row_string = '<tr style="background-color:#EBF4FA"> '
        for i in row: row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string
    else:
        row_string = '<tr> '
        for i in row: row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string  

html += '<table border="0" cellspacing="0" cellpadding="0" style="width:50%;float:left"><tbody>'
html += header_string
html += all_row_string
html += '</tbody>'
html += """</table> </table> </body> </html>"""

# 7 - create email class and insert html into the email class

body = 'Overall Analysis'
sender_email = "bryanpython123@gmail.com"

message = MIMEMultipart()
message["Subject"] = body
message["From"] = sender_email
message["To"] = sender_email

part2 = MIMEText(html, "html")
message.attach(part2)

# 8 - filter datatable into a 3rd time as a 3rd html datatable

table1 = df[['industry','name','Close','trend_mean','Close_200ma','rsi14','trend_sd','rsi_sd']]
table1 = table1.sort_values(['trend_mean'],ascending=False)
table1['Close'] = table1['Close'].apply(lambda x: str(int(x)) if x >= 100 else str(round(x,1)) if x > 8 else str(round(x,2)))
table1['trend_sd'] = table1['trend_sd'].apply(lambda x: round(x,1))
table1['rsi_sd'] = table1['rsi_sd'].apply(lambda x: round(x,1))
table1 = table1.head(int(len(table1)/2+1))
# table1['gap'] = -df['trend_mean'] + 100*df['Close_200ma']
# table1['gap'] = table1['gap'].apply(lambda x: str(round(x,1))+'%')
table1['rsi14'] = table1['rsi14'].apply(lambda x: int(x))
table1['trend_mean'] = table1['trend_mean'].apply(lambda x: str(round(x,2))+'%')
table1['Close_200ma'] = table1['Close_200ma'].apply(lambda x: str(round(100*x,1))+'%')


header = ['Industry','Ticker','Price','5yr Trend','Current Trend','RSI20','Trend STD','RSI STD']
header_string = '<tr> '
for i in header:
    header_string = header_string + '<th style="background-color: #4CAF50;color: white;"> ' + i + ' </th> '
header_string=header_string+' </tr>'

all_row_string = ''
for j in range(len(table1)):
    row = table1.iloc[j,:].values
    if row[1] in ['hangseng','sp500']:
        row_string = '<tr style="background-color:#D1D0CE"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string       
    elif row[1] in purchased_tickers:
        row_string = '<tr style="background-color:#fffec9"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string
    elif row[6]<=-1 and row[1] not in purchased_tickers: 
        row_string = '<tr style="background-color:#EBF4FA"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string
    else:
        row_string = '<tr> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string  

html = """\
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
    padding: 3px;
    border-collapse: collapse;
    border-bottom: 1px solid #ddd
    text-align: center;
}

table { table-layout: fixed; }
td { width: 25%; }
</style>
</head>
  <body>
    <p style="font-size:20px"><br>
       2 - Historically Strong/Weak Companies: </p>
       <table border="0" cellspacing="0" cellpadding="0">
<table border="0" cellspacing="0" cellpadding="0" style="width:50%;float:left"><tbody>"""

html += header_string
html += all_row_string

html += '</tbody></table>'

# 9 - filter datatable into a 4th time as a 4th html datatable

table1 = df[['industry','name','Close','trend_mean','Close_200ma','rsi14','trend_sd','rsi_sd']]
table1 = table1.sort_values(['trend_mean'],ascending=True)
table1 = table1.head(int(len(table1)/2))
table1['Close'] = table1['Close'].apply(lambda x: str(int(x)) if x >= 100 else str(round(x,1)) if x > 8 else str(round(x,2)))
table1['trend_sd'] = table1['trend_sd'].apply(lambda x: round(x,1))
table1['rsi_sd'] = table1['rsi_sd'].apply(lambda x: round(x,1))
# table1['gap'] = -df['trend_mean'] + 100*df['Close_200ma']
# table1['gap'] = table1['gap'].apply(lambda x: str(round(x,1))+'%')
table1['rsi14'] = table1['rsi14'].apply(lambda x: int(x))
table1['trend_mean'] = table1['trend_mean'].apply(lambda x: str(round(x,2))+'%')
table1['Close_200ma'] = table1['Close_200ma'].apply(lambda x: str(round(100*x,1))+'%')


header = ['Industry','Ticker','Price','5yr Trend','Current Trend','RSI20','Trend STD','RSI STD']
header_string = '<tr> '
for i in header:
    header_string = header_string + '<th style="background-color: #7f3123;color: white;"> ' + i + ' </th> '
header_string=header_string+' </tr>'
print(header_string)

all_row_string = ''
for j in range(len(table1)):
    row = table1.iloc[j,:].values
    if row[1] in ['hangseng','sp500']:
        row_string = '<tr style="background-color:#D1D0CE"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string 
    elif row[6]<=-1 and row[1] not in purchased_tickers:
        row_string = '<tr style="background-color:#EBF4FA"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string        
    elif row[1] in purchased_tickers: #Do - bold the text if > 60 (strong buy)
        row_string = '<tr style="background-color:#fffec9"> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string
    else:
        row_string = '<tr> '
        for i in row:
            row_string = row_string + '<td> ' + str(i) + ' </td> '
        row_string = row_string+' </tr>'
        all_row_string = all_row_string + row_string  

html += '<table border="0" cellspacing="0" cellpadding="0" style="width:50%;float:left"><tbody>'
html += header_string
html += all_row_string
html += '</tbody>'
html += """</table></table></body></html>"""

# 10 - furnish the text/html of email

length = int(len(table1)/2+1)
for i in range(int(1.9*(length))):
    text = MIMEText('\n')
    message.attach(text)

part2 = MIMEText(html, "html")
message.attach(part2)

text = MIMEText('\n')
message.attach(text)

# 11 - insert charts into the email body

try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')

img_data = open('overall_4.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('overall_4.png'))
image.add_header('Dashboard', '<{}>'.format('overall_4.png'))
message.attach(image)

img_data = open('overall_2.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('overall_2.png'))
image.add_header('Dashboard', '<{}>'.format('overall_2.png'))
message.attach(image)

img_data = open('overall_volatility.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('overall_volatility.png'))
image.add_header('Dashboard', '<{}>'.format('overall_volatility.png'))
message.attach(image)

img_data = open('overall_5.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('overall_5.png'))
image.add_header('Dashboard', '<{}>'.format('overall_5.png'))
message.attach(image)

# 11 - send out the email

s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.ehlo()
s.login("bryanpython123@gmail.com", '1q2w#E$R')
s.sendmail(sender_email,'ichbinbryan@gmail.com', message.as_string())
s.sendmail(sender_email,'zpteh717@yahoo.com', message.as_string())
s.quit()