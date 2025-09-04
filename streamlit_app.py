import streamlit as st

lab1_page = st.Page("lab1.py", title="Lab 1")
lab2_page = st.Page("lab2.py", title="Lab 2",  default=True)

pg = st.navigation([lab1_page, lab2_page])
st.set_page_config(page_title="Labs", page_icon=":material/edit:")
pg.run()