from flask import render_template, redirect, url_for
from app import app

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


@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/leaderboard')
def leaderboard():
    players = [
        {
            "username": "Neuro_Elite",
            "xp": "42,980",
            "accuracy": "99.8%",
            "cases_solved": "1,204",
            "trend": "trending_up",
            "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuB1_llpmTESCnFQd_G9uziWLEMSsLSWU8y9rR-3DsLzvaNzR_fk8GVQaGeN2n90nLnsaetU5qngIwMD_t4rYBkZG2o66HpPk8Y0vAwiawxSOHe93qXPekZB0ZVBBjiTiiNbvvSGZQjDrUS1tuMQ3ylRI7yso0P4tbw-y1iFyMEyEYrEQmrOnMPfkbIldpyOwKAe7CQvgb95jYN2mo6dBWpzt2pZwnoTKvBJUWNCOWOqUwAPyeUtQQWT3IP3oL-OrRe-SW53kJo1UGg"
        },
        {
            "username": "PulseVector",
            "xp": "38,120",
            "accuracy": "99.4%",
            "cases_solved": "988",
            "trend": "trending_up",
            "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuDY7yKl1duyvszNZtUDCgcDxRiNojZgn0MBlff_a8lhIQoIG-E8ToLLQFRZBWgAO4zZdQ1xJEoL8ThP-sEQ5HeaosHCKZIWCowY3pRaycX7FgSjJ2jE07NRzdkYoZUBjZf2j3BCRG3zceOOADFPs-3S0ceunq45804sNbuh9IhKzOx3hjOZHxw-zqsrRiSIc9yPP0_YYVSLPjAvlI_E4YwRrdV5Sf-DsYIz8fPSEh23US4Efz-0CQldCnf8Ax9727Hu2oZfUsc5bU0"
        },
        {
            "username": "Synapse_RX",
            "xp": "35,440",
            "accuracy": "98.9%",
            "cases_solved": "842",
            "trend": "remove",
            "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuBf0Kd4d0Yx4fj35Q-up0T2g5rzBiGboIg_EQpOWCmlHlWPEQICEbWb9khNg-Ig_bOdmWcb56sd7aCYP8FzKwX33RWujYI0LCfUO5Diow2k9Y12Hqhy9Y-FaF2FeMm6OE9e0qNiF1OB1joGZAcD3DfO3qF_w1d-RipclhqsLVcy7Znu5Rf1jvOdyQKG5lURYVBngJvFGOQnu80fMtJbEbhKSFM6wDMacBUHihkRjD12iPiyMmESsbwIXkFsrbgYRLHmc1N2nXpZsRg"
        },
        {
            "username": "BioHacker_01",
            "xp": "29,800",
            "accuracy": "97.2%",
            "cases_solved": "715",
            "trend": "trending_up",
            "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuA4ix1-0Ens-NF4wZXyrmLDeYHDiq3C_A6kL9BxGDf1YPKZZcAbxD5NP_X2jx48vAMzyeJqn1IFm2n5Oa8FhBHZAqUzyZ-0o9EHG_378qIn7EmtV-xPqjKpJyVxQtgrzJqwSSVnJ1ehDVW9wvXJ5xece7kCcz--_5_dUywRR2GaX4cILvopBYuY4DKO36oh9ijDwxJZMSGNpDbqwXIOUTQwTtGExLOhba9QMfwx3RhubBUmuUJklOf_ETyya-pFfcFcyF0jBu3oVdM"
        },
        {
            "username": "CortexMapper",
            "xp": "27,550",
            "accuracy": "96.8%",
            "cases_solved": "640",
            "trend": "trending_down",
            "avatar": "https://lh3.googleusercontent.com/aida-public/AB6AXuCmWs-1nAfLolBD4yKV5i3newSjp3xoaWDwGjMYqfSihpBs7XBzcpvN1Ep-rC-OpGkQRvq_a-orYp1sgAhd8Kr_SVm4tUVDLhrouIUCaXy81G_wrWp9YQYOS5tQ5REX4zrfl3yGqE4l7-MiUpuTE0T_jDg11kPTtajrpI6OMIzdUDoZgeis1F_25U8SIkx4QQJfFvDdiiX7353SkW3dQdXM0qHG2MJmWoCWyFhLAXF0szcC7PCbNPKQpSq_pi6vYVadbL6B1A5oMQs"
        }
    ]

    return render_template('leaderboard.html', players=players)


@app.route('/profile')
def profile_default():
    return redirect(url_for('profile', username='elara'))


@app.route('/profile/<username>')
def profile(username):
    user = users.get(username)

    if user is None:
        return "User not found", 404

    return render_template('profile.html', user=user)


@app.route('/segmentation-tool')
def segmentation_tool():
    return render_template('segmentation_tool.html')


@app.route('/login')
def login():
    return render_template('login.html')