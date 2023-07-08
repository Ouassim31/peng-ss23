# -*- coding: utf-8 -*-

import os
import flask
import requests
from cryptography.fernet import Fernet
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
from datetime import datetime, timedelta
from fit_data_agg import SelectAggregationType
import json

from component import getUserinfos
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read',
          'https://www.googleapis.com/auth/fitness.body.read',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid',
          'https://www.googleapis.com/auth/userinfo.profile',
          
          'https://www.googleapis.com/auth/user.gender.read',
          'https://www.googleapis.com/auth/user.birthday.read',
          'https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'FKSRstfF1-k1bUwi5MW1S-wVdLlbP4W0GNnkmmKkPek='


@app.route('/')
def index():
    return print_index_table()


@app.route('/test')
def getMirorToken():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

   
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    
    cipher_suite = Fernet(app.secret_key)
    token = cipher_suite.encrypt(json.dumps(credentials_to_dict(credentials)).encode())
    response = requests.post("http://localhost:3000/callback",json=({'token': token.decode()}))
    return flask.redirect(response.json()['redirect_link'])
@app.route('/my/pdata')

def getpdata():
    #fetch header
    token = flask.request.headers.get('Authorization')
    #decrypt mirror token
    cipher_suite = Fernet(app.secret_key)
    #fetch and trasform personal data
    credentials_json = cipher_suite.decrypt(token.encode()).decode().replace('\'',"\"")
    credentials = google.oauth2.credentials.Credentials(
        **json.loads(credentials_json)
    )
    
    return flask.jsonify(getUserinfos(credentials))
@app.route('/my/fitdata')
def getfitdata():
    
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
        "startTimeMillis": int((datetime.now() - timedelta(weeks=2)).timestamp()*1000),
        "endTimeMillis": int(datetime.now().timestamp()*1000)
    }
    #fetch  mirror token
    token = flask.request.headers.get('Authorization')
    #decrypt mirror token
    cipher_suite = Fernet(app.secret_key)
     # Assuming the encrypted data is passed in the request body as JSON
    credentials_json = cipher_suite.decrypt(token.encode()).decode().replace('\'',"\"")
    #fetch and aggregate fit data
    credentials = google.oauth2.credentials.Credentials(
        **json.loads(credentials_json)
    )
    fitness = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    fitdata = fitness.users().dataset().aggregate(
        userId="me", body=request_body).execute()
    #return flask.jsonify(**fitdata)
    
    type_select = SelectAggregationType(int(flask.request.args['aggtype']), fitdata)
    
    return flask.jsonify(type_select.aggregation_type())
@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    
    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state
   
    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    print(authorization_response)
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('getMirorToken'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return ('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
