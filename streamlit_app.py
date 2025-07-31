import streamlit as st
from litellm import completion
from streamlit.components.v1 import html

st.set_page_config(page_title="💬 Enki Chatbot", layout="wide")
st.title("Enki Workshop")

# ====================== VM Terminal Component ======================
xterm_html = """
<link rel="stylesheet" href="https://unpkg.com/xterm@5.3.0/css/xterm.css">
<script src="https://unpkg.com/xterm@5.3.0/lib/xterm.js"></script>
<script src="https://unpkg.com/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>

<div id="terminal" style="width:100%; height:100%; background:#000; padding:10px"></div>

<script>
const term = new Terminal({
    fontSize: 14,
    theme: {
        background: '#111827',
        foreground: '#f3f4f6'
    }
});
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

# ====================== Split Screen Layout ======================
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.header("💬 AI Chat")
    
    # Chatbot UI
    provider = st.selectbox("LLM Provider", options=["OpenAI", "Anthropic Claude"], index=0)
    
    # Simplified model selection
    models = {
        "OpenAI": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "Anthropic Claude": ["claude-3-opus-20240229", "claude-3-haiku-20240307"]
    }
    
    selected_model = st.selectbox("Model", models[provider])
    api_key = st.text_input("API Key", type="password")

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Type your message..."):
        if not api_key:
            st.warning("Please enter your API key")
            st.stop()
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
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
                    st.error(f"Error: {str(e)}")

with col2:
    st.header("🖥️ VM Terminal")
    html(xterm_html, height=500)
    st.caption("""
    **Try these mock commands**:  
    `ls` - List files  
    `python --version` - Check Python  
    `clear` - Reset terminal  
    """)

# CSS to make the terminal fill available space
st.markdown("""
<style>
.st-emotion-cache-1v0mbdj {
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
}
.st-emotion-cache-1y4p8pa {
    padding: 1.5rem;
}
</style>
""", unsafe_allow_html=True)
