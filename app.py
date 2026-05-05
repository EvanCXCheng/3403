from flask import Flask, render_template
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/segmentation')
def segmentation():
    return render_template('segmentation.html')


if __name__ == '__main__':
    app.run(debug=True)
