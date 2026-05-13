import streamlit as st

st.title("Debate Me")

topic = st.text_input("Debate topic")
person_a = st.text_area("Person A's argument")
person_b = st.text_area("Person B's argument")

if st.button("Judge Debate"):
    st.write("AI judging will go here.")
    st.write("Topic:", topic)
    st.write("Person A:", person_a)
    st.write("Person B:", person_b)