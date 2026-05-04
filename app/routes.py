from flask import render_template, redirect, url_for
from app import app

users = {
    "elara": {
        "name": "DR. ELARA VANCE",
        "level": "Level 42 Lead Pathologist",
        "accuracy": "99.4%",
        "segments": "14,802",
        "weekly_segments": "+240 this week",
        "xp": "84,200",
        "xp_progress": "65%",
        "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuBwkuY2xbL_hE-6lloyVmgXWZPa8MrCpHFPdK_nepmL1lDRHibhFrkDjCHRFG-gRzj7mF_ss_Q_68Sgv0VnGbKu8g5OKSemMBubJVqvwyli1ok-aL9txO5vcqlbMzdJxg8UHqSnd1tR2n1PA52GtU7U6fjdwUuIl3HGAJEMgDyShAMhcGv9Ks_pP6aXN6AgvshmjGQsqM3xchW1vATamciWQeV4sK5CaVpcV6I0oVO5xnpAbR1eNFl_g-CJzyqKQJDSpJyPE9a3EDs"
    },
    "maverick": {
        "name": "DR. MAVERICK ALPHA",
        "level": "Level 35 Radiology Specialist",
        "accuracy": "98.2%",
        "segments": "9,420",
        "weekly_segments": "+115 this week",
        "xp": "64,500",
        "xp_progress": "48%",
        "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuDyq46Y2C7cXphyal-gskknSlsGoordUK0Z7yB1Gask6Pz59wSkC04eK9jtqC5cmsqRRoiyyvbrfHyA_tQkHtpAbKOUi7DJlIDxZ0q218iS4dcaBEUW943s5hdCRXVaN_2p-os4GYIvmc8NHmlWe6zPlaojP02qMNdJc6un6HCBTJWlfXx4pbmGBipbXrEAFXxFLMpnpErMBuba8_X0xbgPicrBTffF7Ei0ItNUO3ths8hFaIS2Z01_dPPlZE-ReBXcaLndFPfEX-Y"
    }
}


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