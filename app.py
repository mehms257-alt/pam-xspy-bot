import streamlit as st
import tempfile
import os
from google import genai

st.title("PAM & XSPY Assistant")

# Initialize Gemini Client (using Streamlit secrets)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# File uploader in the sidebar
uploaded_files = st.sidebar.file_uploader(
    "Upload PAM/XSPY Notes", 
    type=["pdf", "txt", "docx"], 
    accept_multiple_files=True
)

# Process files and hold them in a list/payload if needed
payload = []
if uploaded_files:
    for f in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
            tmp.write(f.getvalue())
            tmp_path = tmp.name
        
        gemini_file = client.files.upload(file=tmp_path)
        payload.append(gemini_file)
        os.unlink(tmp_path)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages when app reruns
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create the chat input box at the bottom of the page
if prompt := st.chat_input("Ask a question about your PAM/XSPY notes..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response from Gemini (including uploaded files if available)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Combine uploaded files + user prompt content
                contents = payload + [prompt] if payload else [prompt]
                
                response = client.models.generate_content(
                    model="gemini-3.8-flash",  # or gemini-2.5-pro
                    contents=contents
                )
                answer = response.text
            except Exception as e:
                answer = f"Error generating response: {e}"
            
            st.markdown(answer)
            
    st.session_state.messages.append({"role": "assistant", "content": answer})
