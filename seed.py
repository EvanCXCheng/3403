"""
Seed the database with demo data.
Run once after `flask db upgrade`:  python seed.py
Safe to re-run — skips if data already exists.
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import Badge, MedicalImage, Challenge, User, Segmentation, UserBadge, ChallengeEntry


def seed():
    with app.app_context():
        if User.query.first():
            print('Database already seeded — skipping.')
            return

        now = datetime.utcnow()

        # ── Badges ────────────────────────────────────────────────────────────
        b_neural = Badge(
            name='Neural Master',
            description='Complete 1,000 brain segmentations',
            icon='neurology',
            requirement_type='organ_count',
            requirement_value=1000,
            requirement_organ='Brain',
        )
        b_cardio = Badge(
            name='Cardio Precision',
            description='Achieve 99%+ mean accuracy',
            icon='cardiology',
            requirement_type='accuracy',
            requirement_value=99.0,
        )
        b_dna = Badge(
            name='DNA Weaver',
            description='Reach 10,000 total segmentations',
            icon='genetics',
            requirement_type='total_segments',
            requirement_value=10000,
        )
        b_radio = Badge(
            name='Radiology Pro',
            description='Earn 50,000 XP',
            icon='radiology',
            requirement_type='xp',
            requirement_value=50000,
        )
        db.session.add_all([b_neural, b_cardio, b_dna, b_radio])
        db.session.flush()  # get badge IDs before linking

        # ── Medical Images ─────────────────────────────────────────────────────
        img_lung = MedicalImage(
            filename='lung_ct_001.jpg', modality='CT', organ='Lung', difficulty=2,
            description='High-resolution chest CT showing early-stage pulmonary nodule.',
            objective='Segment the pulmonary nodule and isolate its boundary from surrounding tissue.',
        )
        img_brain = MedicalImage(
            filename='brain_mri_001.jpg', modality='MRI', organ='Brain', difficulty=3,
            description='T1-weighted MRI with visible white-matter lesion.',
            objective='Segment the white-matter lesion and label surrounding cortical tissue.',
        )
        img_heart = MedicalImage(
            filename='cardiac_mri_001.jpg', modality='MRI', organ='Heart', difficulty=2,
            description='Cardiac MRI at peak systole.',
            objective='Delineate the left ventricular wall and identify the endocardial boundary.',
        )
        img_liver = MedicalImage(
            filename='liver_ct_001.jpg', modality='CT', organ='Liver', difficulty=2,
            description='Contrast-enhanced CT of abdominal region.',
            objective='Segment the hepatic liver mass and identify arterial vascularization points.',
        )
        img_retina = MedicalImage(
            filename='retina_oct_001.jpg', modality='OCT', organ='Retina', difficulty=3,
            description='Optical coherence tomography of the macula.',
            objective='Segment the retinal layers and mark any areas of drusen deposition.',
        )
        db.session.add_all([img_lung, img_brain, img_heart, img_liver, img_retina])
        db.session.flush()

        # ── Challenges ─────────────────────────────────────────────────────────
        ch_neural = Challenge(
            name='Neural Pathway Precision',
            description='Segment 50 intricate neural fiber tracks with average accuracy above 98.5%.',
            xp_reward=2500, deadline=now + timedelta(hours=24),
            image_modality='MRI', target_accuracy=0.985, target_count=50,
        )
        ch_cardiac = Challenge(
            name='Cardiac Valve Mapping',
            description='Identify micro-calcifications in cardiac valve ultrasound sequences.',
            xp_reward=1800, deadline=now + timedelta(hours=4, minutes=12),
            image_modality='MRI', target_accuracy=0.97, target_count=20,
        )
        ch_retina = Challenge(
            name='Retinal Layer Scan',
            description='Master OCT retinal layer segmentation in rare pathology cases.',
            xp_reward=3200, deadline=now + timedelta(days=7),
            image_modality='OCT', target_accuracy=0.99, target_count=30,
        )
        db.session.add_all([ch_neural, ch_cardiac, ch_retina])
        db.session.flush()

        # ── Users ──────────────────────────────────────────────────────────────
        # Each user's accuracy_sum = total_segments * (accuracy_pct / 100)
        # so that User.accuracy_pct property returns the correct value.
        def make_user(username, email, password, xp, total_segments, accuracy_pct):
            return User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                xp=xp,
                total_segments=total_segments,
                accuracy_sum=round(total_segments * accuracy_pct / 100, 2),
                created_at=now - timedelta(days=total_segments // 10),
            )

        # Leaderboard top players (matching the placeholder names in leaderboard.html)
        u1 = make_user('Neuro_Elite',   'neuro@medseg.io',   'Demo1234!', 42980, 1204, 99.8)
        u2 = make_user('PulseVector',   'pulse@medseg.io',   'Demo1234!', 38120,  988, 99.4)
        u3 = make_user('Synapse_RX',    'synapse@medseg.io', 'Demo1234!', 35440,  842, 98.9)
        u4 = make_user('BioHacker_01',  'bio@medseg.io',     'Demo1234!', 29800,  715, 97.2)
        u5 = make_user('CortexMapper',  'cortex@medseg.io',  'Demo1234!', 27550,  640, 96.8)

        # Demo account shown on the profile page ("Dr. Maverick_Alpha" from leaderboard)
        u_demo = make_user('Maverick_Alpha', 'demo@medseg.io', 'Demo1234!', 12450, 442, 98.2)

        # A few lower-ranked players to fill out the board
        u6 = make_user('ScanMaster',    'scan@medseg.io',    'Demo1234!', 19200,  480, 95.1)
        u7 = make_user('NoduleHunter',  'nodule@medseg.io',  'Demo1234!', 14800,  360, 94.3)
        u8 = make_user('AxialSlice',    'axial@medseg.io',   'Demo1234!',  9300,  210, 92.7)

        all_users = [u1, u2, u3, u4, u5, u_demo, u6, u7, u8]
        db.session.add_all(all_users)
        db.session.flush()

        # ── Segmentations (recent activity for demo account) ───────────────────
        seg_records = [
            Segmentation(
                user_id=u_demo.id, image_id=img_brain.id,
                dice_score=0.94, xp_awarded=450, status='validated',
                submitted_at=now - timedelta(hours=2),
            ),
            Segmentation(
                user_id=u_demo.id, image_id=img_lung.id,
                dice_score=0.97, xp_awarded=820, status='validated',
                submitted_at=now - timedelta(hours=5),
            ),
            Segmentation(
                user_id=u_demo.id, image_id=img_heart.id,
                dice_score=0.88, xp_awarded=120, status='validated',
                submitted_at=now - timedelta(days=1),
            ),
            # A handful for top players so their counts are plausible
            Segmentation(user_id=u1.id, image_id=img_brain.id,  dice_score=0.998, xp_awarded=900, status='validated', submitted_at=now - timedelta(hours=1)),
            Segmentation(user_id=u1.id, image_id=img_retina.id, dice_score=0.997, xp_awarded=850, status='validated', submitted_at=now - timedelta(hours=3)),
            Segmentation(user_id=u2.id, image_id=img_lung.id,   dice_score=0.993, xp_awarded=780, status='validated', submitted_at=now - timedelta(hours=2)),
            Segmentation(user_id=u3.id, image_id=img_heart.id,  dice_score=0.990, xp_awarded=700, status='validated', submitted_at=now - timedelta(hours=4)),
        ]
        db.session.add_all(seg_records)

        # ── Badges earned ──────────────────────────────────────────────────────
        # Top players have earned multiple badges
        badge_links = [
            UserBadge(user_id=u1.id, badge_id=b_neural.id, earned_at=now - timedelta(days=30)),
            UserBadge(user_id=u1.id, badge_id=b_cardio.id, earned_at=now - timedelta(days=20)),
            UserBadge(user_id=u1.id, badge_id=b_radio.id,  earned_at=now - timedelta(days=10)),
            UserBadge(user_id=u2.id, badge_id=b_neural.id, earned_at=now - timedelta(days=25)),
            UserBadge(user_id=u2.id, badge_id=b_cardio.id, earned_at=now - timedelta(days=15)),
            UserBadge(user_id=u3.id, badge_id=b_neural.id, earned_at=now - timedelta(days=20)),
            # Demo user has three badges (matching the profile page UI)
            UserBadge(user_id=u_demo.id, badge_id=b_neural.id, earned_at=now - timedelta(days=60)),
            UserBadge(user_id=u_demo.id, badge_id=b_cardio.id, earned_at=now - timedelta(days=40)),
            UserBadge(user_id=u_demo.id, badge_id=b_dna.id,    earned_at=now - timedelta(days=15)),
        ]
        db.session.add_all(badge_links)

        # ── Challenge entries ──────────────────────────────────────────────────
        challenge_entries = [
            # Demo user: completed retinal, in-progress cardiac
            ChallengeEntry(user_id=u_demo.id, challenge_id=ch_retina.id,  status='completed', progress=30, started_at=now - timedelta(days=5)),
            ChallengeEntry(user_id=u_demo.id, challenge_id=ch_cardiac.id, status='active',    progress=12, started_at=now - timedelta(hours=2)),
            # Top players active on neural challenge
            ChallengeEntry(user_id=u1.id, challenge_id=ch_neural.id,  status='active',    progress=38, started_at=now - timedelta(hours=10)),
            ChallengeEntry(user_id=u2.id, challenge_id=ch_neural.id,  status='active',    progress=21, started_at=now - timedelta(hours=8)),
            ChallengeEntry(user_id=u3.id, challenge_id=ch_cardiac.id, status='completed', progress=20, started_at=now - timedelta(days=1)),
        ]
        db.session.add_all(challenge_entries)

        db.session.commit()
        print('Database seeded successfully.')
        print('Demo login:  demo@medseg.io  /  Demo1234!')


if __name__ == '__main__':
    seed()
