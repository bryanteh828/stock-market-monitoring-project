import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import sys
import pandas as pd

try: 
    os.chdir(r'C:\\Users\\USER\\Dropbox\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/dropbox')
    print('using macbook...')

ticker_list = pd.read_csv('tickers.csv')

try:
    ticker = sys.argv[1]
    print('ticker is ' + ticker)
except:
    ticker = 'SP500'
    print('no ticker specified...analyzing sp500')

ticker_name = list(ticker_list[ticker_list['ticker']==ticker]['name'])[-1]

body = ticker_name.upper()
sender_email = "bryanpython123@gmail.com"

message = MIMEMultipart()
message["Subject"] = body
message["From"] = sender_email
message["To"] = sender_email

try: 
    os.chdir(r'C:\\Users\\USER\\Desktop\\stock_data\\')
    print('using windows...')
except: 
    os.chdir(r'/Users/tehyuqi/stockdata')
    print('using macbook...')

f=open("text.txt", "r")
contents =f.read()
text = MIMEText(contents)
message.attach(text)

img_data = open('plots.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('plots.png'))
image.add_header('Dashboard', '<{}>'.format('plots.png'))
message.attach(image)
    
s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.ehlo()
s.login("bryanpython123@gmail.com", '1q2w#E$R')
s.sendmail(sender_email,'ichbinbryan@gmail.com', message.as_string())
s.sendmail(sender_email,'zpteh717@yahoo.com', message.as_string())
s.quit()
