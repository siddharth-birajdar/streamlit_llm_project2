import streamlit as st
import pandas as pd
import fitz
from openai import OpenAI

# Load API key from Streamlit secrets
api_key = st.secrets.openaiDetails.my_api_key

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

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

st.write("API Key Loaded Successfully.")

# Form for PDF upload
with st.form(key='file_upload_form'):

    file = st.file_uploader("Upload a Context file", key=2)

    submit_button = st.form_submit_button(label='Submit File')

# Context variable for later use
context = ""

if submit_button:
    if file is not None:

        st.success(f"File '{file.name}' submitted successfully!")

        pdf_data = file.read()

        # Extract text using PyMuPDF
        with fitz.open(stream=pdf_data, filetype=file.type) as doc:
            for page in doc:
                context += page.get_text()

        # AI summary request
        prompt = (
            "Analyze the whole document and provide ONE LINE summarizing what the document is about."
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze documents."},
                {"role": "user", "content": context + "\n\nPrompt: " + prompt}
            ]
        )

        st.write(completion.choices[0].message["content"])

    else:
        st.warning("Please upload a file before submitting.")


# User Question Section
st.header("Input your question")
question = st.text_input("Input your Question:")

if submit_button and question:
    st.header("AI Response")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer questions based on context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    )

    st.write(completion.choices[0].message["content"])

elif question:
    st.header("AI Response")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": question}
        ]
    )

    st.write(completion.choices[0].message["content"])

 
