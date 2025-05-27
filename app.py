from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import bcrypt
import datetime

#tinydb
from tinydb import TinyDB, Query
users = TinyDB('data/users.json')
friends = TinyDB('data/friends.json')
User = Query()

app = Flask(__name__)
app.secret_key = "temp"

@app.route('/')
def domov():
    user=session.get('username')
    if not user:
        user="none"
    return render_template('index.html', user=user)

@app.route("/search", methods=['POST'])
def search():
    ime=request.form["search"]
    return redirect(f'/gora/{ime}')

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
            'password': hash_pass(password)
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
        print("Form data:", request.form)
        if 'email' not in request.form or 'password' not in request.form:
            return 'Manjkajoči podatki v obrazcu: potrebna sta email in geslo'

        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            return 'Email in geslo sta obvezna'

        user = users.get(User.email == email)

        if user and check_pass(user['password'], password):

            session['email'] = email
            session['username'] = user['username']
            session['ime'] = user['ime']
            session['priimek'] = user['priimek']
            return redirect(url_for('domov'))
        else:
            return 'Napačen email ali geslo'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('domov'))

@app.route('/profile',methods=['GET', 'POST'])
def profile():

    username = session.get('username')

    if not username:
        return redirect(url_for('login'))

    Friend = Query()
    user_friends = friends.search((Friend.user == username) | (Friend.friend == username))

    friend_list = []
    for friendship in user_friends:
        if friendship['status'] == 'accepted':
            if friendship['user'] == username:
                friend_list.append(friendship['friend'])
            else:
                friend_list.append(friendship['user'])

    friend_details = []
    for friend_username in friend_list:
        friend = users.get(User.username == friend_username)
        if friend:
            friend_details.append({
                'username': friend['username'],
                'ime': friend['ime'],
                'priimek': friend['priimek']
            })

    return render_template('Userpage.html', user=username, friends=friend_details)

@app.route('/set/profile/', methods=['GET'])
def setprof():
    return render_template('settings/profile.html', ime=session.get('ime'), priimek=session.get('priimek'), email=session.get('email'), username=session.get('username'))

@app.route('/set/del/', methods=['GET'])
def delprof():
    return render_template('settings/delete.html')

@app.route('/set/del/yes/')
def delete():
    users.remove(User.username==session.get('username'))
    session.clear()
    return 'Račun Izbrisan.'

@app.route('/set', methods=['POST'])
def setuppost():
    ime = request.form["ime"]
    priimek = request.form['priimek']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    user = users.get(User.email == session.get('email'))

    if any(user['username'] == username for user in users):
        return 'Uporabniško ime je že v uporabi!'

    if user:
        updates = {}
        if ime:
            updates['ime'] = ime
            session['ime'] = ime

        if priimek:
            updates['priimek'] = priimek
            session['priimek'] = priimek

        if email:
            updates['email'] = email
            session['email'] = email

        if username:
            updates['username'] = username
            session['username'] = username

        if password:
            updates['password'] = hash_pass(password)

        users.update(updates, User.email == session.get('email'))
    return(redirect(url_for('setprof')))

@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Niste prijavljeni'})

    data = request.get_json()
    if not data or 'friend_username' not in data:
        return jsonify({'success': False, 'message': 'Manjkajoči podatki'})

    user = session['username']
    friend_username = data['friend_username']

    if not users.get(User.username == friend_username):
        return jsonify({'success': False, 'message': 'Uporabnik ne obstaja'})

    if user == friend_username:
        return jsonify({'success': False, 'message': 'Ne morete dodati sebe kot prijatelja'})

    Friend = Query()
    existing_friendship = friends.get(
        ((Friend.user == user) & (Friend.friend == friend_username)) |
        ((Friend.user == friend_username) & (Friend.friend == user))
    )

    if existing_friendship:
        if existing_friendship['status'] == 'accepted':
            return jsonify({'success': False, 'message': 'Uporabnik je že vaš prijatelj'})
        elif existing_friendship['status'] == 'pending':
            if existing_friendship['user'] == user:
                return jsonify({'success': False, 'message': 'Prošnja za prijateljstvo je že poslana'})
            else:

                friends.update({'status': 'accepted'},
                              ((Friend.user == friend_username) & (Friend.friend == user)))
                return jsonify({'success': True, 'message': 'Prijateljstvo sprejeto'})

    friends.insert({
        'user': user,
        'friend': friend_username,
        'status': 'pending',
        'date_sent': str(datetime.datetime.now())
    })

    return jsonify({'success': True, 'message': 'Prošnja za prijateljstvo poslana'})

@app.route('/friend_requests', methods=['GET'])
def friend_requests():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Niste prijavljeni'})

    user = session['username']
    Friend = Query()

    pending_requests = friends.search(
        (Friend.friend == user) & (Friend.status == 'pending')
    )

    request_details = []
    for request in pending_requests:
        sender = users.get(User.username == request['user'])
        if sender:
            request_details.append({
                'username': sender['username'],
                'ime': sender['ime'],
                'priimek': sender['priimek']
            })

    return jsonify({'success': True, 'requests': request_details})

@app.route('/decline_friend', methods=['POST'])
def decline_friend():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Niste prijavljeni'})

    data = request.get_json()
    if not data or 'friend_username' not in data:
        return jsonify({'success': False, 'message': 'Manjkajoči podatki'})

    user = session['username']
    friend_username = data['friend_username']

    Friend = Query()
    existing_request = friends.get(
        (Friend.user == friend_username) & (Friend.friend == user) & (Friend.status == 'pending')
    )

    if not existing_request:
        return jsonify({'success': False, 'message': 'Prošnja za prijateljstvo ne obstaja'})

    friends.remove(
        (Friend.user == friend_username) & (Friend.friend == user)
    )

    return jsonify({'success': True, 'message': 'Prošnja za prijateljstvo zavrnjena'})

@app.route('/gora/<mountain_name>', methods=['GET'])
def gore_data(mountain_name):
    data = get_mountain_info(mountain_name)
    #print(data)
    return render_template('gora.html', data=data)

mountain_array = [
    "Triglav", "Škrlatica", "Mangart", "Jalovec", "Krn", 
    "Tosc", "Razor", "Prisojnik", "Vrh nad Vršičem", 
    "Grintovec", "Rjavina", "Veliki Draški vrh", 
    "Spodnje Sleme", "Stador","Hochstuhl","škrlatica"
]


# Wikidata API
def get_mountain_info(mountain_name):
    if mountain_name not in mountain_array:
        return redirect(url_for('domov'))
    
    # iskanje 
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        'action': 'wbsearchentities',
        'search': mountain_name,
        'language': 'si',
        'format': 'json'
    }
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()

    
    if not search_data['search']:
        return
 
    # prvi rezultat
    mountain_entity = search_data['search'][0]
    mountain_id = mountain_entity['id']
 
    # pridobitev podatkov
    entity_url = "https://www.wikidata.org/w/api.php"
    entity_params = {
        'action': 'wbgetentities',
        'ids': mountain_id,
        'props': 'claims|labels',
        'format': 'json'
    }
 
    entity_response = requests.get(entity_url, params=entity_params)
    entity_data = entity_response.json()
 
    # višina (P2048), lokacija (P625)
    claims = entity_data['entities'][mountain_id]['claims']
    labels = entity_data['entities'][mountain_id]['labels']
 
    height = claims.get('P2044', [])
    location = claims.get('P625', [])
    img = claims.get('P18', [])
 
    # mm - m
    if height:
        height_value = int(round(float(height[0]['mainsnak']['datavalue']['value']['amount']), 0))
    else:
        height_value = None
    #lokacija
    mountain_label = labels.get('en', {}).get('value', mountain_name)
 
    # lokacija
    if location:
        latitude = location[0]['mainsnak']['datavalue']['value']['latitude']
        longitude = location[0]['mainsnak']['datavalue']['value']['longitude']
        location_value = (latitude, longitude)
    else:
        location_value = None

    # url slike
    if img: 
        img_value=requests.get(f"https://commons.wikimedia.org/wiki/Special:FilePath/{img[0]['mainsnak']['datavalue']['value']}").url

    else: img_value = None
 
    return {
        "mount" : mountain_label,
        "height" : height_value,
        "location" : location_value,
        "img" : img_value
    }

def hash_pass(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return (bcrypt.hashpw(password_bytes, salt)).decode() #podatkovni tipi

def check_pass(hashed, password):
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed.encode('utf-8'))

@app.route('/check_users')
def check_users():
    all_users = users.all()
    return jsonify(all_users)

if __name__ == '__main__':
    app.run(debug=True)
