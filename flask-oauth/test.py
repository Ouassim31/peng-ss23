from datetime import date
from time import time
import json
from cryptography.fernet import Fernet
import requests
import  random
import fit_data_agg
import google.oauth2.credentials
from component import categorize_locale, fetchUserinfo,fetch_fit_data,hash_email,mask_email,mask_string
import pandas as pd
from pycanon import anonymity, report
import sys
secret_key = 'FKSRstfF1-k1bUwi5MW1S-wVdLlbP4W0GNnkmmKkPek='
USER_FILE = "test_results/test_user.csv"

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return average
def get_static(numbers):
    return {
    'avg' : round(calculate_average(numbers),5),
    'max' : round(max(numbers),5),
    'min' : round(min(numbers),5),
    'count': len(numbers)
}
import pandas as pd

def calculate_k_anonymity(dataset, sensitive_attributes, quasi_identifiers,k):
    """
    Calculate k-anonymity and generate an anonymity report.

    Args:
        dataset (pd.DataFrame): The user dataset as a Pandas DataFrame.
        sensitive_attributes (list): List of sensitive attribute column names.
        quasi_identifiers (list): List of quasi-identifier column names.

    Returns:
        dict: Anonymity report with k-anonymity information.
    """
    anonymity_report = {}

    # Calculate the count of unique combinations of quasi-identifiers
    unique_combinations = dataset.groupby(quasi_identifiers).size().reset_index(name='count')

    # Calculate the minimum group size for k-anonymity
    min_group_size = unique_combinations['count'].min()

    # Calculate the k-anonymity level
    k_anonymity = (min_group_size >= k)

    anonymity_report['k_anonymity'] = k_anonymity
    anonymity_report['min_group_size'] = min_group_size

    # Calculate the count of unique combinations of sensitive attributes
    unique_sensitive_combinations = dataset.groupby(sensitive_attributes).size().reset_index(name='count')

    # Calculate the risk of re-identification
    risk_of_reidentification = unique_sensitive_combinations['count'].max()

    anonymity_report['risk_of_reidentification'] = risk_of_reidentification

    return anonymity_report

def test_encrypt(token):
    start_time = time()
    cipher_suite = Fernet(secret_key)
    mirror_token = cipher_suite.encrypt(json.dumps(token).encode())
    execution_time = time()-start_time
    return {'execution_time' : execution_time*1000,
            'mirror_token' : mirror_token,
            'size' : sys.getsizeof(json.dumps(token))/1024}

def test_decrypt(token):
    start_time = time()
    cipher_suite = Fernet(secret_key)
    credentials_json = cipher_suite.decrypt(token).decode().replace('\'',"\"")
    execution_time = time()-start_time
    return {'execution_time' : execution_time*1000,
            }
def test_pdata_agg(data):
    start_time = time()
    birthdays = data.get('birthdays', [])
    genders = data.get('genders', [])
    names = data.get('names',[])
    locales = data.get('locales',[])
    date_of_birth = birthdays[0]['date'] if birthdays else None
    test = {
        'id': hash_email(data['email']) if data else None,
        'firstname':names[0]['givenName'] if names else None,
        #'lastname': mask_string(0,names[0]['familyname']) if names else None,
        'gender': genders[0]['value'] if genders else None,
        'isAdult': (date.today().year - date_of_birth['year']) > 17 if date_of_birth['year'] else None,
        'email': mask_email(data['email']) if data else None,
        'region': categorize_locale(locales[0]['value']) if locales else None,
    }
    return {'execution_time' : time()-start_time, 'size' : sys.getsizeof(json.dumps(data))/1024}
def test_data_agg(aggtype,data):
    start_time = time()
    type_select = fit_data_agg.SelectAggregationType(aggtype, data)
    type_select.aggregation_type()
    json_string = json.dumps(data)
    return {'aggtype' : aggtype,'execution_time' : time()-start_time, 'size' : sys.getsizeof(json_string)/1024}
def test_google_api(creds):
    start_time = time()
    credentials = google.oauth2.credentials.Credentials(
        **creds
    )
    
    data = fetchUserinfo(credentials)
    json_string = json.dumps(data)
    return {
        
        'execution_time' : time()-start_time,
        'size' : sys.getsizeof(json_string)/1024
    }
def test_googlefit_api(creds):
    start_time = time()
    credentials = google.oauth2.credentials.Credentials(
        **creds
    )
    
    data = fetch_fit_data(credentials,4)
    json_string = json.dumps(data)
    return {
        'execution_time' : time()-start_time,
        'size' : sys.getsizeof(json_string)/1024
    }
def test_endpoint(token,endpoint_url):
   start_time= time()
   response = requests.get(endpoint_url,headers={'Authorization':token})
   if (response.status_code != 200):
       return {'error' : response.status_code}
   execution_time = time() - start_time
   json_string = json.dumps(response.json())
   return {'endpoint_url': endpoint_url, 'execution_time' : execution_time,'size' : sys.getsizeof(json_string)/1024}

#TEST ENCRYPTION/DECRYPTION
with open('test_data/test_credential.json','r') as file:
   credentials =  json.loads(file.read())
encrypted_creds = [test_encrypt(token=cred) for cred in credentials]
test_decrypt_time = [test_decrypt(token['mirror_token'])['execution_time'] for token in encrypted_creds]
test_encrypt_time = [token['execution_time'] for token in encrypted_creds]
print('## ENCRYPTION/DECRYPTION TEST ##')
print(get_static(test_encrypt_time))
print('size of creds')
print(get_static([token['size'] for token in encrypted_creds]))
print(get_static(test_decrypt_time))

#TEST FIT AGG
with open('test_data/test_fit_data.json','r') as file:
   fitdata =  json.load(file)
fdata_agg_exec_time = [test_data_agg(random.randint(1, 4),fitdata) for i in range(1000)]
print('## FIT AGG TEST ##')
print ('time')
print(get_static([x['execution_time'] for x in fdata_agg_exec_time]))
print('size')
print(get_static([x['size'] for x in fdata_agg_exec_time]))
#TEST PDATA AGG
with open('test_data/test_raw_pdata.json','r') as file:
   pdata =  json.load(file)
   
pdata_agg_exec_time = [test_pdata_agg(pdata) for i in range(1000)]
print('## PDATA AGG TEST ##')
print ('time')
print(get_static([x['execution_time'] for x in pdata_agg_exec_time]))
print('size')
print(get_static([x['size'] for x in pdata_agg_exec_time]))


# Print the anonymity report:
QI = ['firstname','region','isAdult','gender']
SA = ['agg_active_minutes','agg_calories','agg_heart_minutes']
DATA = pd.read_csv(USER_FILE,).drop(columns=['id','email'])
print('## ANONYMITY REPORT ##')
print(calculate_k_anonymity(DATA.reset_index(drop=True),SA,QI,2))
#TEST ENDPOINTS
with open('test_data/test_real_credential.json','r') as file:
   credentials =  json.loads(file.read())
mirror_token = test_encrypt(credentials)

test_fit_time = [test_endpoint(mirror_token['mirror_token'],'http://localhost:8080/my/fitdata?aggtype=1&weeks=4') for i in range(20)]
print('##TEST FIT ENDPOINT##')
print(get_static([x['execution_time'] for x in test_fit_time]))


test_personal_time = [test_endpoint(mirror_token['mirror_token'],'http://localhost:8080/my/pdata') for x in range(20)]
print('##TEST PDATA ENDPOINT##')
print(get_static([x['execution_time'] for x in test_personal_time]))
#test google oauth flow exsecution time
print('## GOOGLE OATH FLOW - PDATA ##')
test_google_time = [test_google_api(credentials) for x in range(20)]
print(get_static([x['execution_time'] for x in test_google_time]))
print('## GOOGLE OATH FLOW - FITDATA ##')
test_googlefit_time = [test_googlefit_api(credentials) for x in range(20)]
print(get_static([x['execution_time'] for x in test_googlefit_time]))
print('## TEST Personal ENDPOINT - SIZE ##')
print(get_static([x['size'] for x in test_personal_time]))
print('## GOOGLE OATH FLOW - FITDATA - SIZE ##')
print(get_static([x['size'] for x in test_googlefit_time]))
print('## TEST FIT ENDPOINT - SIZE ##')
print(get_static([x['size'] for x in test_fit_time]))
print('## GOOGLE OATH FLOW - PDATA - SIZE ##')
print(get_static([x['size'] for x in test_google_time]))
#print(test_endpoint(mirror_token['mirror_token'],'http://localhost:8080/my/fitdata?aggtype=1&weeks=4'))
#print(test_endpoint(mirror_token['mirror_token'],'http://localhost:8080/my/pdata'))
#print(test_decrypt(encprypt_time['mirror_token']))
