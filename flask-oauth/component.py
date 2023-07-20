import os
import pycountry_convert as pcc
from datetime import date
import json
import hashlib
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from time import time
from datetime import datetime, timedelta
from fit_data_agg import AverageFitData,SelectAggregationType

# Define the scopes for accessing user data
def auth():
    SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 
            'openid',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/user.gender.read',
            'https://www.googleapis.com/auth/user.birthday.read',
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
            user_input = ''
            while user_input.lower() != 'yes' and user_input.lower() != 'no':
                user_input = input("do you want to save the encripted credential as .json file for the next run ? (yes/no)")
                if (user_input.lower() == 'yes'):
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
    return creds

def hash_email(email):
    hasher = hashlib.sha256()
    hash_bytes = email.encode('utf-8')
    hasher.update(hash_bytes)
    return hasher.hexdigest()
def categorize_locale(language_tag):
    try:    
        country = pcc.country_alpha2_to_continent_code(language_tag.split('-')[-1].upper())
        return country
    except:
        return None

    
def mask_string(n,input):
  return  input[:n] + '*' * (len(input) - n)

def mask_email(email):
    parts = email.split('@')
    username = parts[0]
    domain = parts[1]
    masked_username = mask_string(2,username)
    masked_email = masked_username + '@' + domain
    
    return masked_email
def fetch_fit_data(creds,weeks):
    
    request_body = {
        "aggregateBy": [{
            #
            "dataTypeName": "com.google.calories.expended",
            # "dataSourceId": "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
        },
            {
            "dataTypeName": "com.google.heart_minutes",
            # "dataSourceId": "derived:com.google.heart_minutes:com.google.android.gms:merge_heart_minutes"
        },
            {
            "dataTypeName": "com.google.active_minutes",
            # "dataSourceId": "derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes"
        },
            {
            "dataTypeName": "com.google.activity.segment",
            # "dataSourceId": "derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments"
        }
        ],
        "bucketByTime": {"durationMillis": 3600000},
        "startTimeMillis": int(((datetime.now() - timedelta(weeks=int(weeks)))).timestamp()*1000),
        "endTimeMillis": int(datetime.now().timestamp()*1000)
    }
    
    #fetch and aggregate fit data
    fitness = build(
        'fitness', 'v1', credentials=creds)
    fitdata = fitness.users().dataset().aggregate(
        userId="me", body=request_body).execute()
    return fitdata    
def getUserfitdata(creds,weeks,aggtype):
    
    request_body = {
        "aggregateBy": [{
            #
            "dataTypeName": "com.google.calories.expended",
            # "dataSourceId": "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
        },
            {
            "dataTypeName": "com.google.heart_minutes",
            # "dataSourceId": "derived:com.google.heart_minutes:com.google.android.gms:merge_heart_minutes"
        },
            {
            "dataTypeName": "com.google.active_minutes",
            # "dataSourceId": "derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes"
        },
            {
            "dataTypeName": "com.google.activity.segment",
            # "dataSourceId": "derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments"
        }
        ],
        "bucketByTime": {"durationMillis": 3600000},
        "startTimeMillis": int(((datetime.now() - timedelta(weeks=int(weeks)))).timestamp()*1000),
        "endTimeMillis": int(datetime.now().timestamp()*1000)
    }
    
    #fetch and aggregate fit data
    fitness = build(
        'fitness', 'v1', credentials=creds)
    fitdata = fitness.users().dataset().aggregate(
        userId="me", body=request_body).execute()
    
    type_select = SelectAggregationType(aggtype, fitdata)
    
    return type_select.aggregation_type()
def fetchUserinfo(creds):
    

     # Build the API client
    service = build('oauth2', 'v2', credentials=creds)
    p_service = build('people', 'v1', credentials=creds)
    # Fetch user data
    user_info = service.userinfo().get().execute()
    profile = p_service.people().get(resourceName='people/me', personFields='birthdays,genders,names,locales').execute()
    birthdays = profile.get('birthdays', [])
    genders = profile.get('genders', [])
    names = profile.get('names',[])
    locales = profile.get('locales',[])
    date_of_birth = birthdays[0]['date'] if birthdays else None
    
    return {
        'id': user_info['email'] if user_info else None,
        'firstname':names[0]['givenName'] if names else None,
        #'lastname': mask_string(0,names[0]['familyname']) if names else None,
        'gender': genders[0]['value'] if genders else None,
        'isAdult': date_of_birth['year'] if date_of_birth['year'] else None,
        'email': user_info['email'] if user_info else None,
        'region': locales[0]['value'] if locales else None,
    }


def getUserinfos(creds):
     # Build the API client
    service = build('oauth2', 'v2', credentials=creds)
    p_service = build('people', 'v1', credentials=creds)
    # Fetch user data
    user_info = service.userinfo().get().execute()
    profile = p_service.people().get(resourceName='people/me', personFields='birthdays,genders,names,locales').execute()
    birthdays = profile.get('birthdays', [])
    genders = profile.get('genders', [])
    names = profile.get('names',[])
    locales = profile.get('locales',[])

    date_of_birth = birthdays[0]['date'] if birthdays else None
    return {
        'id': hash_email(user_info['email']) if user_info else None,
        'firstname':names[0]['givenName'] if names else None,
        'gender': genders[0]['value'] if genders else None,
        'isAdult': (date.today().year - date_of_birth['year']) > 17 if date_of_birth['year'] else None,
        'email': mask_email(user_info['email']) if user_info else None,
        'region': categorize_locale(locales[0]['value']) if locales else None,
    }








