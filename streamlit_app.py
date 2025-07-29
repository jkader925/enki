import streamlit as st

# Set Streamlit page config
st.set_page_config(page_title="Enki Workshop", layout="centered")

# Sidebar for provider selection
st.sidebar.title("Settings")
provider = st.sidebar.selectbox("Select LLM Provider", ["OpenAI", "Anthropic", "Other"])

# Model categories: completion and vision
model_options = {
    "Completion Models": [
        # OpenAI
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini", "o3-mini", "o3",
        "o1-mini", "o1-preview", "gpt-4o-mini", "gpt-4o-mini-2024-07-18",
        "gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-turbo",
        "gpt-4-turbo-preview", "gpt-4-0125-preview", "gpt-4-1106-preview",
        "gpt-3.5-turbo-1106", "gpt-3.5-turbo", "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613",
        "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        # Anthropic
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
    ],
    "Vision Models": [
        # OpenAI
        "gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview",
        # Anthropic vision-capable models
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
    ]
}

# Flatten and indent model options for display
model_display = []
for category, models in model_options.items():
    model_display.append(f"🔹 {category}")
    for model in models:
        model_display.append(f"  {model}")

selected_display = st.selectbox("Choose a model", model_display)

# Clean up model selection
if selected_display.startswith("  "):
    selected_model = selected_display.strip()
else:
    selected_model = None
    st.warning("Please select a specific model, not just a category.")

# API Key input
api_key = st.text_input("Enter your API Key", type="password")

# Prompt input
prompt = st.text_area("Enter your prompt")

if st.button("Submit"):
    if not selected_model or not api_key or not prompt:
        st.error("Please fill in all fields before submitting.")
    else:
        st.success(f"Model: `{selected_model}`\nProvider: `{provider}`\nPrompt submitted!")
        # Placeholder: add actual API call logic here
