import streamlit as st

# Define model categories
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
}

# Flatten the model list for selection display, preserving categories
model_display = []
for category, models in model_options.items():
    model_display.append(f"🔹 {category}")
    for model in models:
        model_display.append(f"  {model}")

# Handle selection
selected_display = st.selectbox("Choose model", model_display)

# Extract model name (remove leading bullets/spaces)
if selected_display.startswith("  "):
    selected_model = selected_display.strip()
else:
    selected_model = None
    st.warning("Please select a specific model, not just a category.")

# Optionally: display or use the model
if selected_model:
    st.success(f"Selected model: `{selected_model}`")
    # Use `selected_model` in your completion() call
