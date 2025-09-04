import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 Nikita's Document QA Lab 2")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get "
    "[here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets["DB_TOKEN"]

key_valid = False
if not openai_api_key:
    st.info("No OpenAI API key", icon="🗝️")
else:
    try:
        # Immediate validation
        OpenAI(api_key=openai_api_key).models.list()
        st.success("API key is valid ✅")
        key_valid = True
    except Exception as e:
        st.error(f"Invalid API key. {e}")

uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md"), disabled=not key_valid
)

question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled=(not key_valid or not uploaded_file),
)

if key_valid and uploaded_file and question:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
    
    # Let the user upload a file via `st.file_uploader`.
    document = uploaded_file.read().decode(errors="ignore")
    messages = [
        {"role": "user", "content": f"Here's a document: {document}\n\n---\n\n{question}"}
    ]

    stream = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        stream=True,
    )
    st.write_stream(stream)
