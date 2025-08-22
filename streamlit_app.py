import streamlit as st
from litellm import completion
from streamlit.components.v1 import html
import json

CHAT_CSS = """
<style>
/* Fixed chat container */
.chat-container {
    height: 65vh;
    overflow-y: auto;
    padding: 15px;
    background: #111827;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 10px;
}

/* Message bubbles */
.stChatMessage {
    padding: 8px 12px;
    margin: 8px 0;
    border-radius: 12px;
    max-width: 80%;
}
[data-testid="chatUserMessage"] {
    background: #1e40af;
    margin-left: auto;
}
[data-testid="chatAssistantMessage"] {
    background: #374151;
}

/* Input area */
.stTextInput>div>div>input {
    color: white !important;
}

/* Remove extra padding */
.st-emotion-cache-1y4p8pa {
    padding: 1rem;
}
</style>
"""


def noVNC_viewer():
    return """
    <div style="width:100%; height:600px; border:1px solid #ccc; border-radius:8px;">
        <iframe src="http://64.23.239.222:6080/vnc.html?autoconnect=true&resize=scale"
                style="width:100%; height:100%; border:none;"
                allowfullscreen>
        </iframe>
    </div>
    """


st.set_page_config(page_title="💬 Enki Chatbot", layout="wide")
st.title("Enki Workshop")
st.markdown(CHAT_CSS, unsafe_allow_html=True)  # Add this line

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
    
    # Chat container div
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
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

st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.header("🖥️ VM Desktop (VNC)")
    
    with st.expander("VNC Settings"):
        vnc_host = st.text_input("VNC Host", value="64.23.187.223")  # Your DO IP
        vnc_port = st.number_input("VNC Port", value=6080)  # WebSocket port
        vnc_password = st.text_input("VNC Password", type="password")
        
        if st.button("Connect VNC"):
            html(noVNC_viewer(), height=650)  # REMOVED THE PARAMETERS

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
