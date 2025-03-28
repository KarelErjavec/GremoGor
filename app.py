from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def domov():
    return render_template('index.html', prijava=True)

if __name__ == '__main__':
    app.run(debug=True)