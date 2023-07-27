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
    if "gender" in st.session_state:
        del st.session_state["gender"]
    if "bangs" in st.session_state:
        del st.session_state["bangs"]
    if "hair" in st.session_state:
        del st.session_state["hair"]

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
    description_col.markdown("#### 이미지 업로드 주의 사항")
    description_col.write("* 정면을 바라보는 사진을 업로드 해주세요.")
    description_col.write("* 성별 및 원하는 스타일 선택 사항을 선택해 주세요.")

    # 이미지 업로드
    img = image_col.file_uploader("upload your image", type=["jpg", "jpeg", "png"])
    if img:
        st.session_state.src = img
        image_col.image(img)
    elif "src" in st.session_state:
        del st.session_state["src"]

    st.divider()

    style = st.container()
    style.markdown("#### 스타일 선택 사항")
    st.session_state.gender = style.radio("성별", ("남성", "여성"), horizontal=True)

    if st.session_state.domain == "id":
        if st.session_state.gender == "남성":
            st.session_state.bangs = style.radio("앞머리 유무", ("O", "X"), horizontal=True)
        else:
            st.session_state.bangs = style.radio("앞머리 유무", ("O", "X"), horizontal=True)
            if st.session_state.bangs == "X":
                st.session_state.hair = style.radio("머리 스타일", ("장발", "단발", "묶은 머리"), horizontal=True)
            else:
                st.session_state.hair = style.radio("머리 스타일", ("장발", "단발"), horizontal=True)

    st.divider()
    # 버튼
    next = st.button("다음 단계", on_click=next_callback, use_container_width=True)
    prev = st.button("처음으로", on_click=prev_callback, use_container_width=True)

    