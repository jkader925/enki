import streamlit as st
from litellm import completion
import os

st.title("💬 Enki Chatbot with LiteLLM")

st.write(
    "Chat with LLMs using your API key. Select your model and provider below."
)

# Model and provider selection
provider = st.selectbox(
    "Choose LLM Provider",
    options=["OpenAI", "Anthropic Claude"],
    index=0,
)

# Model options depending on provider
model_options = {
    "OpenAI Chat Completion Models": [
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini", "o3-mini", "o3",
        "o1-mini", "o1-preview", "gpt-4o-mini", "gpt-4o-mini-2024-07-18",
        "gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-turbo",
        "gpt-4-turbo-preview", "gpt-4-0125-preview", "gpt-4-1106-preview",
        "gpt-3.5-turbo-1106", "gpt-3.5-turbo", "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613",
        "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314",
        "gpt-4-32k-0613"
    ],
    "OpenAI Vision Models": [
        "gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview"
    ]
    "Anthropic Claude": [
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ],
}

model = st.selectbox("Choose model", options=model_options[provider])

# API key input
api_key_label = f"{provider} API Key"
api_key = st.text_input(api_key_label, type="password")
if not api_key:
    st.info(f"Please enter your {provider} API key to continue.", icon="🗝️")
    st.stop()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):

    # Append user message and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for LiteLLM
    llm_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Select correct API key environment variable key for LiteLLM backend
    env_vars = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic Claude": "ANTHROPIC_API_KEY",
    }
    os.environ[env_vars[provider]] = api_key

    # Call LiteLLM completion with streaming
    stream = completion(
        model=model,
        messages=llm_messages,
        stream=True,
        api_key=api_key,
        provider=provider.lower().replace(" ", ""),
    )

    # Stream response into chat
    with st.chat_message("assistant"):
        response_text = st.write_stream(stream)

    # Append assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response_text})
