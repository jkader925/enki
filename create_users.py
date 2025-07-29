import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from pathlib import Path
import bcrypt

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
    # Method 1: Try the direct function approach
    try:
        return stauth.Hasher([password]).generate()[0]
    except TypeError:
        # Method 2: Fall back to bcrypt directly
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
