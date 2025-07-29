# user_utils.py
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from pathlib import Path

USERS_FILE = Path("users.yaml")

def load_users():
    if not USERS_FILE.exists():
        return {
            "credentials": {"usernames": {}},
            "cookie": {"expiry_days": 30, "key": "enki_cookie_secret", "name": "enki_auth"},
        }
    with open(USERS_FILE, "r") as f:
        return yaml.load(f, Loader=SafeLoader)

def save_users(config):
    with open(USERS_FILE, "w") as f:
        yaml.dump(config, f)

def hash_password(password):
    # The correct way to hash passwords in current versions of streamlit-authenticator
    return stauth.Hasher([password]).generate()[0]
