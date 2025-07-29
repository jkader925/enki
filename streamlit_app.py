import streamlit as st
from litellm import completion

# ---- Provider dropdown ----
PROVIDERS = ["OpenAI", "Anthropic"]
provider = st.selectbox("Select LLM Provider:", PROVIDERS)

# ---- Define models by provider and category ----
OPENAI_COMPLETION_MODELS = [
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "o4-mini",
    "o3-mini",
    "o3",
    "o1-mini",
    "o1-preview",
    "gpt-4o-mini",
    "gpt-4o-mini-2024-07-18",
    "gpt-4o",
    "gpt-4o-2024-08-06",
    "gpt-4o-2024-05-13",
    "gpt-4-turbo",
    "gpt-4-turbo-preview",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-4-32k-0613",
]

OPENAI_VISION_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4-vision-preview",
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
]

# ---- Model selection ----
if provider == "OpenAI":
    st.markdown("### Completion Models")
    model = st.selectbox("Select a model:", OPENAI_COMPLETION_MODELS, key="completion_model")
    
    st.markdown("### Vision Models")
    vision_model = st.selectbox("Select a vision model:", OPENAI_VISION_MODELS, key="vision_model")

    # Pick whichever was changed most recently (you can customize this logic)
    model = vision_model if st.session_state["vision_model"] != OPENAI_VISION_MODELS[0] else model

elif provider == "Anthropic":
    st.markdown("### Anthropic Models")
    model = st.selectbox("Select a model:", ANTHROPIC_MODELS)
else:
    model = st.text_input("Enter model name manually")

# ---- API Key Input ----
api_key = st.text_input("Enter your API Key:", type="password")

# ---- Prompt input ----
prompt = st.text_area("Enter your prompt:")

# ---- Submit and respond ----
if st.button("Submit") and prompt.strip() and api_key.strip():
    st.write(f"**Provider:** `{provider}`")
    st.write(f"**Model:** `{model}`")

    try:
        with st.spinner("Waiting for response..."):
            messages = [{"role": "user", "content": prompt}]
            response = completion(model=model, messages=messages, api_key=api_key)
            content = response["choices"][0]["message"]["content"]
            st.success("Response:")
            st.markdown(content)
    except Exception as e:
        st.error(f"Error: {e}")
