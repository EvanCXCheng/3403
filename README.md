# MED-SEG-ALPHA: medical segmentation game

An online game where users compete to create the most accurate segmentations on medical images.

Medical students can sharpen their anatomy and medical imaging skills, while the general public can learn more about anatomy and medical segmentation through a fun and interactive experience.

Open the homepage, login, then click play now to have fun with our segmentation tool!
---

## Why This Matters

High‑performing players will complete segmentations on previously unlabelled medical data.  
These newly created annotations can then be used for:

- **Training or fine‑tuning** medical segmentation models (CNNs, transformers, etc.)
- **Weakly supervised learning**, since the labels are non‑clinical but still informative
- **Expanding datasets** for researchers who often lack labelled medical images
- **Potential model testing**, depending on annotation quality

This opens the door to more widely available labelled medical data for machine‑learning researchers.

![medSAM medical segmenation image](https://github.com/user-attachments/assets/ef29667f-dd5a-48b4-b8ae-dc462ec163b5)
*Source: Segment Anything in Medical Images 
https://doi.org/10.48550/arXiv.2304.12306*

## Students

 UWA ID | Name | Github Account Name |
| -------- | -------- | -------- |
| 24072654 | Evan Cheng | EvanCXCheng |
| 23775697 | Ethan Judge | judgee21 |
| 24491744 | Maaish Ahmed | MaaishAhmed |
| 24276561 | Mujtaba Al-Asadi | Mujtaba |

## Launch the Application

cd 3403  
pip install -r requirements.txt  
flask db upgrade  
python app/seed.py  
python Scripts/convert_dcm.py  
python Scripts/seed_liver.py  
flask run  

## Run Tests

### Selenium test only:
pytest tests/selenium/ -v

### Unit test only:
pytest tests/ --ignore=tests/selenium -v

### All tests:
pytest tests/ -v
