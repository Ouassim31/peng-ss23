
# PENG E-STORE Flask Application

This is a simple Flask web application for the PENG E-STORE. It showcases functionality for user authentication, user profile display, and fetching fitdata.

## Prerequisites

Before running the application, make sure you have Python and the required packages installed. You can install the necessary packages using the provided `requirements.txt` file. To do this, run the following command:

```bash
pip install -r requirements.txt
```
## Usage

The provided code is a Flask application that serves a simple e-store website. The application allows users to log in with Google, view their profile information, and see some fit data. The front-end uses HTML templates to render the web pages, and the back-end uses Flask to handle requests and fetch data from an API.

To use the GUI and run the application, follow these steps:

1. Install Required Packages:
   Make sure you have the required packages installed. If you haven't installed them already, you can do so by creating a virtual environment and then installing the packages using the provided `requirements.txt` file.

   First, create and activate a virtual environment (optional, but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

   Next, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Flask Application:

   Run the Flask application using the following command:
   ```bash
   python client.py
   ```

   The application will start and run on `localhost:3000`.

3. Access the Website:
   Open your web browser and navigate to `http://localhost:3000/`. You should see the e-store website with a login button.

4. Logging In:
   Chose the all the scopes and Click on the "Login with Google" button, and it will redirect you to a Google login page. After successful login, you will be redirected to your profile page.

5. Viewing Profile:
   Once logged in, you will see your profile page by clicking on the button "Profile" displaying your email, first name, gender, ID, adult status, and region. The fit data will also be shown in a table.

6. Logging Out:
   To log out, click on the "Logout" button. This will remove the `mirror_token.json` file, which contains your authentication token, and redirect you to the login page again.

## Endpoints

### 1. `/`

This is the home page of the application. If the user is authenticated, their profile data will be fetched and displayed on this page. Otherwise, they will be redirected to the login page.

### 2. `/login`

The login page allows users to sign in to the application using their Google account and chose scopes to login with. Upon successful login, the user will be redirected back to the home page.

### 3. `/logout`

Clicking on the "Logout" button on the navigation bar will remove the user's authentication token from the session and redirect them to the login page.

### 4. `/profile`

The profile page displays the user's profile information fetched from the PENG-component. It also fetches fitdata from the server and displays it in a table.

## Templates

The Flask application uses the following HTML templates stored in the `templates/client` folder:

### 1. `home.html`

This template displays the home page of the application. It shows a welcome message to the user and provides navigation links, including a "Profile" button and a "Logout" button.

### 2. `login.html`

The login page allows users to sign in to the application using their Google account. It provides a button to initiate the login process and checkboxes for the scopes.

### 3. `profile.html`

The profile page displays the user's profile information and fitdata. It shows the user's email, first name, gender, ID, age category, and region.

