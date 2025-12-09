import streamlit as st
import fitz  # PyMuPDF
import re
from langchain_ollama import ChatOllama

# Initialize LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0
)

# --- HELPER FUNCTION: REGEX EXTRACTION ---
def extract_abbreviation_context(full_text):
    """
    Finds abbreviations like (WDC) and grabs surrounding context
    to help the AI define them accurately.
    """
    pattern = re.compile(r"\(([A-Z]{2,}[A-Za-z0-9]*)\)")
    relevant_chunks = []
    
    for match in pattern.finditer(full_text):
        start, end = match.span()
        # Grab 100 chars before and after
        context_start = max(0, start - 100)
        context_end = min(len(full_text), end + 100)
        chunk = full_text[context_start:context_end].replace('\n', ' ')
        relevant_chunks.append(chunk)
            
    return " ... ".join(relevant_chunks)

# --- APP LAYOUT ---
st.title("Python Project 2: Web-Based LLM App")
st.header("MSIS 5193")
st.subheader("Team")
st.text("""
-Chinmay Deshpande
-Dheerusha Tiwari
-Kazi Armaan Ahmed
-Siddharth Birajdar
""")

# Initialize session state to hold the document text
if 'full_text' not in st.session_state:
    st.session_state.full_text = ""

# --- SECTION 1: UPLOAD & SUBMIT CONTEXT ---
st.markdown("### 1. Upload Document")
uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="main_uploader")

# BUTTON 1: Submit File (Just loads context, does NOT generate index)
if st.button("Submit File for Context"):
    if uploaded_file is not None:
        with st.spinner('Reading file...'):
            # Read PDF
            pdf_data = uploaded_file.read()
            with fitz.open(stream=pdf_data, filetype=uploaded_file.type) as doc:
                text_content = ""
                for page in doc:
                    text_content += page.get_text()
            
            # Save to session state
            st.session_state.full_text = text_content
            st.success(f"File '{uploaded_file.name}' loaded successfully! You can now ask questions below.")
    else:
        st.warning("Please select a file first.")

# --- SECTION 2: GENERATE ABBREVIATIONS (OPTIONAL) ---
st.markdown("### 2. Tools")
# BUTTON 2: Generate Index (Separate action)
if st.button("Generate Abbreviation Index"):
    # Check if context exists in session state
    if st.session_state.full_text:
        
        with st.spinner('Scanning for abbreviations...'):
            # 1. Regex Optimization
            filtered_context = extract_abbreviation_context(st.session_state.full_text)
            
            # Fallback if no abbreviations found
            if len(filtered_context) < 10:
                filtered_context = st.session_state.full_text[:2000]

            st.info(f"Optimization: Extracted {len(filtered_context)} chars for processing.")

            # 2. AI Prompt
            prompt = """
            You are a technical editor. Read the context text below. 
            Identify technical abbreviations and their full definitions found IN THE TEXT.
            
            Rules:
            1. Format the output as a Markdown bulleted list.
            2. Example format:
               * **WDC**: Weighted Degree Centrality
            3. If the text does not define the abbreviation, DO NOT include it.
            4. Ignore citations like (Author, Year).
            
            Context:
            """
            
            # 3. Invoke LLM
            ai_msg = llm.invoke(prompt + filtered_context)
            
            st.markdown("#### Abbreviation Index")
            st.markdown(ai_msg.content)
            
    else:
        st.error("No document context found. Please upload and click 'Submit File for Context' first.")

# --- SECTION 3: Q&A ---
st.markdown("---")
st.markdown("### 3. Ask a Question")
question = st.text_input("Input your Question:")

if question:
    if st.session_state.full_text:
        # Use the stored text for Q&A
        context_to_send = st.session_state.full_text[:10000] # Limit to avoid context overflow
        
        with st.spinner('AI is thinking...'):
            ai_msg = llm.invoke(f"Context: {context_to_send}\n\nQuestion: {question}")
        
        st.markdown("#### AI Response")
        st.write(ai_msg.content)
    else:
        with st.spinner('AI is thinking...'):
            ai_msg = llm.invoke(f"Question: {question}")
        
        st.markdown("#### AI Response")
        st.write(ai_msg.content)
