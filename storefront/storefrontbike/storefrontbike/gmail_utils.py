import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_gmail_email(to_email, subject, message_text,  html_content=None, pdf_content=None, pdf_filename=None):
    creds = Credentials.from_authorized_user_file('storefrontbike/token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = subject

    msg = MIMEText(message_text, 'plain')
    message.attach(msg)

    if html_content:
        html_msg = MIMEText(html_content, 'html')
        message.attach(html_msg)

    if pdf_content and pdf_filename:
        pdf = MIMEApplication(pdf_content, 'pdf')
        pdf.add_header('Content-Disposition', f'attachment; filename="{pdf_filename}"')
        message.attach(pdf)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    send_message = {'raw': raw_message}

    try:
        sent_message = service.users().messages().send(userId="me", body=send_message).execute()
        print(f"Message sent successfully. Message ID: {sent_message['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")