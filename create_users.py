# create_users.py
import streamlit_authenticator as stauth
from auth import load_users, save_users

def add_user(username, name, password):
    users = load_users()
    if "usernames" not in users:
        users["usernames"] = {}

    if username in users["usernames"]:
        raise ValueError(f"User '{username}' already exists.")

    hashed_pw = stauth.Hasher([password]).generate()[0]
    users["usernames"][username] = {
        "name": name,
        "password": hashed_pw
    }

    save_users(users)
    print(f"✅ User '{username}' added.")

if __name__ == "__main__":
    # Example usage — run this script from the terminal to add users
    import getpass
    username = input("Username: ")
    name = input("Full name: ")
    password = getpass.getpass("Password: ")
    add_user(username, name, password)
