import streamlit as st
from litellm import completion

# --- Define model categories and models ---
MODEL_CATEGORIES = {
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

# --- Flatten all models for st.selectbox, prepending category ---
MODEL_OPTIONS = []
MODEL_MAP = {}

for category, models in MODEL_CATEGORIES.items():
    for model in models:
        label = f"{category} → {model}"
        MODEL_OPTIONS.append(label)
        MODEL_MAP[label] = model

# --- Streamlit UI ---
st.title("Enki 3D Chat Interface")

selected_label = st.selectbox("Choose a model:", MODEL_OPTIONS)
selected_model = MODEL_MAP[selected_label]

st.markdown(f"**Selected model:** `{selected_model}`")

user_input = st.text_area("Enter your prompt:")

if st.button("Submit") and user_input.strip():
    with st.spinner("Generating response..."):
        messages = [{"role": "user", "content": user_input}]
        try:
            response = completion(model=selected_model, messages=messages)
            st.success("Response received!")
            st.markdown(f"**Assistant:** {response['choices'][0]['message']['content']}")
        except Exception as e:
            st.error(f"Error: {e}")
