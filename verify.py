import random
import smtplib
from email.message import EmailMessage

#Generates 4 digit code for verification
def generate_code():
    code = random.randint(1000,9999)
    return code

#Multi-factor authentication
#Sends an email with random 4 digit number when the user tries to login
#Email is sent to the address that the user has signed up with 
#and of which the user has also verified at the time of registration
def verify_login(receiver):
    code = generate_code()

    content = EmailMessage()
    content['Subject'] = 'Are you trying to login?'
    content['From'] = 'info2222re06@gmail.com'
    content['To'] = receiver
    content.set_content("""
    Hi
    
    Please help us confirm that it's you trying to log in. 
    Simply enter the following code.
    
    Verification Code: {}
    
    The code will expire in 10 minutes.
    
    Best,
    Admin team""".format(code))
    #SSL connection enabled
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('info2222re06@gmail.com', 're06team2admin')
        smtp.send_message(content)

    return str(code)

def verify_email(receiver):
    code = generate_code()

    content = EmailMessage()
    content['Subject'] = 'Please verify your email address'
    content['From'] = 'info2222re06@gmail.com'
    content['To'] = receiver
    content.set_content("""
    Hi

    Thanks for signing up!
    Now, we just need you to verify your email address 
    to complete setting up your account.
    Simply enter the code below!
    
    Verification Code: {}
    
    The code will expire in 10 minutes.
    
    Best,
    Admin team""".format(code))
    #SSL connection enabled
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('info2222re06@gmail.com', 're06team2admin')
        smtp.send_message(content)

    return str(code)
