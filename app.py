import streamlit as st
import tempfile
import os

st.title("PAM & XSPY Assistant")

# 1. Define the file uploader widget first so the variable exists
uploaded_files = st.sidebar.file_uploader(
    "Upload PAM/XSPY Notes", 
    type=["pdf", "txt", "docx"], 
    accept_multiple_files=True
)

# 2. Now you can safely check if uploaded_files has any files
if uploaded_files:
    for f in uploaded_files:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
            tmp.write(f.getvalue())
            tmp_path = tmp.name
        
        # Process or upload your files here...
        os.unlink(tmp_path)
