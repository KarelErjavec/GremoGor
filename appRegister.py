from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


users = []

@app.route('/')
def index():
    return 'Dobrodošli na spletni strani!'

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

        
        users.append({
            'ime': ime,
            'priimek': priimek,
            'email': email,
            'username': username,
            'password': password  # Nikoli ne shranjuj gesel v plaintextu! (uporabi hashiranje gesel)
        })
        
        
        return redirect(url_for('index'))
    
    
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
