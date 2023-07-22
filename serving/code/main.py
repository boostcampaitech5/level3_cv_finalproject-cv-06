import streamlit as st
from homePage import show_homePage
from uploadPage import show_uploadPage
from resultPage import show_resultPage

def main():
    st.title("CV06 - 최종 프로젝트")
    
    # entrypoint file
    if 'page' not in st.session_state:
        st.session_state.page = 'home_page'

    if st.session_state.page == 'home_page':
        show_homePage()
    elif st.session_state.page == 'upload_page':
        show_uploadPage()
    elif st.session_state.page == 'result_page':
        show_resultPage()

if __name__ == "__main__":
    main()
