import streamlit as st
import fitz  # PyMuPDF
import re
from openai import OpenAI

# Load your Gemini API key (e.g. via Streamlit secrets)
api_key = st.secrets.gemini.my_api_key  # adjust to your config

# Initialize Gemini client via OpenAI‑compatible interface
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- HELPER: same regex extraction as before ---
def extract_abbreviation_context(full_text):
    pattern = re.compile(r"\(([A-Z]{2,}[A-Za-z0-9]*)\)")
    relevant_chunks = []
    for match in pattern.finditer(full_text):
        start, end = match.span()
        context_start = max(0, start - 100)
        context_end = min(len(full_text), end + 100)
        chunk = full_text[context_start:context_end].replace('\n', ' ')
        relevant_chunks.append(chunk)
    return " ... ".join(relevant_chunks)


st.title("Python Project 2: Web‑Based LLM App (using Gemini)")
st.header("MSIS 5193")
st.subheader("Team")
st.text("""
- Chinmay Deshpande
- Dheerusha Tiwari
- Kazi Armaan Ahmed
- Siddharth Birajdar
""")

if 'full_text' not in st.session_state:
    st.session_state.full_text = ""

### Section 1: Upload & store context ###
uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="main_uploader")
if st.button("Submit File for Context"):
    if uploaded_file is not None:
        with st.spinner('Reading file...'):
            pdf_data = uploaded_file.read()
            with fitz.open(stream=pdf_data, filetype=uploaded_file.type) as doc:
                text_content = "".join(page.get_text() for page in doc)
        st.session_state.full_text = text_content
        st.success(f"File '{uploaded_file.name}' loaded successfully! You can now use tools below.")
    else:
        st.warning("Please select a file first.")

### Section 2: Abbreviation Index (optional) ###
if st.button("Generate Abbreviation Index"):
    if st.session_state.full_text:
        filtered_context = extract_abbreviation_context(st.session_state.full_text)
        if len(filtered_context) < 10:
            filtered_context = st.session_state.full_text[:2000]
        st.info(f"Processing {len(filtered_context)} characters for abbreviation detection.")
        prompt = """
You are a technical editor. Read the context text below. 
Identify technical abbreviations and their full definitions found IN THE TEXT.

Rules:
1. Format output as a Markdown bulleted list.
2. Example:
   * **WDC**: Weighted Degree Centrality
3. If the text does not define the abbreviation, do NOT include it.
4. Ignore citations like (Author, Year).

Context:
""" + filtered_context

        with st.spinner('Generating index...'):
            completion = client.chat.completions.create(
                model="gemini-2.5-flash",   # or another Gemini model of your choice
                messages=[
                    {"role": "system", "content": "You are a technical editor that extracts abbreviations."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_msg = completion.choices[0].message.content

        st.header("Abbreviation Index")
        st.markdown(ai_msg)
    else:
        st.error("No document context found. Please upload and submit first.")

### Section 3: Q&A ###
st.markdown("---")
st.header("Ask a Question about the Document")
question = st.text_input("Input your Question:")

if question:
    if st.session_state.full_text:
        context_to_send = st.session_state.full_text[:10000]
        with st.spinner('Thinking...'):
            completion = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "You answer questions based on document context."},
                    {"role": "user", "content": f"Context: {context_to_send}\n\nQuestion: {question}"}
                ]
            )
            ai_msg = completion.choices[0].message.content
        st.markdown("#### AI Response")
        st.write(ai_msg)
    else:
        st.error("Please submit a document first.")
