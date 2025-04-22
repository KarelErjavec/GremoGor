from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests

#tinydb
from tinydb import TinyDB, Query
users = TinyDB('data/users.json')

#mountainapi
rapidapi_key = "6948397d3fmsh016ac5964e79765p1f044djsn300adf413fe5"
rapidapi_host = "mountain-api1.p.rapidapi.com"

app = Flask(__name__)
app.secret_key = "temp"

@app.route('/')
def domov():
    user=session.get('username')
    if not user:
        user="none"
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        ime = request.form["ime"]
        priimek = request.form['priimek']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        
        if any(user['username'] == username for user in users):
            return 'Uporabniško ime je že v uporabi!'

        print(ime)

        users.insert({
            'ime': ime,
            'priimek': priimek,
            'email': email,
            'username': username,
            'password': password  # Nikoli ne shranjuj gesel v plaintextu! (uporabi hashiranje gesel)
        })

        session["ime"] = ime
        session["priimek"] = priimek
        session["email"] = email
        session["username"] = username
        #session["password"] = password
        
        
        return redirect(url_for('domov'))
    
    
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #print(request.form["geslo"], request.form["email"])
        #return jsonify({'success': True})

        email = request.form['email']
        password = request.form['password']
        User = Query()
        user = users.get(User.email == email)
        #print(email,password)
        if user:
            if user['password'] == password:
                session['email'] = email
                session['username'] = users['username']
                session['ime'] = users['ime']
                ession['priimek'] = users['priimek']
                return redirect(url_for('domov'))
            else:
                return jsonify({'success': False, 'error': 'Napačno geslo'})
        else:
            return jsonify({'success': False, 'error': 'Uporabnik ne obstaja'})

                
        
        
    return render_template('login.html')
   
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
