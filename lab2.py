import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 Nikita's Document Summarizer Lab 2")

openai_api_key = st.secrets["DB_TOKEN"]

summary_type = st.selectbox(
        "Select Summary Type",
        ["100 Words", "2 Paragraphs", "5 Bullet Points"]
    )

# Checkbox to select advanced model
use_advanced_model = st.checkbox("Use Advanced Model (GPT-4)")

# Default model selection
model = "gpt-4" if use_advanced_model else "gpt-4.1-nano"

    
key_valid = False
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
        client.models.list()  
        st.success("API key is valid ✅")
        key_valid = True
    except Exception as e:
        st.error(f"Invalid API key. {e}")
else:
    st.info("No OpenAI API key", icon="🗝️")

st.write("Upload your document and select summary type.")

uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

if uploaded_file:
        document = uploaded_file.read().decode(errors="ignore")
        st.write("Document Content:")
        st.text_area("Document Content", document, height=200)

    # Show the summary options and get the LLM key from secrets
openai_api_key = st.secrets["DB_TOKEN"]

if key_valid and uploaded_file and document:
        if summary_type == "100 Words":
            prompt = f"Summarize the document in 100 words: {document}"
        elif summary_type == "2 Paragraphs":
            prompt = f"Summarize the document in 2 paragraphs: {document}"
        else:
            prompt = f"Summarize the document in 5 bullet points: {document}"

        messages = [{"role": "user", "content": prompt}]
        
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            st.write_stream(stream)
        except Exception as e:
            st.error(f"Error: {e}")

   