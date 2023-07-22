import streamlit as st
from PIL import Image
import io

def image_to_bytes(image):
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format = "JPEG")
    return img_byte_array.getvalue()

def get_reference_images(domain, gender, src):
    
    # todo : Arcface로 src와 유사한 이미지 3개 리턴
    references = []

    # test
    references.append(Image.open("serving/data/pro_m_1.jpg"))
    references.append(Image.open("serving/data/pro_m_2.jpg"))
    references.append(Image.open("serving/data/pro_m_3.jpg"))

    return references

def get_result_images(src, refs):
    
    # todo : simswap inference

    results = []

    # test
    results.append(Image.open("serving/data/pro_m_1.jpg"))
    results.append(Image.open("serving/data/pro_m_2.jpg"))
    results.append(Image.open("serving/data/pro_m_3.jpg"))

    return results

def reupload_callback():
    del st.session_state["src"]
    st.session_state.page = "upload_page"

def home_callback():
    del st.session_state["src"]
    st.session_state.page = "home_page"

def show_resultPage():

    # side bar
    with st.sidebar:
        st.markdown("""
            <center>
            👔스타일 선택

            ↓

            📂 사진 업로드

            ↓

            <span style="font-family: 'Arial'; font-size: 18px; font-weight: bold; color: #ff0000;">🎉 결과 확인</span>
            </center>
        """, unsafe_allow_html=True)

    # 설명
    description = st.container()
    description.write("result 관련 설명...")
    
    st.divider()

    # reference 이미지
    refs = get_reference_images(st.session_state.domain, st.session_state.gender, st.session_state.src)

    # result 이미지
    results = get_result_images(st.session_state.src, refs)

    cols = st.columns(3)
    for i in range(3):
        col = cols[i]
        
        # image
        col.image(results[i])

        # download button
        img_byte = image_to_bytes(results[i])
        col.download_button("다운로드", data=img_byte, file_name=f"{st.session_state.domain}_{st.session_state.gender}_{i}.jpg", use_container_width=True)

    # button
    buttons = st.container()
    reupload_button = buttons.button("이미지 다시 업로드하기", use_container_width=True, on_click=reupload_callback)
    home_button = buttons.button("처음으로 돌아가기", use_container_width=True, on_click=home_callback)




