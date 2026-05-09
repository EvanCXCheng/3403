"""
Seed 95 liver CT MedicalImage rows (series_id=1).
Safe to re-run — skips if any series_id=1 rows already exist.

Run from the repo root:
    python scripts/seed_liver.py
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app, db
from app.models import MedicalImage


def seed_liver():
    with app.app_context():
        if MedicalImage.query.filter_by(series_id=1).first():
            print('Liver CT series already seeded — skipping.')
            return

        rows = []
        for n in range(95):
            rows.append(MedicalImage(
                filename=f'images/liver_ct_{n:03d}.png',
                modality='CT',
                organ='Liver',
                difficulty=2,
                description=(
                    'Contrast-enhanced abdominal CT slice showing hepatic parenchyma. '
                    'Part of a 95-slice liver CT series.'
                ),
                objective='Segment the liver parenchyma boundary from the surrounding tissue.',
                series_id=1,
                ground_truth_path=f'images/ground_truth/liver_GT_{n:03d}.png',
            ))

        db.session.add_all(rows)
        db.session.commit()
        print(f'Seeded {len(rows)} liver CT MedicalImage rows (series_id=1).')


if __name__ == '__main__':
    seed_liver()
