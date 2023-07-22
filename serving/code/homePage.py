import streamlit as st
from PIL import Image

def button_callback(key):
    if key == "id":
        st.session_state.domain = "id"
    elif key == "pro":
        st.session_state.domain = "pro"
    st.session_state.page = "upload_page"

def show_homePage():

    # side bar
    with st.sidebar:
        st.markdown("""
            <center>
            <span style="font-family: 'Arial'; font-size: 18px; font-weight: bold; color: #ff0000;">👔스타일 선택</span>

            ↓

            📂 사진 업로드

            ↓

            🎉 결과 확인
            </center>
        """, unsafe_allow_html=True)

    # project 설명
    description = st.container()
    description.write("프로젝트 설명...")

    st.divider()

    # 도메인 선택
    domain1, domain2 = st.columns(2)

    domain1.markdown("""<center>
        <h3>증명 사진</h3>
        증명 사진 설명...
        </center>""", unsafe_allow_html=True)
    domain1_img = Image.open("serving/data/id_f_1.jpg")
    domain1.image(domain1_img)
    domain1.button("증명 사진 만들기", key="id", on_click=button_callback, kwargs={"key":"id"}, use_container_width=True)
    
    domain2.markdown("""<center>
        <h3>취업 사진</h3>
        취업 사진 설명...
        </center>""", unsafe_allow_html=True)
    domain2_img = Image.open("serving/data/pro_f_1.jpg")
    domain2.image(domain2_img)
    domain2.button("취업 사진 만들기", key="pro", on_click=button_callback, kwargs={"key":"pro"}, use_container_width=True)