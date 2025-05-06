import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Specify the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    creds = None
    creds_file = 'D:\\Documents\\Vue-Django-Website\\storefront\\credentials.json'
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print("Authorization successful! Token saved as 'token.json'.")

if __name__ == '__main__':
    main()
