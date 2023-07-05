<<<<<<< HEAD
from flask import Flask, render_template,request,url_for,jsonify
=======
from flask import Flask, render_template
>>>>>>> d6030ee1596d4319889d9bc2eee58525beb914be

app = Flask(__name__, template_folder='templates')


@app.route("/")
def home():
<<<<<<< HEAD

    return render_template('home.html')

@app.route("/callback",methods=['POST'])
def callback():
    data= request.get_json()
    with open('out.json','w') as file:
        file.write(data)
    url = request.host_url+url_for('home')
    
    response = {'redirect_link': url}

    return jsonify(response)
=======
    return render_template('home.html')


>>>>>>> d6030ee1596d4319889d9bc2eee58525beb914be
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=3000)
