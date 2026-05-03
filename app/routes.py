from flask import render_template, redirect, url_for
from app import app

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/profile')
def profile_default():
    return redirect(url_for('profile', username='elara'))


@app.route('/profile/<username>')
def profile(username):
    users = { # User dictionary is a filler for future database
        "elara": {
            "name": "DR. ELARA VANCE",
            "level": "Level 42 Lead Pathologist",
            "accuracy": "99.4%",
            "segments": "14,802",
            "xp": "84,200"
        },
        "maverick": {
            "name": "DR. MAVERICK ALPHA",
            "level": "Level 35 Radiology Specialist",
            "accuracy": "98.2%",
            "segments": "9,420",
            "xp": "64,500"
        }
    }

    user = users.get(username)

    if user is None:
        return "User not found", 404

    return render_template('profile.html', user=user)


@app.route('/segmentation-tool')
def segmentation_tool():
    return render_template('segmentation_tool.html')


@app.route('/login')
def login():
    return render_template('login.html')