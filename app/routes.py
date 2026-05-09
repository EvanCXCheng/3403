from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db

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


# ── Public routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html')


# ── Auth routes ────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    from app.forms import LoginForm, RegisterForm
    from app.models import User

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form    = LoginForm()
    register_form = RegisterForm()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            # Re-bind form to current request data for validation
            form = LoginForm()
            if form.validate_on_submit():
                identifier = form.email.data.strip()
                # Allow login by email or username
                user = (User.query.filter_by(email=identifier.lower()).first()
                        or User.query.filter_by(username=identifier).first())
                if user and check_password_hash(user.password_hash, form.password.data):
                    login_user(user)
                    return jsonify({'ok': True, 'redirect': url_for('index')})
                return jsonify({'ok': False, 'field': 'password',
                                'error': 'Invalid email/username or password.'})
            errors = {k: v[0] for k, v in form.errors.items() if k != 'csrf_token'}
            return jsonify({'ok': False, 'errors': errors})

        if action == 'register':
            form = RegisterForm()
            if form.validate_on_submit():
                base     = form.email.data.split('@')[0]
                username = base
                n = 1
                while User.query.filter_by(username=username).first():
                    username = f'{base}{n}'
                    n += 1
                user = User(
                    username=username,
                    email=form.email.data.lower(),
                    password_hash=generate_password_hash(form.password.data),
                )
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return jsonify({'ok': True, 'redirect': url_for('index')})
            errors = {k: v[0] for k, v in form.errors.items() if k != 'csrf_token'}
            return jsonify({'ok': False, 'errors': errors})

        return jsonify({'ok': False, 'error': 'Unknown action.'})

    return render_template('login.html', login_form=login_form, register_form=register_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ── Protected routes ───────────────────────────────────────────────────────────

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/segmentation')
@login_required
def segmentation():
    return render_template('segmentation.html')