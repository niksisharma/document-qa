import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 Nikita's ChatBot Lab 3")

openai_api_key = st.secrets["DB_TOKEN"]

openAI_model = st.sidebar.selectbox("Which Model?",("mini","regular"))
model = "gpt-4o" if openAI_model == "regular" else "gpt-4o-mini"

    
if 'client' not in st.session_state:
    st.session_state.client = OpenAI(api_key=openai_api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What is up?"):
    if prompt == "no":
        st.session_state.messages.append({"role": "user", "content": "ask me WHAT ELSE CAN I HELP YOU WITH?"})
    else: 
        st.session_state.messages.append({"role": "user", "content": prompt+"After answering ask me DO YOU WANT MORE INFO?"})

    with st.chat_message("user"):
        st.markdown(prompt)

    client = st.session_state.client
    stream = client.chat.completions.create(
        model = model,
        messages = st.session_state.messages,
        stream = True
    )

    response = "response"
    
    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # Keep initial message + last 2 conversation messages  
    if len(st.session_state.messages) > 3:  
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-2:]                                                                          