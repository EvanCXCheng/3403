import base64
import os
import random
from datetime import datetime

import numpy as np
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import User, Friendship
from sqlalchemy import or_, and_

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


# ── Quest helper ───────────────────────────────────────────────────────────────

_MODALITY_ICONS = {
    'CT':    'radiology',
    'MRI':   'neurology',
    'OCT':   'visibility',
    'X-Ray': 'patient_list',
}

def get_quests():
    """Return one quest dict per distinct series_id in MedicalImage."""
    from app.models import MedicalImage
    from sqlalchemy import func

    rows = (
        db.session.query(
            MedicalImage.series_id,
            MedicalImage.organ,
            MedicalImage.modality,
            MedicalImage.difficulty,
            func.count(MedicalImage.id).label('total'),
        )
        .filter(MedicalImage.series_id.isnot(None))
        .group_by(MedicalImage.series_id)
        .order_by(MedicalImage.series_id)
        .all()
    )

    quests = []
    for row in rows:
        # Use the middle slice as a representative thumbnail
        mid = MedicalImage.query.filter_by(series_id=row.series_id) \
                .order_by(MedicalImage.id) \
                .offset(row.total // 2).first()
        quests.append({
            'series_id': row.series_id,
            'name':      f'{row.organ} {row.modality} Series',
            'modality':  row.modality,
            'difficulty': row.difficulty or 1,
            'total':     row.total,
            'description': (
                f'Annotate {row.total} {row.modality} slices of the '
                f'{row.organ.lower()} to build a complete ground-truth dataset.'
            ),
            'thumbnail': mid.filename if mid else None,
            'icon':      _MODALITY_ICONS.get(row.modality, 'biotech'),
        })
    return quests


# ── Public routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('homepage.html', quests=get_quests())


@app.route('/leaderboard')
@login_required
def leaderboard():
    from app.models import User

    global_players = User.query.order_by(User.xp.desc()).limit(20).all()
    current_user_rank = (User.query.filter(User.xp > current_user.xp).count() + 1) if current_user.xp else None
    friends = Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == current_user.id, Friendship.status == 'accepted'),
            and_(Friendship.receiver_id == current_user.id, Friendship.status == 'accepted')
        )
    ).all()
    friend_ids = {current_user.id}
    for f in friends:
        friend_ids.add(f.receiver_id if f.requester_id == current_user.id else f.requester_id)

    friend_players = User.query.filter(User.id.in_(friend_ids)).order_by(User.xp.desc()).all()
    current_user_rank_global = (User.query.filter(User.xp > current_user.xp).count() + 1) if current_user.xp else None
    current_user_rank_friends = (User.query.filter(User.xp > current_user.xp, User.id.in_(friend_ids)).count() + 1) if current_user.xp else None
    pin_global = current_user_rank_global > 3
    pin_friends = current_user_rank_friends > 3
    return render_template('leaderboard.html', global_players=global_players, friend_players=friend_players, quests=get_quests(), current_user=current_user, 
                            current_user_rank_global=current_user_rank_global, current_user_rank_friends=current_user_rank_friends, pin_global=pin_global, pin_friends=pin_friends)

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
    # Accepted friendships where current user is either requester or receiver
    friendships = Friendship.query.filter(
        or_(
            and_(
                Friendship.requester_id == current_user.id,
                Friendship.status == 'accepted'
            ),
            and_(
                Friendship.receiver_id == current_user.id,
                Friendship.status == 'accepted'
            )
        )
    ).all()

    # Pending requests sent to current user
    pending_requests = Friendship.query.filter_by(
        receiver_id=current_user.id,
        status='pending'
    ).all()

    # Pending requests sent by current user
    sent_requests = Friendship.query.filter_by(
        requester_id=current_user.id,
        status='pending'
    ).all()

    # IDs of users already connected/requested either direction
    connected_ids = {current_user.id}

    all_friend_records = Friendship.query.filter(
        or_(
            Friendship.requester_id == current_user.id,
            Friendship.receiver_id == current_user.id
        )
    ).all()

    for record in all_friend_records:
        connected_ids.add(record.requester_id)
        connected_ids.add(record.receiver_id)

    # Users current user can still add
    suggested_users = User.query.filter(
        ~User.id.in_(connected_ids)
    ).all()
    return render_template(
        'profile.html',
        friendships=friendships,
        pending_requests=pending_requests,
        sent_requests=sent_requests,
        suggested_users=suggested_users
)

@app.route('/friend-request/accept/<int:friendship_id>', methods=['POST'])
@login_required
def accept_friend_request(friendship_id):
    friendship = Friendship.query.get_or_404(friendship_id)

    if friendship.receiver_id != current_user.id:
        return redirect(url_for('profile'))

    friendship.status = 'accepted'
    db.session.commit()

    return redirect(url_for('profile'))

@app.route('/friend-request/decline/<int:friendship_id>', methods=['POST'])
@login_required
def decline_friend_request(friendship_id):
    friendship = Friendship.query.get_or_404(friendship_id)

    if friendship.receiver_id != current_user.id:
        return redirect(url_for('profile'))

    db.session.delete(friendship)
    db.session.commit()

    return redirect(url_for('profile'))

@app.route('/friend-request/send/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    if user_id == current_user.id:
        return redirect(url_for('profile'))

    existing = Friendship.query.filter(
        or_(
            and_(
                Friendship.requester_id == current_user.id,
                Friendship.receiver_id == user_id
            ),
            and_(
                Friendship.requester_id == user_id,
                Friendship.receiver_id == current_user.id
            )
        )
    ).first()

    if existing:
        return redirect(url_for('profile'))

    friendship = Friendship(
        requester_id=current_user.id,
        receiver_id=user_id,
        status='pending'
    )

    db.session.add(friendship)
    db.session.commit()

    return redirect(url_for('profile'))

@app.route('/segmentation')
@login_required
def segmentation():
    from app.models import MedicalImage, Segmentation
    # Pick a random liver CT image the current user hasn't segmented yet
    done_ids = {s.image_id for s in Segmentation.query.filter_by(user_id=current_user.id).all()}
    candidates = MedicalImage.query.filter_by(series_id=1).filter(
        ~MedicalImage.id.in_(done_ids)
    ).all()
    if not candidates:
        # All done — pick any random one to allow re-attempts
        candidates = MedicalImage.query.filter_by(series_id=1).all()
    image = random.choice(candidates)
    return render_template('segmentation.html', image=image)


@app.route('/api/segmentation/submit', methods=['POST'])
@login_required
def submit_segmentation():
    from app.models import MedicalImage, Segmentation

    data = request.get_json(force=True)
    image_id      = data.get('image_id')
    mask_b64      = data.get('mask')          # data:image/png;base64,...
    img_offset_x  = float(data.get('img_offset_x', 0))
    img_offset_y  = float(data.get('img_offset_y', 0))
    img_display_w = float(data.get('img_display_w', 0))
    img_display_h = float(data.get('img_display_h', 0))

    med_img = MedicalImage.query.get(image_id)
    if not med_img:
        return jsonify({'ok': False, 'error': 'Image not found.'}), 404

    # ── Decode submitted canvas mask ──────────────────────────────────────────
    header, b64data = mask_b64.split(',', 1)
    raw_bytes = base64.b64decode(b64data)

    import io
    canvas_img = Image.open(io.BytesIO(raw_bytes)).convert('RGBA')
    cw, ch = canvas_img.size

    # Crop to the region where the scan image was displayed (remove letterboxing)
    ox = max(0, int(round(img_offset_x)))
    oy = max(0, int(round(img_offset_y)))
    dw = max(1, int(round(img_display_w)))
    dh = max(1, int(round(img_display_h)))
    # Clamp to canvas bounds
    ox2 = min(ox + dw, cw)
    oy2 = min(oy + dh, ch)
    cropped = canvas_img.crop((ox, oy, ox2, oy2))

    # ── Load ground-truth mask and resize crop to match ───────────────────────
    gt_path = os.path.join(app.static_folder, med_img.ground_truth_path)
    gt_img  = Image.open(gt_path).convert('L')   # grayscale
    gw, gh  = gt_img.size

    pred_resized = cropped.resize((gw, gh), Image.LANCZOS)

    # Binarise: predicted = any pixel with alpha > 10
    pred_arr = np.array(pred_resized)
    pred_bin = (pred_arr[:, :, 3] > 10).astype(np.uint8)

    # Binarise ground truth: pixels brighter than 10 are liver
    gt_arr   = np.array(gt_img)
    gt_bin   = (gt_arr > 10).astype(np.uint8)

    # ── Dice score ────────────────────────────────────────────────────────────
    intersection = int((pred_bin & gt_bin).sum())
    denom        = int(pred_bin.sum() + gt_bin.sum())
    dice_score   = (2.0 * intersection / denom) if denom > 0 else 0.0
    dice_score   = round(dice_score, 4)

    # ── Save submitted mask to disk ───────────────────────────────────────────
    seg_dir = os.path.join(app.static_folder, 'segmentations')
    os.makedirs(seg_dir, exist_ok=True)
    ts       = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    mask_filename = f'u{current_user.id}_i{image_id}_{ts}.png'
    mask_full_path = os.path.join(seg_dir, mask_filename)
    pred_resized.save(mask_full_path)
    mask_rel_path = f'segmentations/{mask_filename}'

    # ── XP award: 50 base + up to 450 for dice score ─────────────────────────
    xp_awarded = int(50 + 450 * dice_score)

    # ── Persist segmentation record ───────────────────────────────────────────
    seg = Segmentation(
        user_id=current_user.id,
        image_id=image_id,
        dice_score=dice_score,
        xp_awarded=xp_awarded,
        status='validated',
        mask_path=mask_rel_path,
    )
    db.session.add(seg)

    # Update user stats
    current_user.total_segments += 1
    current_user.accuracy_sum   += dice_score
    current_user.xp             += xp_awarded
    db.session.commit()

    return jsonify({
        'ok': True,
        'dice_score': dice_score,
        'xp_awarded': xp_awarded,
        'accuracy_pct': current_user.accuracy_pct,
    })