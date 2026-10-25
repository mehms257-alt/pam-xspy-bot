import tempfile
import os

# Upload and attach reference files if present
if uploaded_files:
  for f in uploaded_files:
    # Save uploaded file temporarily so the SDK can read its extension/mimetype
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
      tmp.write(f.getvalue())
      tmp_path = tmp.name
    
    # Upload using the local file path
    gemini_file = client.files.upload(file=tmp_path)
    payload.append(gemini_file)
    
    # Clean up the temporary file
    os.unlink(tmp_path)
