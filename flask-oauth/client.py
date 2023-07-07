
from flask import Flask, render_template,request,url_for,jsonify,redirect
import json
import requests
app = Flask(__name__, template_folder='templates')



@app.route("/")
def home():
    try:
        with open('out.json', 'r') as f:
            token = json.load(f)
            pdata = requests.get('http://localhost:8080/my/pdata',headers={'Authorization':token['token']})
            fitdata = requests.get('http://localhost:8080/my/fitdata',headers={'Authorization':token['token']})
            if(pdata.status_code != 200):
                return jsonify({'error' : 'missing pdata '+str(pdata.status_code)})
            if(pdata.status_code != 200):
                return jsonify({'error' : 'missing pdata '+str(pdata.status_code)} )   
            return jsonify({
                **pdata.json(),
                **fitdata.json()
            })
    except:
        return render_template('home.html')

@app.route("/callback",methods=['POST'])
def callback():
    data= request.get_json()
    with open('out.json','w') as file:
        file.write(json.dumps(data))
    url = request.host_url+url_for('home')
    
    response = {'redirect_link': url}

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=3000)
