import yaml
import streamlit as st
from litellm import completion
import os
import base64
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import Hasher
from streamlit.components.v1 import html

st.set_page_config(page_title="💬 Enki Chatbot", layout="wide")
st.title("Enki Workshop")


with st.sidebar:
    st.write("---")
    st.header("🔑 API Key Management")
    
    
    # API Key Input Fields
    openai_key = st.text_input(
        "OpenAI API Key", 
        value="", 
        type="password",
        help="Get your key from https://platform.openai.com/account/api-keys"
    )
    
    anthropic_key = st.text_input(
        "Anthropic API Key", 
        value="", 
        type="password",
        help="Get your key from https://console.anthropic.com/settings/keys"
    )
    
    # Save keys when user clicks the button
    if st.button("Save API Keys"):
        config['credentials']['usernames'][username]['api_keys'] = {
            'openai': openai_key,
            'anthropic': anthropic_key
        }
        with open('config.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False)
        st.success("API keys saved successfully!")

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

# Get the appropriate API key
api_key = config['credentials']['usernames'][username]['api_keys'].get(
    'openai' if provider == "OpenAI" else 'anthropic', ""
)

if not api_key:
    st.warning(f"Please enter your {provider} API key in the sidebar")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if selected model is a vision model
is_vision_model = (provider == "OpenAI" and 
                  any(vm in model for vm in ["gpt-4o", "gpt-4-turbo", "gpt-4-vision"]))

# Image upload for vision models
uploaded_image = None
if is_vision_model:
    st.subheader("Upload Image")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_image = st.file_uploader(
            "Drag and drop or click to upload",
            type=["jpg", "jpeg", "png"],
            key="image_upload"
        )
    with col2:
        if uploaded_image:
            st.image(uploaded_image, width=200)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(message["image"], width=300)
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    message_content = {"role": "user", "content": prompt}
    if uploaded_image:
        message_content["image"] = uploaded_image.getvalue()
    st.session_state.messages.append(message_content)
    
    # Display user message
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image.getvalue(), width=300)
        st.markdown(prompt)
    
    # Prepare messages for API
    messages_for_api = []
    for msg in st.session_state.messages:
        if is_vision_model and msg.get("image"):
            # Only include image processing for vision models when image exists
            messages_for_api.append({
                "role": msg["role"],
                "content": [
                    {"type": "text", "text": msg["content"]},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(msg['image']).decode('utf-8')}"
                        }
                    }
                ]
            })
        else:
            # Regular text message format
            messages_for_api.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Call the LLM
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = completion(
                    model=model,
                    messages=messages_for_api,
                    api_key=api_key,
                    stream=True
                )
                
                # Create a placeholder for the streaming response
                response_placeholder = st.empty()
                full_response = ""
                
                # Process each chunk in the stream
                for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices:
                        content = chunk.choices[0].delta.content
                        if content:
                            full_response += content
                            response_placeholder.markdown(full_response + "▌")
                
                # Finalize the response display
                response_placeholder.markdown(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                
            except Exception as e:
                st.error(f"Error calling {provider} API: {str(e)}")
