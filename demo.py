import os
import json
import requests
#import jwt
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Define the scopes for accessing user data
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 
          'openid',
          'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/user.gender.read',
          'https://www.googleapis.com/auth/user.birthday.read',
          'https://www.googleapis.com/auth/user.addresses.read',
          'https://www.googleapis.com/auth/user.organization.read',
          

           ]

# Load the client secret file
client_secret_file = 'client_file.json'
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Build the API client
service = build('oauth2', 'v2', credentials=creds)
cal_service = build('calendar', 'v3', credentials=creds)
p_service = build('people', 'v1', credentials=creds)

# fitness_service = build('fitness', 'v1', credentials=creds)

# Fetch user data
user_info = service.userinfo().get().execute()
# data_sources = fitness_service.users().dataSources().list(userId='me').execute()
# Retrieve the list of calendars
calendar_list = cal_service.calendarList().list().execute()
profile = p_service.people().get(resourceName='people/me', personFields='birthdays,genders,names,organizations,addresses').execute()
# Print the calendar titles
for calendar in calendar_list['items']:
    print('Calendar:', calendar['summary'])
# Print the user's personal data
birthdays = profile.get('birthdays', [])
genders = profile.get('genders', [])
names = profile.get('names',[])
date_of_birth = birthdays[0]['date'] if birthdays else None
gender = genders[0]['value'] if genders else None
print('Date of Birth:', date_of_birth)
print('Gender:', gender)
print('Names:', names)
print(profile.get('addresses'))






