import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

USERS_FILE = Path("users.yaml")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE) as f:
            data = yaml.load(f, Loader=SafeLoader)
            # Ensure correct structure
            if not data or "usernames" not in data:
                return {"usernames": {}}
            return data
    else:
        # Initialize empty structure
        return {"usernames": {}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        yaml.dump(users, f)

def get_authenticator():
    users = load_users()
    # stauth expects credentials under 'usernames' key
    credentials = users  # This should already have 'usernames'
    return stauth.Authenticate(
        credentials,
        "enki_chat_app",
        "abcdef",  # your secret key here
        cookie_expiry_days=30,
    )
def hash_passwords(password_list):
    """Returns a list of bcrypt-hashed passwords from a list of plaintext ones."""
    hasher = stauth.Hasher(password_list)
    return hasher.generate()
    
def login():
    authenticator = get_authenticator()
    # Use 'main' or 'sidebar' location for now, to avoid the unrendered error
    name, auth_status, username = authenticator.login("Login", "main")
    return authenticator, name, auth_status, username

def logout(authenticator):
    authenticator.logout("Logout", "sidebar")
