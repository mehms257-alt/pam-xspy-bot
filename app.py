import streamlit as st
from google import genai
from google.genai import types

# Page Layout
st.set_page_config(page_title="PAM & XSPY Assistant", page_icon="📈", layout="centered")
st.title("📈 PAM & XSPY Knowledge Assistant")
st.caption("Ask questions strictly based on PAM strategies & XSPY Lessons.")

# 1. Secure API Key handling
# Reads from Streamlit Cloud Secrets (or sidebar if testing locally)
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if not api_key:
        st.info("Please enter your Gemini API Key in the sidebar to start.", icon="🗝️")
        st.stop()

client = genai.Client(api_key=api_key)

# 2. Sidebar File Uploader (to attach PAM & XSPY documents)
st.sidebar.header("Document Context")
uploaded_files = st.sidebar.file_uploader(
    "Upload PAM/XSPY Notes (PDF, TXT, DOCX)", 
    type=["pdf", "txt", "docx"], 
    accept_multiple_files=True
)

# 3. Strict System Prompt
SYSTEM_INSTRUCTION = (
    "You are a helpful knowledge assistant on PAM strategies & XSPY Lessons. "
    "You must answer questions ONLY using the information provided in the attached documents. "
    "If the answer cannot be found in the documents, state clearly: "
    "'I cannot find that information in the provided sources.' "
    "Do not guess or use outside knowledge."
)

# 4. Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. User Input
if prompt := st.chat_input("Ask a question about PAM or XSPY..."):
    # Display user query
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare data payload for Gemini
    payload = []
    
    # Upload and attach reference files if present
    if uploaded_files:
        for f in uploaded_files:
            gemini_file = client.files.upload(file=f)
            payload.append(gemini_file)
            
    payload.append(prompt)

    # Generate strictly grounded response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=payload,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        max_output_tokens=4096,
                    )
                )
                answer = response.text
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")