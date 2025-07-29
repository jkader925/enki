import yaml
import streamlit as st
from litellm import completion
import os
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import Hasher

st.set_page_config(page_title="💬 Enki Chatbot with LiteLLM", layout="wide")
st.title("💬 Enki Chatbot with LiteLLM")

# Initialize session state variables
if 'auth_states' not in st.session_state:
    st.session_state.auth_states = {
        'show_register': False,
        'registration_complete': False,
        'force_rerun': False
    }

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Handle forced rerun if needed
if st.session_state.auth_states['force_rerun']:
    st.session_state.auth_states['force_rerun'] = False
    st.rerun()

# Show either login or registration form based on state
if not st.session_state.get("authentication_status"):
    if not st.session_state.auth_states['show_register']:
        # Show login form
        try:
            authenticator.login()
            
            # Only show register button if not authenticated
            if not st.session_state.get("authentication_status"):
                if st.button("Register New User"):
                    st.session_state.auth_states['show_register'] = True
                    st.session_state.auth_states['force_rerun'] = True
                    
        except Exception as e:
            st.error(f"Login error: {e}")
            
    else:
        # Show registration form
        try:
            st.write("")  # Spacer
            
            # Use the authenticator's registration form
            register_success = False
            try:
                if authenticator.register_user():
                    register_success = True
            except Exception as e:
                st.error(f"Registration error: {e}")
            
            if register_success:
                st.session_state.auth_states['show_register'] = False
                st.session_state.auth_states['registration_complete'] = True
                with open('config.yaml', 'w', encoding='utf-8') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('User registered successfully! Please login.')
                st.session_state.auth_states['force_rerun'] = True
            
            # Back button
            if st.button("Back to Login"):
                st.session_state.auth_states['show_register'] = False
                st.session_state.auth_states['force_rerun'] = True
                
        except Exception as e:
            st.error(f"Error: {e}")


# After login content
if st.session_state.get("authentication_status"):
    st.write(f'Welcome *{st.session_state["name"]}*')  
    authenticator.logout("Logout", "sidebar")
    
    # Chatbot UI
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
    
    # Build and display model selection
    model_display = []
    for category, models in all_model_options[provider].items():
        model_display.append(f"🔹 {category}")
        for model in models:
            model_display.append(f"  {model}")
    
    selected_display = st.selectbox("Choose model", model_display)
    
    if selected_display.startswith("  "):
        model = selected_display.strip()
    else:
        st.warning("Please select a specific model (not just a category).")
        st.stop()

elif st.session_state.get("authentication_status") is False:
    st.error('Username/password is incorrect')
elif st.session_state.get("authentication_status") is None:
    if not st.session_state.auth_states['show_register']:
        st.warning('Please enter your username and password')

# Save config file after any changes
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
