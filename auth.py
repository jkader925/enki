# auth.py
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

USERS_FILE = Path("users.yaml")

def load_authenticator():
    with open(USERS_FILE, "r") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator, config

def save_user_config(config):
    with open(USERS_FILE, "w") as file:
        yaml.dump(config, file)
