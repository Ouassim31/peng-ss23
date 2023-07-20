
from flask import Flask, render_template,request,url_for,jsonify,redirect
import json
import requests
import os
import csv
app = Flask(__name__, template_folder='templates')

@app.route("/profile")
def profile():
    try:
        with open('mirror_token.json', 'r') as f:
            token = json.load(f)
            pdata = requests.get('http://localhost:8080/my/pdata',headers={'Authorization':token['token']})
            fitdata = requests.get('http://localhost:8080/my/fitdata?aggtype=1&weeks=4',headers={'Authorization':token['token']})
            if(pdata.status_code != 200):
                return jsonify({'error' : 'missing pdata '+str(pdata.status_code)})
            if(pdata.status_code != 200):
                return jsonify({'error' : 'missing pdata '+str(pdata.status_code)} )   
            response = {
                **pdata.json(),
                'fitdata': fitdata.json()
            }
            with open('test_results/test_user.json', 'w' ) as file :
                file.write(json.dumps(response))
            return render_template('client/profile.html', response=response)
    except:
        return redirect(url_for('home'))
@app.route("/login")
def login():
    return render_template('client/login.html')
@app.route("/logout")
def logout():
    os.remove('mirror_token.json')
    return redirect(url_for('login'))
@app.route("/")  
def home():
    try:
        with open('mirror_token.json', 'r') as f:
            token = json.load(f)
            pdata = requests.get('http://localhost:8080/my/pdata',headers={'Authorization':token['token']})
            if(pdata.status_code != 200):
                return redirect(url_for('login'))
  
            return render_template('client/home.html', pdata=pdata.json())
    except FileNotFoundError :
        return redirect(url_for('login'))
@app.route("/callback",methods=['POST'])
def callback():
    data= request.get_json()
    try:
        with open('mirror_token.json','w') as file:
            file.write(json.dumps(data))
        url = request.host_url+url_for('home')
        return jsonify({'redirect_link': 'http://localhost:3000/'})   
    except:
        return jsonify({'error':'send failed'})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=3000)
