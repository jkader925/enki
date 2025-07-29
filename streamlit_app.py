import streamlit as st
from litellm import completion
from auth import load_authenticator, save_user_config
import os

# Load login system
authenticator, config = load_authenticator()
name, auth_status, username = authenticator.login(location="main", form_name="Login")


if auth_status is False:
    st.error("Invalid username or password")
    st.stop()
elif auth_status is None:
    st.warning("Please enter your username and password")
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"Logged in as {name}")

# API key storage section
st.sidebar.header("🔑 API Key Settings")
user_data = config["credentials"]["usernames"][username]

for key_type in ["openai", "anthropic"]:
    current_key = user_data.get("api_keys", {}).get(key_type, "")
    new_key = st.sidebar.text_input(f"{key_type.capitalize()} API Key", value=current_key, type="password")
    if "api_keys" not in user_data:
        user_data["api_keys"] = {}
    user_data["api_keys"][key_type] = new_key

# Save updated config
save_user_config(config)

st.title("💬 Enki Chatbot with LiteLLM")
st.write("Chat with LLMs using your stored API key.")

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
    model = None
    st.warning("Please select a specific model (not just a category).")
    st.stop()

# API key input
#api_key_label = f"{provider} API Key"
#api_key = st.text_input(api_key_label, type="password")
#if not api_key:
#    st.info(f"Please enter your {provider} API key to continue.", icon="🗝️")
#    st.stop()

# Get key from user settings
key_lookup = {
    "OpenAI": "openai",
    "Anthropic Claude": "anthropic",
}
api_key = user_data["api_keys"].get(key_lookup[provider], "")
if not api_key:
    st.warning("No API key found in settings.")
    st.stop()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    llm_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Set API key in environment
    env_vars = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic Claude": "ANTHROPIC_API_KEY",
    }
    os.environ[env_vars[provider]] = api_key

    # Stream from LiteLLM
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
