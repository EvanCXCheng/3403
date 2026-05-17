"""Unit tests for Flask routes via the test client."""
import json

import pytest
from werkzeug.security import generate_password_hash

from app.models import User
from tests.conftest import TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME


def post_login(client, action, email, password):
    resp = client.post('/login', data={
        'action': action,
        'email': email,
        'password': password,
    })
    return resp, json.loads(resp.data)


# ── Public access ─────────────────────────────────────────────────────────────

def test_homepage_returns_200(client):
    assert client.get('/').status_code == 200


def test_login_page_returns_200(client):
    assert client.get('/login').status_code == 200


def test_leaderboard_redirects_unauthenticated_users(client):
    resp = client.get('/leaderboard')
    assert resp.status_code == 302
    assert 'login' in resp.headers['Location'].lower()


# ── Registration ──────────────────────────────────────────────────────────────

def test_register_with_valid_credentials_succeeds(client):
    _, data = post_login(client, 'register', 'fresh@example.com', 'ValidPass1!')
    assert data['ok'] is True
    assert 'redirect' in data


def test_register_with_duplicate_email_fails(client):
    _, data = post_login(client, 'register', TEST_EMAIL, 'ValidPass1!')
    assert data['ok'] is False


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_with_correct_credentials_succeeds(client):
    _, data = post_login(client, 'login', TEST_EMAIL, TEST_PASSWORD)
    assert data['ok'] is True


def test_login_with_username_succeeds(client):
    _, data = post_login(client, 'login', TEST_USERNAME, TEST_PASSWORD)
    assert data['ok'] is True


def test_login_with_wrong_password_fails(client):
    _, data = post_login(client, 'login', TEST_EMAIL, 'WrongPass1!')
    assert data['ok'] is False


# ── Authenticated routes ──────────────────────────────────────────────────────

def test_leaderboard_no_crash_for_new_user_with_zero_xp(client, db):
    """Regression: new users with xp=0 previously caused TypeError (None > 3)."""
    db.session.add(User(
        username='zeroxp',
        email='zeroxp@example.com',
        password_hash=generate_password_hash('ZeroXP123!'),
        xp=0,
        total_segments=0,
        accuracy_sum=0.0,
    ))
    db.session.commit()

    # Log in as the zero-xp user (ignore JSON response — we just need the session)
    client.post('/login', data={
        'action': 'login',
        'email': 'zeroxp@example.com',
        'password': 'ZeroXP123!',
    })
    assert client.get('/leaderboard').status_code == 200
