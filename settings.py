# settings.py
import streamlit as st
from auth import load_users, save_users

def api_key_settings(username):
    st.header("Settings")
    users = load_users()

    user_api_key = users["usernames"].get(username, {}).get("api_key", "")
    new_api_key = st.text_input("Enter your API key", value=user_api_key, type="password")
    if st.button("Save API key"):
        if username not in users["usernames"]:
            users["usernames"][username] = {}
        users["usernames"][username]["api_key"] = new_api_key
        save_users(users)
        st.success("API key saved!")
