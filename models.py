from datetime import datetime
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """Registered player account."""
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    email         = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    xp            = db.Column(db.Integer, default=0)
    total_segments = db.Column(db.Integer, default=0)
    # Running sum of dice scores; divide by total_segments for mean accuracy
    accuracy_sum  = db.Column(db.Float, default=0.0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    segmentations  = db.relationship('Segmentation', backref='user', lazy=True)
    earned_badges  = db.relationship('UserBadge',    backref='user', lazy=True)
    challenge_entries = db.relationship('ChallengeEntry', backref='user', lazy=True)

    @property
    def accuracy_pct(self):
        """Mean segmentation accuracy as a percentage (0–100)."""
        if self.total_segments == 0:
            return 0.0
        return round((self.accuracy_sum / self.total_segments) * 100, 1)

    def __repr__(self):
        return f'<User {self.username}>'


class MedicalImage(db.Model):
    """A single medical scan available for segmentation."""
    id         = db.Column(db.Integer, primary_key=True)
    filename   = db.Column(db.String(256), nullable=False)
    modality   = db.Column(db.String(32),  nullable=False)   # CT | MRI | X-Ray
    organ      = db.Column(db.String(64),  nullable=False)
    difficulty = db.Column(db.Integer, default=1)             # 1 easy → 3 hard
    description = db.Column(db.Text)
    objective   = db.Column(db.Text)

    segmentations = db.relationship('Segmentation', backref='image', lazy=True)

    def __repr__(self):
        return f'<MedicalImage {self.modality}/{self.organ} id={self.id}>'


class Segmentation(db.Model):
    """One user's submitted segmentation of one image."""
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'),          nullable=False)
    image_id     = db.Column(db.Integer, db.ForeignKey('medical_image.id'), nullable=False)
    dice_score   = db.Column(db.Float)
    xp_awarded   = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    # pending → awaiting consensus validation; validated → score finalised
    status       = db.Column(db.String(32), default='pending')

    def __repr__(self):
        return f'<Segmentation user={self.user_id} image={self.image_id} dice={self.dice_score}>'


class Badge(db.Model):
    """An achievement that can be earned by a player."""
    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(64),  nullable=False)
    description       = db.Column(db.String(256))
    icon              = db.Column(db.String(64))   # Material Symbols icon name
    # What metric triggers the badge: xp | total_segments | accuracy | organ_count
    requirement_type  = db.Column(db.String(32))
    requirement_value = db.Column(db.Float)
    # For organ_count badges, which organ must reach the threshold
    requirement_organ = db.Column(db.String(64))

    holders = db.relationship('UserBadge', backref='badge', lazy=True)

    def __repr__(self):
        return f'<Badge {self.name}>'


class UserBadge(db.Model):
    """Junction: which badges a user has earned and when."""
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    badge_id  = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id'),)

    def __repr__(self):
        return f'<UserBadge user={self.user_id} badge={self.badge_id}>'


class Challenge(db.Model):
    """A timed competitive task with bonus XP."""
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(128), nullable=False)
    description     = db.Column(db.Text)
    xp_reward       = db.Column(db.Integer, default=0)
    deadline        = db.Column(db.DateTime)
    image_modality  = db.Column(db.String(32))   # filter images by this modality
    target_accuracy = db.Column(db.Float)         # minimum dice score to count
    target_count    = db.Column(db.Integer)       # how many images to complete

    entries = db.relationship('ChallengeEntry', backref='challenge', lazy=True)

    def __repr__(self):
        return f'<Challenge {self.name}>'


class ChallengeEntry(db.Model):
    """Tracks a user's progress through one challenge."""
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'),       nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'),  nullable=False)
    # active | completed
    status       = db.Column(db.String(32), default='active')
    progress     = db.Column(db.Integer, default=0)   # images completed so far
    started_at   = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'challenge_id'),)

    def __repr__(self):
        return f'<ChallengeEntry user={self.user_id} challenge={self.challenge_id}>'
