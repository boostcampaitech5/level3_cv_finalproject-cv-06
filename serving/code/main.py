import streamlit as st
from PIL import Image

def up_callback():
    st.session_state.num += 1

if 'num' not in st.session_state:
    st.session_state.num = 0

st.text("hello, world!")

button = st.button('up', on_click=up_callback)
st.write(st.session_state.num)

img = Image.open("serving/data/id_f_1.jpg")

st.image(img)