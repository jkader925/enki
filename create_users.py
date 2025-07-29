import streamlit_authenticator as stauth
import yaml

usernames = ["jdoe", "asmith"]
names = ["John Doe", "Alice Smith"]
passwords = ["hunter2", "secret123"]

hashed_passwords = stauth.Hasher(passwords).generate()

users_dict = {
    "usernames": {
        uname: {
            "name": name,
            "password": pw,
        }
        for uname, name, pw in zip(usernames, names, hashed_passwords)
    }
}

with open("users.yaml", "w") as f:
    yaml.dump(users_dict, f)
