import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import sys
import pandas as pd



body = 'my_stocks'
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


img_data = open('my_stocks.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('my_stocks.png'))
image.add_header('Dashboard', '<{}>'.format('my_stocks.png'))
message.attach(image)
    
s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.ehlo()
s.login("bryanpython123@gmail.com", '1q2w#E$R')
s.sendmail(sender_email,'ichbinbryan@gmail.com', message.as_string())
s.sendmail(sender_email,'zpteh717@yahoo.com', message.as_string())
s.quit()
