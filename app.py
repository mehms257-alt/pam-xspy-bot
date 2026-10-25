import streamlit as st
import os
import time
from google import genai
from google.genai import types

st.title("PAM & XSPY Assistant")

# Initialize Gemini Client (using Streamlit secrets)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Automatically load all notes from the 'notes/' folder on startup
@st.cache_resource
def load_notes_payload():
    payload = []
    notes_dir = "notes"
    if os.path.exists(notes_dir):
        for filename in os.listdir(notes_dir):
            file_path = os.path.join(notes_dir, filename)
            if os.path.isfile(file_path):
                # Upload each file to Gemini's File API automatically
                gemini_file = client.files.upload(file=file_path)
                payload.append(gemini_file)
    return payload

payload = load_notes_payload()

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

    # Generate response from Gemini with strict document grounding and retry logic
    with st.chat_message("assistant"):
        with st.spinner("Thinking using your notes..."):
            answer = ""
            max_retries = 3
            retry_delay = 2
            contents = payload + [prompt] if payload else [prompt]
            
            # Strict system instruction to prevent outside knowledge
            strict_system_instruction = (
                "You are a strict, secure document-grounded assistant for PAM and XSPY notes. "
                "You must ONLY answer questions using the exact information contained in the uploaded files/documents. "
                "If no files are uploaded, or if the answer cannot be found inside the uploaded documents, "
                "you must reply with: 'I cannot find this information in your uploaded PAM/XSPY notes.' "
                "Never use general knowledge, internet assumptions, or outside information."
            )

            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=strict_system_instruction,
                            temperature=0.1,  # Low temperature keeps responses factual and strict to text
                        )
                    )
                    answer = response.text
                    break
                except Exception as e:
                    error_msg = str(e)
                    if "503" in error_msg or "UNAVAILABLE" in error_msg:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                    answer = f"Error generating response: {e}"
                    break

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
