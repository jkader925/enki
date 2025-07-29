import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import Hasher

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.image('logo.png')

col1, col2 = st.columns(2)
with col1:
    st.metric('Streamlit Version', '1.43.1')
with col2:
    st.metric('Streamlit Authenticator Version', '0.4.2')

st.code(f"""
Credentials:

First name: {config['credentials']['usernames']['jsmith']['first_name']}
Last name: {config['credentials']['usernames']['jsmith']['last_name']}
Username: jsmith
Password: {'abc' if 'pp' not in config['credentials']['usernames']['jsmith'].keys() else config['credentials']['usernames']['jsmith']['pp']}

First name: {config['credentials']['usernames']['rbriggs']['first_name']}
Last name: {config['credentials']['usernames']['rbriggs']['last_name']}
Username: rbriggs
Password: {'def' if 'pp' not in config['credentials']['usernames']['rbriggs'].keys() else config['credentials']['usernames']['rbriggs']['pp']}
"""
)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Creating a login widget
try:
    authenticator.login()
except Exception as e:
    st.error(f"Login error: {e}")

if st.session_state["authentication_status"]:
    st.write('___')
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')    
    st.write('___')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

# Creating a new user registration widget
try:
    (email_of_registered_user,
     username_of_registered_user,
     name_of_registered_user) = authenticator.register_user()
    if email_of_registered_user:
        st.success('User registered successfully')
        # Update config file
        with open('config.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(f"Registration error: {e}")

# Creating an update user details widget
if st.session_state["authentication_status"]:
    try:
        if authenticator.update_user_details(st.session_state["username"]):
            st.success('Entries updated successfully')
            # Update config file
            with open('config.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(f"Update error: {e}")
