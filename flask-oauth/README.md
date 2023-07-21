# PENG component

This is a Flask web application that integrates with Google Fit and Google People to fetch and transform user data. The application uses OAuth 2.0 for user authentication and authorization to access their fitness data and personal data. The user can log in, authorize the application to access their  data, and view the sent credentials on the home page.

## Prerequisites

Before running the application, make sure you have the following installed:

- Python (version 3.x)
- Flask (`pip install flask`)
- Requests (`pip install requests`)
- Google Auth (`pip install google-auth`)
- Google Auth OAuthlib (`pip install google-auth-oauthlib`)
- Google API Client (`pip install google-api-python-client`)
- Cryptography (`pip install cryptography`)
- pycountry-convert (`pip install pycountry-convert`)

Also, ensure that you have created a `client_secret.json` file containing the OAuth 2.0 client_id and client_secret for this application.

## How to Run

1. Clone or download the flask-oauth directory to your local machine.
2. create and activate a virtual environment (optional, but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
   
3. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```

4. Start the Flask development server by running the following command:
   ```
   python app.py
   ```

5. The web application will be available at `http://localhost:8080/` in your web browser.

## Endpoints

### `/`

- Description: Home page of the application. If the user is authenticated, it displays credentials and an inputfield to send the mirror token to the client application. Otherwise, it redirects to the Google OAuth 2.0 authorization page for login.
- Method: GET

### `/send`

- Description: Fetches the google credentials from the session, encrypts it into a mirror token, and sends the token to a specified callback URL.
- Method: GET

### `/my/pdata`

- Description: Fetches and transform personal data (user info) for the authenticated user.
- Method: GET

### `/my/fitdata`

- Description: Fetches and aggregates fitness data for the authenticated user based on the specified aggregation type and weeks.
- Method: GET

### `/authorize`

- Description: Initiates the OAuth 2.0 Authorization Grant Flow to authenticate and authorize the user.
- Method: POST

### `/oauth2callback`

- Description: Handles the callback after the user has authorized the application. It fetches the google OAuth 2.0 tokens and stores them in the session.
- Method: GET

### `/clear`

- Description: Clears the stored credentials of the authenticated user.
- Method: GET

## Additional Notes

- The application uses Flask's session to store user credentials after successful authentication.
- The application uses the `google-auth` library to handle OAuth 2.0 authorization. Make sure to place the `client_secret.json` file containing your own credentials obtained from the Google API Console in the `flask-oauth` directory.
- The `client.py` script implement an example client application that showcase agregated user's fitness data recorded in the last month (further instructions how to run the client [here](CLIENT.md))
- The fitness data aggregation logic is implemented in the `fit_data_agg.py` module.
- The `templates/component` folder contains HTML templates for rendering the login and home pages. Customize these templates according to your requirements.
- The application runs in debug mode (`debug=True`) for development purposes. In a production environment, this should be set to `False`.
