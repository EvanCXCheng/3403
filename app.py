from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db       = SQLAlchemy(app)
migrate  = Migrate(app, db)
csrf     = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view    = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


# ── Public routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


# ── Auth routes ────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms import LoginForm, RegisterForm
    from models import User

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


# Models must be imported after db is defined so Flask-Migrate can find them
import models  # noqa: E402, F401


if __name__ == '__main__':
    app.run(debug=True)
