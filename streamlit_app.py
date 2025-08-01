import streamlit as st
from litellm import completion
from streamlit.components.v1 import html
import json


def noVNC_viewer(vnc_host="localhost", vnc_port=5901, password=None):
    """Embed noVNC viewer in Streamlit"""
    return f"""
<div style="width:100%; height:65vh;">
    <iframe src="https://novnc.com/noVNC/vnc.html?host={vnc_host}&port={vnc_port}&autoconnect=true&password={password or ''}"
            style="width:100%; height:100%; border:1px solid #ccc; border-radius:8px;"
            allowfullscreen>
    </iframe>
</div>
"""
st.set_page_config(page_title="💬 Enki Chatbot", layout="wide")
st.title("Enki Workshop")

# ====================== Configuration ======================
if 'vm_connected' not in st.session_state:
    st.session_state.vm_connected = False

# ====================== VM Terminal Component ======================
def get_vm_terminal_html(vm_host="localhost", vm_port=7681):
    return f"""
<link rel="stylesheet" href="https://unpkg.com/xterm@5.3.0/css/xterm.css">
<script src="https://unpkg.com/xterm@5.3.0/lib/xterm.js"></script>
<script src="https://unpkg.com/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@xterm/addon-webgl@0.15.0/lib/xterm-addon-webgl.min.js"></script>

<style>
.terminal-container {{
    width: 100%;
    height: 65vh;  /* Fixed viewport height */
    background: #000;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
}}
</style>

<div class="terminal-container">
    <div id="terminal" style="width:100%; height:100%;"></div>
</div>

<script>
const term = new Terminal({{
    fontSize: 14,
    theme: {{
        background: '#111827',
        foreground: '#f3f4f6'
    }},
    allowProposedApi: true
}});

const fitAddon = new FitAddon();
const webglAddon = new WebglAddon();
term.loadAddon(fitAddon);
term.loadAddon(webglAddon);

term.open(document.getElementById('terminal'));
fitAddon.fit();

// WebSocket connection
const socket = new WebSocket('ws://{vm_host}:{vm_port}');

socket.onopen = () => {{
    term.write('\\x1b[32mConnected to VM\\x1b[0m\\r\\n$ ');
    window.parent.postMessage({{type: 'vm_status', connected: true}}, '*');
}};

socket.onclose = () => {{
    term.write('\\x1b[31mDisconnected from VM\\x1b[0m\\r\\n');
    window.parent.postMessage({{type: 'vm_status', connected: false}}, '*');
}};

socket.onerror = (error) => {{
    term.write(`\\x1b[31mConnection error: ${{error.message}}\\x1b[0m\\r\\n`);
}};

socket.onmessage = (event) => {{
    term.write(event.data);
}};

term.onData((data) => {{
    socket.send(data);
}});

// Handle resize
window.addEventListener('resize', () => {{
    fitAddon.fit();
}});
</script>
"""

# ====================== Split Screen Layout ======================
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.header("💬 AI Chat")
    
    # Chatbot UI
    provider = st.selectbox("LLM Provider", options=["OpenAI", "Anthropic Claude"], index=0)
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
    st.header("🖥️ VM Desktop (VNC)")
    
    with st.expander("VNC Settings"):
        vnc_host = st.text_input("VNC Host", value="localhost")
        vnc_port = st.number_input("VNC Port", value=5901)
        vnc_password = st.text_input("VNC Password", type="password")
        
        if st.button("Connect VNC"):
            html(noVNC_viewer(vnc_host, vnc_port, vnc_password), height=650)

# CSS styling
st.markdown("""
<style>
.st-emotion-cache-1y4p8pa {
    padding: 1.5rem;
}
.stChatFloatingInputContainer {
    bottom: 20px;
}
</style>
""", unsafe_allow_html=True)
