# -*- coding: utf-8 -*-

import os
import flask
import requests
from cryptography.fernet import Fernet
import google.oauth2.credentials
import google_auth_oauthlib.flow
import os
import json
from component import getUserinfos,getUserfitdata



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
          'https://www.googleapis.com/auth/user.birthday.read'
          ]
API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'FKSRstfF1-k1bUwi5MW1S-wVdLlbP4W0GNnkmmKkPek='


@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.render_template('component/login.html')
    creds = flask.session['credentials']
    return flask.render_template('component/home.html',creds=creds)


@app.route('/send')
def getMirorToken():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    # Encrypt credentials into mirror token
    cipher_suite = Fernet(app.secret_key)
    token = cipher_suite.encrypt(json.dumps(credentials_to_dict(credentials)).encode())
    response = requests.post(flask.request.args['callback_url'],json=({'token': token.decode()}))

    return flask.redirect(response.json()['redirect_link'])

@app.route('/my')
def getprofile():
    #fetch header
    token = flask.request.headers.get('Authorization')
    #decrypt mirror token
    cipher_suite = Fernet(app.secret_key)
    #fetch and trasform personal data
    credentials_json = cipher_suite.decrypt(token.encode()).decode().replace('\'',"\"")
    credentials = google.oauth2.credentials.Credentials(
        **json.loads(credentials_json)
    )
    fitdata = getUserfitdata(credentials,int(flask.request.args['weeks']),int(flask.request.args['aggtype']))
    userdata = getUserinfos(credentials)
    return flask.jsonify({
        **userdata,
        **fitdata
    })
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
    fitdata = getUserfitdata(credentials,int(flask.request.args['weeks']),int(flask.request.args['aggtype']))
    
    return flask.jsonify(fitdata)
@app.route('/authorize',methods=['POST'])
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=flask.request.get_json()['scopes'])

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
   
    return flask.jsonify({'redirect_url' : authorization_url})


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
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('index'))


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
    return flask.redirect(flask.url_for('index'))


@app.route('/clear')
def clear_credentials():
    
    if 'credentials' in flask.session:
        credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

        revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

        status_code = getattr(revoke, 'status_code')
        del flask.session['credentials']
    
        
        
    
    return flask.redirect(flask.url_for('index'))
        


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}



if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
