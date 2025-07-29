import yaml
import streamlit as st
from litellm import completion
import os
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)



st.set_page_config(page_title="💬 Enki Chatbot with LiteLLM", layout="wide")
st.title("💬 Enki Chatbot with LiteLLM")





# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

#st.image('logo.png')


#col1, col2 = st.columns(2)
#with col1:
#  st.metric('Streamlit Version', '1.43.1')
#with col2:
#  st.metric('Streamlit Authenticator Version', '0.4.2')




# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# authenticator = stauth.Authenticate(
#     '../config.yaml'
# )

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*')  
    
    # Select provider
    provider = st.selectbox("Choose LLM Provider", options=["OpenAI", "Anthropic Claude"], index=0)
    
    # Define model options grouped by category
    all_model_options = {
        "OpenAI": {
            "Chat Completion Models": [
                "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini", "o3-mini", "o3",
                "o1-mini", "o1-preview", "gpt-4o-mini", "gpt-4o-mini-2024-07-18",
                "gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-turbo",
                "gpt-4-turbo-preview", "gpt-4-0125-preview", "gpt-4-1106-preview",
                "gpt-3.5-turbo-1106", "gpt-3.5-turbo", "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613",
                "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314",
                "gpt-4-32k-0613"
            ],
            "Vision Models": [
                "gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview"
            ]
        },
        "Anthropic Claude": {
            "Claude Models": [
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307",
            ]
        }
    }
    
    # Build a flattened list with grouping
    model_display = []
    for category, models in all_model_options[provider].items():
        model_display.append(f"🔹 {category}")
        for model in models:
            model_display.append(f"  {model}")
    
    # Model selection
    selected_display = st.selectbox("Choose model", model_display)
    
    # Extract actual model name
    if selected_display.startswith("  "):
        model = selected_display.strip()
    else:
        st.warning("Please select a specific model (not just a category).")
        st.stop()
    authenticator.logout()

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')



#st.subheader('Guest login')

# Creating a guest login button

#try:
#    authenticator.experimental_guest_login('Login with Google', provider='google',
#                                            oauth2=st.secrets["oauth2"])
#    authenticator.experimental_guest_login('Login with Microsoft', provider='microsoft',
#                                            oauth2=st.secrets["oauth2"])
#except LoginError as e:
#    st.error(e)


# Creating a password reset widget
#if st.session_state["authentication_status"]:
#    try:
#        if authenticator.reset_password(st.session_state["username"]):
#            st.success('Password modified successfully')
#            config['credentials']['usernames'][username_of_forgotten_password]['pp'] = new_random_password
#    except ResetError as e:
#        st.error(e)
#    except CredentialsError as e:
#        st.error(e)
#    st.write('_If you use the password reset widget please revert the password to what it was before once you are done._')

# Creating a new user registration widget
try:
    (email_of_registered_user,
     username_of_registered_user,
     name_of_registered_user) = authenticator.register_user()
    if email_of_registered_user:
        st.success('User registered successfully')
except RegisterError as e:
    st.error(e)

# Creating a forgot password widget
#try:
#    (username_of_forgotten_password,
#     email_of_forgotten_password,
#     new_random_password) = authenticator.forgot_password()
#    if username_of_forgotten_password:
#        st.success(f"New password **'{new_random_password}'** to be sent to user securely")
#        config['credentials']['usernames'][username_of_forgotten_password]['pp'] = new_random_password
#        # Random password to be transferred to the user securely
#    elif not username_of_forgotten_password:
#        st.error('Username not found')
#except ForgotError as e:
#    st.error(e)

# Creating a forgot username widget
#try:
#    (username_of_forgotten_username,
#     email_of_forgotten_username) = authenticator.forgot_username()
#    if username_of_forgotten_username:
#        st.success(f"Username **'{username_of_forgotten_username}'** to be sent to user securely")
#        # Username to be transferred to the user securely
#    elif not username_of_forgotten_username:
#        st.error('Email not found')
#except ForgotError as e:
#    st.error(e)

# Creating an update user details widget
#if st.session_state["authentication_status"]:
#    try:
#        if authenticator.update_user_details(st.session_state["username"]):
#            st.success('Entries updated successfully')
#    except UpdateError as e:
#        st.error(e)

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
