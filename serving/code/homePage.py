import streamlit as st
from PIL import Image

def button_callback(key):
    if key == "profile":
        st.session_state.domain = "profile"
    elif key == "id":
        st.session_state.domain = "id"
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
    description.write("AI 사진관은 사용자와 아주 유사한 증명사진을 언제 어디서든 생성할 수 있는 서비스입니다.")
    description.write("생성하고 싶은 사진의 스타일을 선택하여 시작해보세요.")

    st.divider()

    # 도메인 선택
    domain1, domain2 = st.columns(2)

    domain1.markdown("""<center>
        <h3>프로필</h3>
        </center>""", unsafe_allow_html=True)
    domain1_img = Image.open("/opt/ml/input/serving/data/example/profile.jpg")
    domain1.image(domain1_img, use_column_width=True)
    domain1.button("프로필 만들기", key="profile", on_click=button_callback, kwargs={"key":"profile"}, use_container_width=True)
    
    domain2.markdown("""<center>
        <h3>증명 사진</h3>
        </center>""", unsafe_allow_html=True)
    domain2_img = Image.open("/opt/ml/input/serving/data/example/id.jpg")
    domain2.image(domain2_img, use_column_width=True)
    domain2.button("증명 사진 만들기", key="id", on_click=button_callback, kwargs={"key":"id"}, use_container_width=True)