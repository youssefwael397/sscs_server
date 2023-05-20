import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_violence_notification():
    mail_content = '''WARNING!
    There is a violence behaviour detected. 
    Take an action.
    '''
    #The mail addresses and password
    sender_address = 'youssefwael397@gmail.com'
    sender_pass = 'Y@n1022372000'
    receiver_address = 'youssefelharam123@gmail.com'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'WARNING!'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    with smtplib.SMTP('smtp.gmail.com', 587) as session:
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        print('Mail Sent')