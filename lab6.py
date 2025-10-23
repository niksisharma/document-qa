import streamlit as st
from openai import OpenAI
import json

# Show title and description
st.title("📄 Nikita's AI Fact-Checker + Citation Builder Lab 6")

openai_api_key = st.secrets["OPENAI_API_KEY"]

openAI_model = st.sidebar.selectbox("Which Model?", ("mini", "regular"))
model = "gpt-4o" if openAI_model == "regular" else "gpt-4o-mini"

if 'client' not in st.session_state:
    st.session_state.client = OpenAI(api_key=openai_api_key)

if "claim_history" not in st.session_state:
    st.session_state.claim_history = []

# Fact-checking function
def fact_check_claim(claim):
    client = st.session_state.client
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are a fact-checker. Verify claims using available information and provide results in this exact JSON format:
{
  "claim": "the original claim",
  "verdict": "True/False/Partially True/Unclear",
  "explanation": "brief explanation with evidence",
  "sources": ["source1", "source2"]
}"""
            },
            {
                "role": "user",
                "content": f"Fact-check this claim: {claim}"
            }
        ],
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content
    result = json.loads(result_text)
    
    return result

# User input
user_claim = st.text_input("Enter a factual claim:", placeholder="e.g., Is dark chocolate healthy?")

# Check fact button
if st.button("Check Fact"):
    if user_claim:
        with st.spinner("Verifying claim..."):
            result = fact_check_claim(user_claim)
            
            # Display result
            st.json(result)
            
            # Add to history
            st.session_state.claim_history.append({
                "claim": user_claim,
                "result": result
            })
    else:
        st.warning("Please enter a claim to check.")

# Show history
if st.session_state.claim_history:
    st.subheader("Recent Checks")
    for i, item in enumerate(reversed(st.session_state.claim_history[-5:])):
        with st.expander(f"{i+1}. {item['claim'][:50]}..."):
            st.json(item['result'])