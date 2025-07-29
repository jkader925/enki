import streamlit as st
from litellm import completion

# ---- Provider dropdown ----
PROVIDERS = ["OpenAI", "Anthropic"]
provider = st.selectbox("Select LLM Provider:", PROVIDERS)

# ---- Define models by provider and category ----
OPENAI_MODELS = {
    "Chat Completion Models": [
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
    ],
    "Vision Models": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-vision-preview",
    ]
}

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
]

# ---- Build model selection UI ----
if provider == "OpenAI":
    MODEL_OPTIONS = []
    MODEL_MAP = {}
    for category, models in OPENAI_MODELS.items():
        for model in models:
            label = f"{category} → {model}"
            MODEL_OPTIONS.append(label)
            MODEL_MAP[label] = model
    model_label = st.selectbox("Choose OpenAI model:", MODEL_OPTIONS)
    model = MODEL_MAP[model_label]
elif provider == "Anthropic":
    model = st.selectbox("Choose Anthropic model:", ANTHROPIC_MODELS)
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

    # You can pass keys via kwargs or environment
    with st.spinner("Waiting for response..."):
        try:
            messages = [{"role": "user", "content": prompt}]
            response = completion(model=model, messages=messages, api_key=api_key)
            content = response["choices"][0]["message"]["content"]
            st.success("Response:")
            st.markdown(content)
        except Exception as e:
            st.error(f"Error: {e}")
