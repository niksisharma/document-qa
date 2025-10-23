import streamlit as st

lab1_page = st.Page("lab1.py", title="Lab 1", icon="🖥️")
lab2_page = st.Page("lab2.py", title="Lab 2", icon="🖥️")
lab3_page = st.Page("lab3.py", title="Lab 3", icon="🖥️")
lab4_page = st.Page("lab4.py", title="Lab 4", icon="🖥️")
lab5_page = st.Page("lab5.py", title="Lab 5", icon="🖥️")
lab6_page = st.Page("lab6.py", title="Lab 6", icon="🖥️", default=True)

pg = st.navigation([lab1_page, lab2_page, lab3_page, lab4_page, lab5_page, lab6_page])
st.set_page_config(page_title="Nikita's Labs", page_icon="📄")
pg.run()