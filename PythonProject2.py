import streamlit as st
import fitz  # PyMuPDF
import re
from langchain_ollama import ChatOllama

# Initialize LLM with a lower temperature for factual extraction
llm = ChatOllama(
    model="llama3.2",
    temperature=0
)

def extract_abbreviation_context(full_text):
    """
    Optimized extraction function. 
    1. Finds patterns like (WDC), (SH), (IPC4).
    2. Grabs 100 characters BEFORE and AFTER the match to catch definitions.
    """
    pattern = re.compile(r"\(([A-Z]{2,}[A-Za-z0-9]*)\)")
    
    relevant_chunks = []
    
    # Iterate through all matches in the text
    for match in pattern.finditer(full_text):
        start, end = match.span()
        
        # Expand window: 100 chars before and 100 chars after
        context_start = max(0, start - 100)
        context_end = min(len(full_text), end + 100)
        
        # Clean up newlines so the context flows better for the LLM
        chunk = full_text[context_start:context_end].replace('\n', ' ')
        relevant_chunks.append(chunk)
            
    # Join chunks with a separator
    return " ... ".join(relevant_chunks)

st.title("Python Project 2: Abbreviation Indexer")
st.header("MSIS 5193")
st.subheader("Team")
st.text("""
-Chinmay Deshpande
-Dheeursa Tiwari
-Kazi Armaan Ahmed
-Siddharth Birajdar
""")

# Store full_text in session state so it's accessible for the Q&A section
if 'full_text' not in st.session_state:
    st.session_state.full_text = ""

# --- FILE UPLOAD SECTION ---
with st.form(key='file_upload_form'):
    file = st.file_uploader("Upload Article (PDF)", type=['pdf'], key=2)
    submit_button = st.form_submit_button(label='Generate Abbreviation Index')

if submit_button and file is not None:
    st.success(f"File '{file.name}' submitted successfully!")
    
    # 1. Read PDF Content
    pdf_data = file.read()
    with fitz.open(stream=pdf_data, filetype=file.type) as doc:
        text_content = ""
        for page in doc:
            text_content += page.get_text()
    
    # Save to session state for the Q&A section
    st.session_state.full_text = text_content

    # 2. Optimization: Filter Text using Regex
    with st.spinner('Scanning document for abbreviations...'):
        filtered_context = extract_abbreviation_context(text_content)
        
        # Fallback: If no abbreviations found, use the first 2000 chars
        if len(filtered_context) < 10:
            filtered_context = text_content[:2000]

    st.info(f"Optimization: Processing {len(filtered_context)} characters (filtered down from {len(text_content)}).")

    # 3. Define Prompt with Strict Formatting Rules
    # --- CHANGE: Added bullet point instruction to force vertical list format ---
    prompt = """
    You are a technical editor. Read the context text below. 
    Identify technical abbreviations and their full definitions found IN THE TEXT.
    
    Rules:
    1. Format the output as a Markdown bulleted list.
    2. Example format:
       * **WDC**: Weighted Degree Centrality
       * **SH**: Structural Holes
    3. If the text does not define the abbreviation (e.g. it is just a tool name like MPNet with no description), DO NOT include it.
    4. Ignore citations like (Author, Year) or figures like (Fig. 1).
    5. Do not leave any definition blank.
    
    Context:
    """
    
    # 4. Invoke LLM
    with st.spinner('Generating Index...'):
        ai_msg = llm.invoke(prompt + filtered_context)
    
    st.header("Abbreviation Index")
    
    # Using markdown ensures the bullet points render correctly
    st.markdown(ai_msg.content)

elif submit_button and file is None:
    st.warning("Please upload a file before submitting.")

# --- Q&A SECTION ---
st.markdown("---")
st.header("Ask a Question about the Document")
question = st.text_input("Input your Question:")

if question:
    if st.session_state.full_text:
        st.header("AI Response")
        context_to_send = st.session_state.full_text[:10000] 
        
        with st.spinner('Thinking...'):
            ai_msg = llm.invoke(f"Context: {context_to_send}\n\nQuestion: {question}")
        st.write(ai_msg.content)
    else:
        st.error("Please upload and submit a document first.")
