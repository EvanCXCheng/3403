import os

import pytest
from werkzeug.security import generate_password_hash

from app import app as flask_app, db as _db
from app.models import User, MedicalImage

TEST_EMAIL    = 'unit_test@example.com'
TEST_PASSWORD = 'Password1!'
TEST_USERNAME = 'unit_tester'

# File-based test DB avoids StaticPool complexity; lives in the tests/ folder.
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_unit.db')


@pytest.fixture(scope='session')
def app():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{TEST_DB_PATH}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'unit-test-secret',
    })
    yield flask_app

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


# Separate fixture so the app context doesn't stay alive across all tests —
# a persistent outer context would cause Flask-Login's current_user to bleed
# between test requests.
# NOTE: we never call _db.drop_all() — Flask-SQLAlchemy may have a cached
# engine pointing at the production DB, and drop_all() on the wrong engine
# would wipe live data. Deleting the file is the safe alternative.
@pytest.fixture(scope='session')
def setup_db(app):
    with app.app_context():
        _db.create_all()
        _seed(_db)
    yield


def _seed(db):
    if not User.query.filter_by(email=TEST_EMAIL).first():
        db.session.add(User(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password_hash=generate_password_hash(TEST_PASSWORD),
            xp=100,
            total_segments=2,
            accuracy_sum=1.5,
        ))
    if not MedicalImage.query.filter_by(filename='images/liver_ct_000.png').first():
        db.session.add(MedicalImage(
            filename='images/liver_ct_000.png',
            modality='CT',
            organ='Liver',
            difficulty=2,
            series_id=1,
            ground_truth_path='images/ground_truth/liver_GT_000.png',
            objective='Segment the liver.',
        ))
    db.session.commit()


@pytest.fixture()
def client(app, setup_db):
    with app.test_client() as c:
        yield c


@pytest.fixture()
def db(app, setup_db):
    with app.app_context():
        yield _db
