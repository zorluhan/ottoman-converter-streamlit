import os
import tempfile
import streamlit as st
from converter import convert

st.set_page_config(page_title="Ottoman Converter (Chat)", page_icon="🕌", layout="centered")
st.title("Ottoman Letter Converter — Chat")
st.caption("Type Turkish text; the assistant returns Ottoman Arabic script using Gemini 2.5 Pro.")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    # API key from secrets by default; user can override for this session
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    api_key = st.text_input("Google Gemini API Key", value=api_key, type="password", help="Stored only in this session")
    model = st.selectbox("Model", ["gemini-2.5-pro"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05)
    normalize = st.checkbox("Normalize Unicode (NFKC)", value=True)
    force_ng_final = st.checkbox("Force NG final glyph (ﯓ) when input ends with n/ng", value=False)

    kb_file = st.file_uploader("Knowledgebase document (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"], help="Used as reference each turn")
    clear_btn = st.button("Clear chat", use_container_width=True)

# Knowledgebase path handling
kb_path = None
if kb_file is not None:
    suffix = os.path.splitext(kb_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(kb_file.getbuffer())
        kb_path = tmp.name
else:
    default_pdf = os.path.join(os.path.dirname(__file__), "ottoman.pdf")
    if os.path.exists(default_pdf):
        kb_path = default_pdf
        st.info(f"Using default knowledgebase: {default_pdf}")

# Initialize chat history
if "messages" not in st.session_state or clear_btn:
    st.session_state.messages = []

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Türkçe metni yazın…")
if prompt:
    # Validate API key
    if not api_key:
        st.error("Please provide your Google Gemini API Key (or set it in Streamlit secrets).")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant reply
        with st.chat_message("assistant"):
            with st.spinner("Converting…"):
                output = convert(
                    text=prompt,
                    kb_path=kb_path,
                    api_key=api_key,
                    model_name=model,
                    temperature=temperature,
                    normalize=normalize,
                    force_ng_final=force_ng_final,
                )
            st.markdown(f"```
{output}
```")
        # Save assistant reply
        st.session_state.messages.append({"role": "assistant", "content": output})
