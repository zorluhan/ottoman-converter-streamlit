import os
import tempfile
import streamlit as st
from converter import convert

st.set_page_config(page_title="Ottoman Converter", page_icon="🕌", layout="centered")
st.title("Ottoman Letter Converter")
st.caption("Convert modern Turkish text to Ottoman Arabic script using Gemini 2.5 Pro")

with st.sidebar:
    st.header("Settings")
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    api_key = st.text_input("Google Gemini API Key", value=api_key, type="password", help="Stored only in this session")
    model = st.selectbox("Model", ["gemini-2.5-pro"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05)
    normalize = st.checkbox("Normalize Unicode (NFKC)", value=True)
    force_ng_final = st.checkbox("Force NG final glyph (ﯓ) when input ends with n/ng", value=False)

    kb_file = st.file_uploader("Knowledgebase document (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])

# Auto-use ottoman.pdf from app directory if no upload
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

text = st.text_area("Input text", height=160, placeholder="Türkçe metni buraya yazın…")

col1, col2 = st.columns([1,1])
with col1:
    run_clicked = st.button("Convert", use_container_width=True)
with col2:
    clear_clicked = st.button("Clear", use_container_width=True)

if clear_clicked:
    st.experimental_rerun()

if run_clicked:
    if not api_key:
        st.error("Please provide your Google Gemini API Key (or set it in Streamlit secrets).")
    elif not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Converting…"):
            output = convert(
                text=text,
                kb_path=kb_path,
                api_key=api_key,
                model_name=model,
                temperature=temperature,
                normalize=normalize,
                force_ng_final=force_ng_final,
            )
        st.subheader("Output")
        st.code(output)
        st.caption("Tip: Use a font with Arabic Presentation Forms support (e.g., Noto Naskh Arabic, Scheherazade, Amiri) if some glyphs do not render.")
