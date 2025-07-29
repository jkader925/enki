import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import Hasher
from litellm import completion
import os

# --- Configuration Setup ---
st.set_page_config(page_title="💬 Enki Chatbot with LiteLLM", layout="wide")

# Load config file
@st.cache_resource
def load_config():
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            return yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Create default config if file doesn't exist
        default_config = {
            'credentials': {
                'usernames': {
                    'demo': {
                        'email': 'demo@enki.com',
                        'name': 'Demo User',
                        'password': Hasher(['demo123']).generate()[0],
                        'api_keys': {'openai': '', 'anthropic': ''}
                    }
                }
            },
            'cookie': {
                'name': 'enki_auth',
                'key': 'your_cookie_key_here',
                'expiry_days': 30
            }
        }
        with open('config.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(default_config, file, default_flow_style=False)
        return default_config

config = load_config()

# --- Authentication Setup ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Main App Structure ---
def main():
    # Authentication widget
    authenticator.login('Login', 'main')
    
    if st.session_state.get("authentication_status"):
        show_authenticated_interface()
    elif st.session_state.get("authentication_status") is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get("authentication_status") is None:
        show_guest_interface()

def show_authenticated_interface():
    # User info and logout
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Logged in as {st.session_state['name']}")
    
    # API Key Management
    manage_api_keys()
    
    # Chat Interface
    show_chat_interface()

def show_guest_interface():
    st.title("💬 Enki Chatbot with LiteLLM")
    st.warning('Please login to access the chatbot')
    
    # Registration Section
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            # Update config file
            with open('config.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)

def manage_api_keys():
    """Sidebar for API key management"""
    st.sidebar.header("🔑 API Key Settings")
    username = st.session_state['username']
    user_data = config['credentials']['usernames'][username]
    
    if 'api_keys' not in user_data:
        user_data['api_keys'] = {}
    
    for key_type in ["openai", "anthropic"]:
        current_key = user_data['api_keys'].get(key_type, "")
        new_key = st.sidebar.text_input(
            f"{key_type.capitalize()} API Key",
            value=current_key,
            type="password"
        )
        user_data['api_keys'][key_type] = new_key
    
    if st.sidebar.button("Save API Keys"):
        with open('config.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False)
        st.sidebar.success("API keys saved!")

def show_chat_interface():
    """Main chatbot interface"""
    st.header("Chat with Enki")
    
    # Model Selection
    provider = st.selectbox(
        "Choose LLM Provider",
        options=["OpenAI", "Anthropic Claude"],
        index=0
    )
    
    # Model options
    model_options = {
        "OpenAI": [
            "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo",
            "gpt-4", "gpt-4-vision-preview"
        ],
        "Anthropic Claude": [
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ]
    }
    
    model = st.selectbox(
        "Choose model",
        options=model_options[provider]
    )
    
    # Get API key
    username = st.session_state['username']
    api_key = config['credentials']['usernames'][username]['api_keys'].get(
        "openai" if provider == "OpenAI" else "anthropic", ""
    )
    
    if not api_key:
        st.warning(f"Please enter your {provider} API key in the sidebar")
        st.stop()
    
    # Chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Handle new input
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Call LLM
        with st.chat_message("assistant"):
            response = completion(
                model=model,
                messages=[{"role": m["role"], "content": m["content"]} 
                         for m in st.session_state.messages],
                stream=True,
                api_key=api_key
            )
            response_text = st.write_stream(response)
        
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

if __name__ == "__main__":
    main()
