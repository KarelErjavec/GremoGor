from flask import Flask, render_template, request
import requests
app = Flask(__name__)

#tinydb
from tinydb import TinyDB, Query
users = TinyDB('data/users.json')

#mountainapi
rapidapi_key = "6948397d3fmsh016ac5964e79765p1f044djsn300adf413fe5"
rapidapi_host = "mountain-api1.p.rapidapi.com"

app = Flask(__name__)

@app.route('/')
def domov():
    return render_template('index.html', prijava=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        ime = request.form.get("ime")
        priimek = request.form.get('priimek')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        
        if any(user['username'] == username for user in users):
            return 'Uporabniško ime je že v uporabi!'

        
        users.insert({
            'ime': ime,
            'priimek': priimek,
            'email': email,
            'username': username,
            'password': password  # Nikoli ne shranjuj gesel v plaintextu! (uporabi hashiranje gesel)
        })
        
        
        return redirect(url_for('index'))
    
    
    return render_template('register.html')

def gore_data():
    global rapidapi_key
    global rapidapi_host

    url = "https://mountain-api1.p.rapidapi.com/api/mountains"
 
    querystring = {"name":"Mount Everest"}

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": rapidapi_host
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()

if __name__ == '__main__':
    app.run(debug=True)