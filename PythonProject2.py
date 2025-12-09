

import streamlit as st
import pandas as pd
import fitz
from langchain_ollama import ChatOllama
llm = ChatOllama(
model = "llama3.2",
# other params ...
)

st.title("Python Project 2")
st.header("MSIS 5193")
st.header("AI context QnA Web development with Streamlit")
st.subheader("Team")
st.text("""
-Chinmay Deshpande
-Dheeursa Tiwari
-Kazi Armaan Ahmed
-Siddharth Birajdar
""")


st.write(st.secrets.openai.my_api_key)
# form variables create earlier
with st.form(key='file_upload_form'):

    file = st.file_uploader("Upload a Context file", key =2)

    # Submit button inside the form
    submit_button = st.form_submit_button(label='Submit File')
  

# Action to take after the form is submitted
if submit_button:
    if file is not None:
        # Process the uploaded file here
        st.success(f"File '{file.name}' submitted successfully!")
        # Example of reading the file content
        file_details = {"FileName": file.name, "FileType": file.type}
    else:
        st.warning("Please upload a file before submitting.")
    
    pdf_data = file.read()
        
    # Optional: If you need to read the file multiple times or seek to beginning
    # uploaded_pdf.seek(0)
    
    # Open the document using fitz with the byte stream
    with fitz.open(stream=pdf_data, filetype=file.type) as doc:
        context = ""
        for page in doc:
            context += page.get_text()
    prompt = "Analyse the whole, not partial, document and provide One Line summary of what the document is"
    ai_msg = llm.invoke(context + " Prompt: " +prompt)
    st.write(ai_msg.content)

st.header("Input your question")
question = st.text_input("Input your Question:")

# Action to take after the form is submitted
if submit_button:

    st.header("AI Response")
    ai_msg = llm.invoke("Given the context:" +context + " Prompt: " +question)
    st.write(ai_msg.content)
    
elif question:

    st.header("AI Response")
    ai_msg = llm.invoke(" Prompt: " +question)
    st.write(ai_msg.content)












