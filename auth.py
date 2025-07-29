# auth.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from settings import USERS_FILE, COOKIE_NAME, COOKIE_KEY

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE) as f:
            return yaml.load(f, Loader=SafeLoader)
    else:
        return {"usernames": {}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        yaml.dump(users, f)

def get_authenticator():
    users = load_users()
    return stauth.Authenticate(
        users,
        COOKIE_NAME,
        COOKIE_KEY,
        cookie_expiry_days=30
    )

def login():
    authenticator = get_authenticator()
    name, auth_status, username = authenticator.login("Login", location="main")
    return authenticator, name, auth_status, username

def logout(authenticator):
    authenticator.logout("Logout", location="sidebar")
