import streamlit as st
import streamlit_authenticator as stauth
from create_users import load_users, save_users, hash_password
from litellm import completion
import os

st.set_page_config(page_title="💬 Enki Chatbot with LiteLLM", layout="wide")

# Load users config
config = load_users()

st.title("💬 Enki Chatbot with LiteLLM")

if "register" not in st.session_state:
    st.session_state.register = False

if st.session_state.register:
    st.subheader("Register New User")
    new_username = st.text_input("Choose a username")
    new_name = st.text_input("Full name")
    new_email = st.text_input("Email address")
    new_password = st.text_input("Choose a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    
    if st.button("Register"):
        usernames = config["credentials"]["usernames"]
        if new_username in usernames:
            st.error("Username already exists.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif not new_username or not new_password:
            st.error("Please fill all fields.")
        else:
            hashed_pw = hash_password(new_password)
            usernames[new_username] = {
                "name": new_name,
                "email": new_email,
                "password": hashed_pw,
                "api_keys": {"openai": "", "anthropic": ""}
            }
            save_users(config)
            st.success("Registration successful! Please log in.")
            st.session_state.register = False
            st.experimental_rerun()
    
    if st.button("Back to Login"):
        st.session_state.register = False
        st.experimental_rerun()

else:
    # Login form
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    auth_status = authenticator.login("main")
    
    if auth_status is False:
        st.error("Username/password is incorrect")
    elif auth_status is None:
        st.warning("Please enter your username and password")
    else:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Logged in as {name}")

        # Derive username key (assuming usernames are lowercase keys)
        username = None
        for u, v in config["credentials"]["usernames"].items():
            if v.get("name") == name:
                username = u
                break
        
        if username is None:
            st.error("Could not find your user info in config!")
            st.stop()
        
        user_data = config["credentials"]["usernames"][username]

        # API key settings in sidebar
        st.sidebar.header("🔑 API Key Settings")
        for key_type in ["openai", "anthropic"]:
            current_key = user_data.get("api_keys", {}).get(key_type, "")
            new_key = st.sidebar.text_input(f"{key_type.capitalize()} API Key", value=current_key, type="password")
            if "api_keys" not in user_data:
                user_data["api_keys"] = {}
            user_data["api_keys"][key_type] = new_key
        
        if st.sidebar.button("Save API Keys"):
            save_users(config)
            st.sidebar.success("API keys saved.")

        # Chatbot UI below
        st.header("Chat with Enki")

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

        # Get API key from user data
        key_lookup = {
            "OpenAI": "openai",
            "Anthropic Claude": "anthropic",
        }
        api_key = user_data["api_keys"].get(key_lookup[provider], "")
        if not api_key:
            st.warning(f"No API key found for {provider}. Please enter your API key in the sidebar.")
            st.stop()

        # Initialize session state for messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display previous messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Handle user input
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            llm_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            # Set API key env var
            env_vars = {
                "OpenAI": "OPENAI_API_KEY",
                "Anthropic Claude": "ANTHROPIC_API_KEY",
            }
            os.environ[env_vars[provider]] = api_key

            # Call LiteLLM completion stream
            stream = completion(
                model=model,
                messages=llm_messages,
                stream=True,
                api_key=api_key,
                provider=provider.lower().replace(" ", ""),
            )

            with st.chat_message("assistant"):
                response_text = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response_text})

    if st.button("Register new user?"):
        st.session_state.register = True
        st.rerun()
