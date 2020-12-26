import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import pandas as pd

DASHBOARD_dir = r'/Users/tehyuqi/Dropbox'
PORTFOLIO_dir = r'/Users/tehyuqi/Dropbox/portfolio_stocks'

body = 'my_stocks'
sender_email = "bryanpython123@gmail.com"

message = MIMEMultipart()
message["Subject"] = body
message["From"] = sender_email
message["To"] = sender_email

os.chdir(DASHBOARD_dir)

img_data = open('portfolio.png', 'rb').read()
image = MIMEImage(img_data, name=os.path.basename('portfolio.png'))
image.add_header('Dashboard', '<{}>'.format('portfolio.png'))
message.attach(image)

os.chdir(PORTFOLIO_dir)
for file in os.listdir():
    if '.png' in file:
        img_data = open(file, 'rb').read()
        image = MIMEImage(img_data, name=os.path.basename(file))
        image.add_header('Dashboard', '<{}>'.format(file))
        message.attach(image)

s = smtplib.SMTP("smtp.gmail.com:587")
s.ehlo()
s.starttls()
s.ehlo()
s.login("bryanpython123@gmail.com", '1q2w#E$R')
s.sendmail(sender_email,'ichbinbryan@gmail.com', message.as_string())
s.quit()