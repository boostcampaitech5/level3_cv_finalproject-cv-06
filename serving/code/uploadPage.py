import streamlit as st

def next_callback():
    # 이미지 업로드 확인
    if "src" not in st.session_state:
        st.warning('이미지를 업로드 해주세요.', icon="⚠️")
    else:
        st.session_state.page = "result_page"


def prev_callback():
    if "src" in st.session_state:
        del st.session_state["src"]
    st.session_state.page = "home_page"

def show_uploadPage():
    st.divider()

    # side bar
    with st.sidebar:
        st.markdown("""
            <center>
            👔스타일 선택

            ↓

            <span style="font-family: 'Arial'; font-size: 18px; font-weight: bold; color: #ff0000;">📂 사진 업로드</span>

            ↓

            🎉 결과 확인
            </center>
        """, unsafe_allow_html=True)
    
    description_col, image_col = st.columns(2)
    
    # 설명 및 성별 설정
    description_col.write("* 이미지 업로드 주의 사항 및 설명")
    description_col.divider()
    st.session_state.gender = description_col.radio("성별을 선택해주세요.", ("남성", "여성"), horizontal=True)

    # 이미지 업로드
    img = image_col.file_uploader("upload your image", type=["jpg", "jpeg", "png"])
    if img:
        st.session_state.src = img
        image_col.image(img)
    elif "src" in st.session_state:
        del st.session_state["src"]

    # 버튼
    next = st.button("다음 단계", on_click=next_callback, use_container_width=True)
    prev = st.button("스타일 다시 선택하기", on_click=prev_callback, use_container_width=True)

    