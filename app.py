from flask import Flask, render_template
import requests
app = Flask(__name__)

rapidapi-key = "6948397d3fmsh016ac5964e79765p1f044djsn300adf413fe5"
rapidapi-host = "mountain-api1.p.rapidapi.com"

@app.route('/')
def domov():
    return render_template('index.html', prijava=True)

def gore_data():
    global rapidapi-key
    global rapidapi-host

    url = "https://mountain-api1.p.rapidapi.com/api/mountains"

    querystring = {"name":"Mount Everest"}

    headers = {
        "x-rapidapi-key": rapidapi-key,
        "x-rapidapi-host": rapidapi-host
    }

    response = requests.get(url, headers=headers, params=querystring)

return response.json()

if __name__ == '__main__':
    app.run(debug=True)