import streamlit as st
from litellm import completion
import base64
from streamlit.components.v1 import html

st.set_page_config(page_title="💬 Enki Chatbot", layout="wide")
st.title("Enki Workshop")

# ====================== VM Terminal Component ======================
xterm_html = """
<link rel="stylesheet" href="https://unpkg.com/xterm@5.3.0/css/xterm.css">
<script src="https://unpkg.com/xterm@5.3.0/lib/xterm.js"></script>
<script src="https://unpkg.com/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>

<div id="terminal" style="width:100%; height:400px; background:#000; padding:10px"></div>

<script>
const term = new Terminal();
const fitAddon = new FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();

// Mock terminal interaction for demo
term.write('Welcome to Enki VM Terminal\\r\\n$ ');
term.onData(data => {
    term.write(data);
    if (data === '\\r') {  // On Enter key
        term.write('\\r\\n$ Command executed\\r\\n$ ');
    }
});
</script>
"""

# ====================== Main App Layout ======================
tab1, tab2 = st.tabs(["💬 Chat", "🖥️ VM Terminal"])

with tab1:
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
    
    # API Key Input
    api_key = st.text_input(
        f"Enter {provider} API Key", 
        type="password",
        help=f"Get your key from {provider}'s website"
    )
    
    # Model selection
    selected_model = st.selectbox(
        "Choose model",
        [model for models in all_model_options[provider].values() for model in models]
    )
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        if not api_key:
            st.warning("Please enter your API key")
            st.stop()
            
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Call the LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = completion(
                        model=selected_model,
                        messages=[{"role": "user", "content": prompt}],
                        api_key=api_key,
                        stream=True
                    )
                    
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in response:
                        if hasattr(chunk, 'choices') and chunk.choices:
                            content = chunk.choices[0].delta.content
                            if content:
                                full_response += content
                                response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                    
                except Exception as e:
                    st.error(f"Error calling API: {str(e)}")

with tab2:
    st.header("Virtual Machine Terminal")
    html(xterm_html, height=450)
    st.info("This is a mock terminal. Connect to a real VM backend by modifying the JavaScript in the code.")
