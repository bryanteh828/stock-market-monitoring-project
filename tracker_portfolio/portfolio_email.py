import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import sys
import pandas as pd

input_dir = r'/Users/tehyuqi/Dropbox'

body = 'my_stocks'
sender_email = "bryanpython123@gmail.com"

message = MIMEMultipart()
message["Subject"] = body
message["From"] = sender_email
message["To"] = sender_email

os.chdir(input_dir)
print('using macbook...')

img_data = open('portfolio.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('portfolio.png'))
image.add_header('Dashboard', '<{}>'.format('portfolio.png'))
message.attach(image)

s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.ehlo()
s.login("bryanpython123@gmail.com", '1q2w#E$R')
s.sendmail(sender_email,'ichbinbryan@gmail.com', message.as_string())
s.quit()
