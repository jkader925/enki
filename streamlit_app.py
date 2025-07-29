import streamlit as st
import litellm

# Supported models (OpenAI and Anthropic)
MODELS = [
    # OpenAI models
    "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
    # Anthropic models
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]

# App header
st.title("💬 Enki Chatbot")
st.write("Choose your model, enter your API key, and start chatting!")

# Model selector
selected_model = st.selectbox("Choose a model", MODELS)

# API key input
api_key = st.text_input("Enter your API key", type="password")

if not api_key:
    st.info("Please enter your API key to begin.", icon="🔐")
else:
    # Set LiteLLM config
    if selected_model.startswith("claude"):
        litellm.set_verbose = False
        litellm.api_base = "https://api.anthropic.com"  # Optional, LiteLLM usually handles this
        litellm.api_key = api_key
        provider = "anthropic"
    else:
        litellm.api_key = api_key
        provider = "openai"

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Prompt input
    if prompt := st.chat_input("Say something..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate model response
        with st.chat_message("assistant"):
            response_container = st.empty()
            collected_chunks = []

            try:
                stream = litellm.completion(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "") or delta.get("text", "")
                    collected_chunks.append(content)
                    response_container.markdown("".join(collected_chunks))

                final_response = "".join(collected_chunks)
                st.session_state.messages.append({"role": "assistant", "content": final_response})

            except Exception as e:
                st.error(f"Error: {e}")
