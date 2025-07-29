import streamlit_authenticator as stauth
import yaml

passwords = stauth.Hasher(["your_password_here"]).generate()
config = {
    "credentials": {
        "usernames": {
            "your_username": {
                "name": "Your Name",
                "email": "you@example.com",
                "password": passwords[0],
                "api_keys": {"openai": "", "anthropic": ""}
            }
        }
    },
    "cookie": {"expiry_days": 30, "key": "somekey", "name": "enki_auth"},
    "preauthorized": {"emails": ["you@example.com"]}
}

with open("users.yaml", "w") as f:
    yaml.dump(config, f)
