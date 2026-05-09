"""
Convert liver CT DICOM slices to PNG and copy ground-truth masks.

Source DCM:  med_data/raw/i{N:04d},0000b.dcm   (N = 0 .. 94)
Output PNG:  app/static/images/liver_ct_{N:03d}.png

Source mask: med_data/ground_mask/liver_GT_{N:03d}.png
Output mask: app/static/images/ground_truth/liver_GT_{N:03d}.png

Run from the repo root:
    python scripts/convert_dcm.py
"""
import os
import shutil
import sys

import numpy as np
import pydicom
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR   = os.path.join(REPO_ROOT, '..', 'med_data', 'raw')
MASK_DIR  = os.path.join(REPO_ROOT, '..', 'med_data', 'ground_mask')
OUT_IMG   = os.path.join(REPO_ROOT, 'app', 'static', 'images')
OUT_GT    = os.path.join(REPO_ROOT, 'app', 'static', 'images', 'ground_truth')

os.makedirs(OUT_IMG, exist_ok=True)
os.makedirs(OUT_GT,  exist_ok=True)

converted = skipped = 0
for n in range(95):
    dcm_name = f'i{n:04d},0000b.dcm'
    dcm_path = os.path.join(RAW_DIR, dcm_name)
    out_name = f'liver_ct_{n:03d}.png'
    out_path = os.path.join(OUT_IMG, out_name)

    if not os.path.exists(dcm_path):
        print(f'  MISSING {dcm_name}', file=sys.stderr)
        continue

    if os.path.exists(out_path):
        skipped += 1
        continue

    ds  = pydicom.dcmread(dcm_path)
    arr = ds.pixel_array.astype(np.float32)

    # Convert stored values to Hounsfield Units
    slope     = float(getattr(ds, 'RescaleSlope',     1))
    intercept = float(getattr(ds, 'RescaleIntercept', 0))
    hu = arr * slope + intercept

    # Standard abdominal window: WC=40, WW=400 → display range -160 to +240 HU
    wc, ww = 40.0, 400.0
    lo = wc - ww / 2   # -160 HU
    hi = wc + ww / 2   # +240 HU
    hu = np.clip(hu, lo, hi)
    arr_norm = (hu - lo) / (hi - lo) * 255.0

    Image.fromarray(arr_norm.astype(np.uint8)).save(out_path)
    converted += 1

print(f'Images  — converted: {converted}, already existed (skipped): {skipped}')

# Copy ground-truth masks
gt_converted = gt_skipped = 0
for n in range(95):
    src = os.path.join(MASK_DIR, f'liver_GT_{n:03d}.png')
    dst = os.path.join(OUT_GT,   f'liver_GT_{n:03d}.png')

    if not os.path.exists(src):
        print(f'  MISSING ground_mask/liver_GT_{n:03d}.png', file=sys.stderr)
        continue

    if os.path.exists(dst):
        gt_skipped += 1
        continue

    shutil.copy2(src, dst)
    gt_converted += 1

print(f'Masks   — copied: {gt_converted}, already existed (skipped): {gt_skipped}')
